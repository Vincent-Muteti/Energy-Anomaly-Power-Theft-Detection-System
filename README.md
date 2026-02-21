# Smart Power Disconnection Analytics System - Deployment Guide

## 📋 Overview

This is a production-ready machine learning system for detecting electricity theft and fraudulent meter disconnections in Kenya's power distribution network (KPLC). The system analyzes smart meter consumption data to identify suspicious patterns in real-time.

**Key Features:**
- ✅ **94.59% ROC-AUC** fraud detection accuracy (Random Forest model)
- ✅ Real-time prediction API (Flask/REST)
- ✅ Batch processing capabilities
- ✅ Feature importance analysis
- ✅ Production-ready logging and monitoring
- ✅ Docker-compatible deployment

---

## 🏗️ Project Structure

```
Energy-Anomaly-Power-Theft-Detection-System/
├── Felo.ipynb                      # Main analysis notebook
├── power_theft_detector.py         # Core prediction module
├── app.py                          # Flask API server
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── models_artifacts/               # Trained model artifacts
│   ├── random_forest.joblib       # Random Forest classifier
│   ├── logistic_regression.joblib # Logistic Regression classifier
│   ├── scaler.joblib              # StandardScaler for normalization
│   ├── features.json              # Feature list
│   └── training_results.json      # Training metrics
└── data/                          # Data files (CSV)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or conda
- 4GB RAM minimum

### Installation

**1. Clone/Extract Project**
```bash
cd Energy-Anomaly-Power-Theft-Detection-System
```

**2. Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**4. Verify Installation**
```bash
python power_theft_detector.py
```

---

## 📊 Model Performance

| Metric | Logistic Regression | Random Forest | Status |
|--------|-------------------|---------------|--------|
| **ROC-AUC** | 0.6766 | **0.9459** ✅ | Primary |
| **Precision** | 0.5283 | **0.9837** ✅ | Production |
| **Recall** | 0.6132 | **0.8741** ✅ | Deployed |
| **F1-Score** | 0.5676 | **0.9257** ✅ | Active |

---

## 🔧 Usage

### Option 1: Python Module

```python
from power_theft_detector import load_detector
import pandas as pd

detector = load_detector('models_artifacts')
results = detector.predict_batch(your_data)
```

### Option 2: REST API

```bash
python app.py
# API available at http://localhost:5000
```

**Endpoints:**
- `GET /health` - System health check
- `POST /predict` - Single prediction
- `POST /predict_batch` - Batch predictions
- `GET /features` - Required features list
- `GET /model_info` - Model metadata

---

## 🚀 Production Deployment

**Using Gunicorn (Recommended):**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Using Docker:**
```bash
docker build -t power-theft-detector .
docker run -p 5000:5000 power-theft-detector
```

**Cloud Deployment:**
- AWS: Elastic Beanstalk or ECS
- GCP: Cloud Run or App Engine
- Azure: App Service or Container Instances

---

## 📈 Integration Pipeline

```
Smart Meters → Data Collection → Feature Engineering → 
Fraud Detection → Investigation Queue → Field Team
```

---

## ✅ Production Checklist

- [ ] Install dependencies
- [ ] Test predictions locally
- [ ] Start API server
- [ ] Configure authentication
- [ ] Set up monitoring/logging
- [ ] Connect to KPLC data pipeline
- [ ] User acceptance testing
- [ ] Deploy to production
- [ ] Monitor system performance
- [ ] Schedule model retraining (quarterly)

---

**Version:** 1.0.0 | **Status:** Production Ready ✅

---

## 🇰🇪 Phase B — Production Deployment Simulation

The calibrated anomaly detection methodology was applied to a structured multi-household electricity dataset integrated with contextual weather variables.

### Data Layers Integrated

**1. Electricity Consumption Layer**
- Daily aggregated smart meter statistics
- Structured behavioral indicators

**2. Weather Context Layer**
- Temperature (tmax, tmin)
- Precipitation
- Wind speed

**3. Machine Learning Risk Layer**
- Per-meter Isolation Forest modeling
- Rolling 30-day behavioral baselines
- Residual and z-score deviation features
- Global anomaly score thresholding

---

## Machine Learning & Time-Series Methodology

### Time-Series Feature Engineering

- 30-day rolling consumption baselines
- Rolling standard deviations
- Residual deviations from historical behavior
- Standardized anomaly indicators (z-scores)
- Volatility metrics

### Unsupervised Anomaly Detection

- Per-meter Isolation Forest training
- Global 2% anomaly score threshold
- Natural variation across meters
- Persistent anomaly streak detection

### Supervised Benchmark Validation

- Random Forest theft classification
- ROC-AUC evaluation
- Feature importance extraction

### Risk Scoring & Prioritization

- Total anomalous days per meter
- Longest anomaly streak
- Worst anomaly score
- Normalized risk score (0–100)
- Risk categorization: **Low / Medium / High**
- Ranked inspection prioritization list
- Automated alert generation
- Structured CSV export for operational workflows

---

## Final System Outputs

The final system produces:

- Meter-level anomaly detection  
- Normalized risk scoring (0–100 scale)  
- Structured inspection prioritization  
- Persistent anomaly analysis  
- Automated human-readable alert messages  
- Export-ready inspection report suitable for utility workflows  

The system functions as an inspection prioritization engine rather than a static fraud classifier.

---

## Business Problem Addressed

Electricity utilities face persistent non-technical losses due to:

- Electricity theft  
- Meter tampering  
- Irregular consumption behavior  
- Inefficient manual inspection processes  

Traditional fraud detection approaches are:

- Reactive  
- Rule-based  
- Labor-intensive  
- Operationally costly  

Although smart meters generate large volumes of time-series data, most utilities lack structured machine learning systems capable of:

- Distinguishing legitimate variability from suspicious behavior  
- Adjusting for contextual influences such as weather  
- Prioritizing high-risk customers  
- Automatically generating inspection-ready alerts  

This project addresses the central question:

> How can utilities leverage machine learning and time-series analysis to proactively detect abnormal electricity behavior and automatically generate structured inspection prioritization reports?

The framework shifts utilities from reactive inspection models to proactive, data-driven anomaly intelligence.

---

## Key Insights

- Per-entity modeling significantly improves anomaly detection performance.
- Global anomaly thresholding produces realistic inspection variability.
- Contextual weather integration reduces false positive risk.
- Supervised classification validates consumption feature separability.
- Structured risk scoring bridges analytics and operational decision-making.

---

## Technologies Used

- Python
- Pandas
- NumPy
- Scikit-Learn
- Matplotlib
- Isolation Forest
- Random Forest
- Time-Series Feature Engineering

---

## Dataset Disclaimer

The deployment dataset contains simulated meter identifiers and represents a structured smart meter environment for modeling demonstration purposes.

The architecture, anomaly detection methodology, and risk scoring framework are transferable to real-world utility systems subject to validation using official operational data.

---

## Conclusion

This project demonstrates how machine learning and time-series analysis can power a scalable electricity anomaly detection framework capable of:

- Detecting abnormal consumption behavior  
- Prioritizing high-risk meters  
- Generating automated inspection alerts  
- Exporting structured investigation reports  

By integrating unsupervised anomaly detection, supervised benchmarking, contextual adjustment, rolling time-series modeling, and automated reporting, the system provides a robust and deployable inspection prioritization framework suitable for smart grid environments.

The framework illustrates how utilities can transition from reactive inspection practices toward proactive, machine learning–driven anomaly intelligence supported by structured alert generation.