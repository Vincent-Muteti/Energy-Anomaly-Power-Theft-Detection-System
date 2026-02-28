import json
import os
import shutil
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Electricity Anomaly Detection", layout="wide")

st.title("Electricity Anomaly Detection and Inspection Prioritization")
st.caption("Machine learning–driven anomaly detection for electricity inspection prioritization.")
st.info(
    "Disclaimer: This app flags statistical anomalies for inspection prioritization. "
    "It does not confirm electricity theft. Validate findings with field investigations."
)

DATA_MODE = st.sidebar.radio("Data mode", ["Use repo data", "Upload CSVs"])
st.sidebar.markdown("---")

POWER_PATH = "power_multi_household_daily.csv"
WEATHER_PATH = "nairobi_weather_2007_2008.csv"

ARTIFACT_DIR = "artifacts"
MODELS_PATH = f"{ARTIFACT_DIR}/models_by_meter.joblib"
SCALERS_PATH = f"{ARTIFACT_DIR}/scalers_by_meter.joblib"
META_PATH = f"{ARTIFACT_DIR}/metadata.json"

# Outputs directory (for cross-page sharing)
OUTPUT_DIR = "outputs"
SCORED_PATH = f"{OUTPUT_DIR}/scored_output.csv"
REPORT_PATH = f"{OUTPUT_DIR}/inspection_report.csv"
META_OUT_PATH = f"{OUTPUT_DIR}/run_metadata.json"


# --------------------
# Helper functions
# --------------------
def generate_alert(row: pd.Series) -> str:
    if row["risk_level"] in ["High", "Medium"]:
        last_date = row["last_anomaly_date"]
        last_date_str = last_date.date().isoformat() if pd.notna(last_date) else "N/A"
        return (
            f"ALERT: Meter {row['meter_id']} is {row['risk_level']} risk "
            f"(Risk Score: {row['risk_score']}). "
            f"Anomalous days: {int(row['total_anomalies'])}; "
            f"Max streak: {int(row['max_streak_days'])} days; "
            f"Last anomaly: {last_date_str}. "
            "Recommended for inspection review."
        )
    return "No immediate inspection required."


def compute_max_streak(df: pd.DataFrame, flag_col: str) -> pd.DataFrame:
    df = df.sort_values(["meter_id", "date"]).copy()
    df["prev_flag"] = df.groupby("meter_id")[flag_col].shift(1)
    df["start_streak"] = (df[flag_col].eq(1) & ~df["prev_flag"].eq(1))
    df["streak_group"] = df.groupby("meter_id")["start_streak"].cumsum()

    streak_lengths = (
        df[df[flag_col] == 1]
        .groupby(["meter_id", "streak_group"])
        .size()
        .reset_index(name="streak_len")
    )

    if streak_lengths.empty:
        return pd.DataFrame({"meter_id": df["meter_id"].unique(), "max_streak_days": 0})

    max_streak = streak_lengths.groupby("meter_id")["streak_len"].max().reset_index()
    max_streak.columns = ["meter_id", "max_streak_days"]
    return max_streak


@st.cache_data(show_spinner=False)
def load_artifacts():
    with open(META_PATH, "r") as f:
        meta = json.load(f)
    models_by_meter = joblib.load(MODELS_PATH)
    scalers_by_meter = joblib.load(SCALERS_PATH)
    return meta, models_by_meter, scalers_by_meter


def load_data(power_df: pd.DataFrame, weather_df: pd.DataFrame, start_date: str, end_date: str):
    power_df = power_df.copy()
    weather_df = weather_df.copy()

    power_df["date"] = pd.to_datetime(power_df["date"])
    weather_df["date"] = pd.to_datetime(weather_df["date"])

    df = power_df.merge(weather_df, on="date", how="left")
    df = df[(df["date"] >= start_date) & (df["date"] <= end_date)].copy()
    df = df.dropna().sort_values(["meter_id", "date"]).reset_index(drop=True)
    return df


def add_features(df: pd.DataFrame, rolling_window_days: int):
    w = int(rolling_window_days)
    df = df.sort_values(["meter_id", "date"]).copy()

    df["rolling_mean_30"] = df.groupby("meter_id")["daily_mean_power"].transform(
        lambda x: x.rolling(w, min_periods=1).mean()
    )
    df["rolling_std_30"] = df.groupby("meter_id")["daily_mean_power"].transform(
        lambda x: x.rolling(w, min_periods=1).std()
    )
    df["residual_30"] = df["daily_mean_power"] - df["rolling_mean_30"]
    df["z_score_30"] = df["residual_30"] / (df["rolling_std_30"] + 1e-6)
    return df


def score(df: pd.DataFrame, features: list[str], models_by_meter: dict, scalers_by_meter: dict):
    df = df.copy()
    df["anomaly_score"] = np.nan

    for meter_id, g in df.groupby("meter_id"):
        key = str(meter_id)
        if key not in models_by_meter:
            continue
        X = g[features].fillna(0)
        Xs = scalers_by_meter[key].transform(X)
        df.loc[g.index, "anomaly_score"] = models_by_meter[key].decision_function(Xs)

    return df


def make_report(df: pd.DataFrame, threshold: float):
    df = df.copy()
    df["anomaly_flag_global"] = (df["anomaly_score"] <= threshold).astype(int)

    max_streak = compute_max_streak(df, "anomaly_flag_global")

    report = df.groupby("meter_id").agg(
        total_anomalies=("anomaly_flag_global", "sum"),
        percent_anomalous=("anomaly_flag_global", "mean"),
        worst_anomaly_score=("anomaly_score", "min"),
        avg_anomaly_score=("anomaly_score", "mean"),
        last_anomaly_date=("date", lambda x: x[df.loc[x.index, "anomaly_flag_global"].eq(1)].max()),
    ).reset_index()

    report = report.merge(max_streak, on="meter_id", how="left")
    report["max_streak_days"] = report["max_streak_days"].fillna(0).astype(int)

    score_raw = -report["worst_anomaly_score"]
    smin, smax = score_raw.min(), score_raw.max()
    report["risk_score"] = 100 * (score_raw - smin) / (smax - smin + 1e-9)
    report["risk_score"] = (report["risk_score"] + report["max_streak_days"] * 5).clip(0, 100).round(1)

    report["risk_level"] = pd.cut(
        report["risk_score"],
        bins=[-1, 33, 66, 101],
        labels=["Low", "Medium", "High"],
    )

    report["alert_message"] = report.apply(generate_alert, axis=1)
    return report


def save_outputs(df: pd.DataFrame, report: pd.DataFrame, meta: dict):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(SCORED_PATH, index=False)
    report.to_csv(REPORT_PATH, index=False)

    run_meta = {
        "saved_at": datetime.utcnow().isoformat() + "Z",
        "start_date": meta["start_date"],
        "end_date": meta["end_date"],
        "rolling_window_days": int(meta["rolling_window_days"]),
        "global_threshold": float(meta["global_threshold"]),
        "features": meta["features"],
        "rows_scored": int(len(df)),
        "meters": int(report.shape[0]),
        "flagged_days": int(df["anomaly_flag_global"].sum()),
    }
    with open(META_OUT_PATH, "w") as f:
        json.dump(run_meta, f, indent=2)


# --------------------
# Charts
# --------------------
def plot_score_distribution(df: pd.DataFrame):
    fig, ax = plt.subplots()
    ax.hist(df["anomaly_score"].dropna(), bins=60)
    ax.set_title("Global Anomaly Score Distribution")
    ax.set_xlabel("Anomaly Score (lower = more suspicious)")
    ax.set_ylabel("Count")
    st.pyplot(fig, use_container_width=True)


def plot_daily_anomalies(df: pd.DataFrame):
    daily = (
        df.groupby("date")["anomaly_flag_global"]
        .sum()
        .reset_index(name="flagged_count")
        .sort_values("date")
    )
    st.line_chart(daily.set_index("date")["flagged_count"])


def plot_top_risk(report: pd.DataFrame, top_n: int = 10):
    top = report.sort_values("risk_score", ascending=False).head(top_n).copy()
    top = top.sort_values("risk_score", ascending=True)
    st.bar_chart(top.set_index("meter_id")["risk_score"])


def plot_meter_timeseries(meter_df: pd.DataFrame):
    meter_df = meter_df.sort_values("date").copy()

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(meter_df["date"], meter_df["daily_mean_power"], label="Daily Mean Power")

    if "rolling_mean_30" in meter_df.columns:
        ax.plot(meter_df["date"], meter_df["rolling_mean_30"], label="Rolling Mean")

    anom = meter_df[meter_df["anomaly_flag_global"] == 1]
    if len(anom) > 0:
        ax.scatter(anom["date"], anom["daily_mean_power"], label="Flagged Days")

    ax.set_title("Meter Consumption + Flagged Anomalies")
    ax.set_xlabel("Date")
    ax.set_ylabel("Power")
    ax.legend()
    st.pyplot(fig, use_container_width=True)


# --------------------
# Sidebar controls
# --------------------
try:
    meta, models_by_meter, scalers_by_meter = load_artifacts()
except Exception as e:
    st.error("Artifacts not found. Ensure `artifacts/` exists in the repo.")
    st.exception(e)
    st.stop()

st.sidebar.subheader("Model Info")
st.sidebar.write(f"Time window: {meta['start_date']} → {meta['end_date']}")
st.sidebar.write(f"Rolling window (days): {meta['rolling_window_days']}")
st.sidebar.write(f"Global threshold: {meta['global_threshold']:.6f}")

run_btn = st.sidebar.button("Run Scoring")

if st.sidebar.button("Clear Outputs"):
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
        st.sidebar.success("Cleared outputs/ ✅")
    else:
        st.sidebar.info("No outputs/ folder found.")

if DATA_MODE == "Upload CSVs":
    power_file = st.sidebar.file_uploader("Upload power CSV", type=["csv"])
    weather_file = st.sidebar.file_uploader("Upload weather CSV", type=["csv"])
else:
    power_file = None
    weather_file = None


# --------------------
# Tabs
# --------------------
tabD, tab0, tab1, tab2, tab3 = st.tabs(
    ["Dashboard", "How to Use", "Inspection Report", "Alerts", "Export"]
)

with tab0:
    st.subheader("How to use this app")
    st.markdown(
        """
1. Choose **Data mode** in the sidebar:
   - **Use repo data** (demo mode), or
   - **Upload CSVs** (your own datasets).
2. Click **Run Scoring** to compute anomaly scores and generate the inspection report.
3. Review results in **Dashboard**, **Inspection Report**, and **Alerts**.
4. Download outputs in the **Export** tab.
"""
    )
    st.warning(
        """
Upload Mode Requirements:
- Power CSV must contain: meter_id, date, daily_mean_power (and other daily features used in training)
- Weather CSV must contain: date and required weather columns used in training
- Column names must match exactly.
"""
    )
    st.caption("Note: This system flags statistical anomalies. It does not confirm electricity theft.")


if run_btn:
    with st.spinner("Scoring data..."):
        if DATA_MODE == "Upload CSVs":
            if power_file is None or weather_file is None:
                st.error("Upload both CSV files.")
                st.stop()
            power_df = pd.read_csv(power_file)
            weather_df = pd.read_csv(weather_file)
        else:
            power_df = pd.read_csv(POWER_PATH)
            weather_df = pd.read_csv(WEATHER_PATH)

        df = load_data(power_df, weather_df, meta["start_date"], meta["end_date"])
        df = add_features(df, meta["rolling_window_days"])
        df = score(df, meta["features"], models_by_meter, scalers_by_meter)

        # apply global flag
        df["anomaly_flag_global"] = (df["anomaly_score"] <= float(meta["global_threshold"])).astype(int)

        report = make_report(df, float(meta["global_threshold"]))

        # save outputs (for pages/visualization.py and downloads)
        save_outputs(df, report, meta)

    # --------------------
    # Filters + Search (Report-level)
    # --------------------
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")
    risk_filter = st.sidebar.multiselect(
        "Risk level",
        options=["High", "Medium", "Low"],
        default=["High", "Medium", "Low"],
    )
    min_risk = st.sidebar.slider("Minimum risk score", 0, 100, 0)
    only_flagged = st.sidebar.checkbox("Only meters with anomalies", value=False)
    search_meter = st.sidebar.text_input("Search meter_id")

    filtered_report = report.copy()
    filtered_report = filtered_report[filtered_report["risk_level"].isin(risk_filter)]
    filtered_report = filtered_report[filtered_report["risk_score"] >= min_risk]
    if only_flagged:
        filtered_report = filtered_report[filtered_report["total_anomalies"] > 0]
    if search_meter.strip():
        filtered_report = filtered_report[
            filtered_report["meter_id"].astype(str).str.contains(search_meter.strip(), case=False, na=False)
        ]

    # --------------------
    # KPI Summary
    # --------------------
    flagged_total = int(df["anomaly_flag_global"].sum())
    high_count = int((report["risk_level"] == "High").sum())
    med_count = int((report["risk_level"] == "Medium").sum())

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Rows scored", f"{len(df):,}")
    k2.metric("Meters", f"{report.shape[0]:,}")
    k3.metric("Flagged days", f"{flagged_total:,}")
    k4.metric("High risk meters", f"{high_count:,}")
    k5.metric("Medium risk meters", f"{med_count:,}")

    # --------------------
    # Dashboard
    # --------------------
    with tabD:
        st.subheader("Dashboard Overview")

        cA, cB = st.columns(2)
        with cA:
            plot_score_distribution(df)
        with cB:
            st.subheader("Daily Flagged Anomalies")
            plot_daily_anomalies(df)

        st.subheader("Top Risk Meters")
        top_n = st.slider("Show top N meters", 5, 20, 10)
        plot_top_risk(report, top_n=top_n)

        st.subheader("Drill-down: Meter View")
        meter_list = sorted(df["meter_id"].unique())
        selected_meter = st.selectbox("Select meter", meter_list)
        meter_df = df[df["meter_id"] == selected_meter].copy()
        plot_meter_timeseries(meter_df)

        st.caption("Tip: Use the sidebar filters to focus on High/Medium risk meters.")

    # --------------------
    # Tables
    # --------------------
    with tab1:
        st.subheader("Inspection Report (Filtered)")
        st.dataframe(filtered_report, use_container_width=True)

    with tab2:
        st.subheader("Alerts (High/Medium)")
        alerts_df = filtered_report[filtered_report["risk_level"].isin(["High", "Medium"])][
            ["meter_id", "risk_level", "risk_score", "alert_message"]
        ].copy()
        st.dataframe(alerts_df, use_container_width=True)

    with tab3:
        st.subheader("Export")
        st.write("Download the inspection report and scored daily output.")

        report_bytes = report.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Inspection Report (CSV)",
            report_bytes,
            file_name="Inspection_Report.csv",
            mime="text/csv",
        )

        scored_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Scored Output (CSV)",
            scored_bytes,
            file_name="scored_output.csv",
            mime="text/csv",
        )

else:
    with tabD:
        st.info("Run scoring first (sidebar → **Run Scoring**) to generate KPIs and charts.")
    with tab1:
        st.info("Run scoring first (sidebar → **Run Scoring**).")
    with tab2:
        st.info("Run scoring first (sidebar → **Run Scoring**).")
    with tab3:
        st.info("Run scoring first (sidebar → **Run Scoring**).")