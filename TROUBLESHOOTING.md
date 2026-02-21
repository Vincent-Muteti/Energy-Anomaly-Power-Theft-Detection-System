# Troubleshooting Guide - Power Theft Detection System

## Quick Navigation
- [Installation Issues](#installation-issues)
- [Runtime Issues](#runtime-issues)
- [API Issues](#api-issues)
- [Docker Issues](#docker-issues)
- [Performance Issues](#performance-issues)
- [Model/Data Issues](#modeldata-issues)
- [Deployment Issues](#deployment-issues)
- [Advanced Debugging](#advanced-debugging)

---

## Installation Issues

### Problem: Python version error
**Symptom:** `python: command not found` or version < 3.8

**Solution:**
```bash
# Check Python version
python --version
# or
python3 --version

# Install Python 3.8+
# Windows: Download from python.org
# macOS: brew install python@3.9
# Linux: apt-get install python3.9 python3.9-venv

# Use python3 explicitly if needed
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### Problem: pip version too old
**Symptom:** `WARNING: pip is being invoked by an old script wrapper`

**Solution:**
```bash
# Upgrade pip, setuptools, and wheel
python -m pip install --upgrade pip setuptools wheel
```

### Problem: Virtual environment not activating
**Symptom:** `(venv)` prefix not showing in terminal

**Windows:**
```cmd
# Try alternative activation methods
venv\Scripts\activate.bat  # Standard
call venv\Scripts\activate.bat  # In batch files

# Or use Python directly
python -m venv --upgrade-deps venv
```

**Linux/macOS:**
```bash
# Check venv exists and activate
ls -la venv/
source venv/bin/activate

# Or recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

### Problem: Dependency installation fails
**Symptom:** `ERROR: Could not find a version that satisfies the requirement`

**Solution:**
```bash
# Clear pip cache
pip cache purge

# Upgrade pip and try again
python -m pip install --upgrade pip

# Install with specific version constraints
pip install --upgrade -r requirements.txt

# If specific package fails, install individually
pip install scikit-learn==1.3.0
pip install pandas==2.0.3

# Check system dependencies (Linux)
sudo apt-get install python3-dev  # Required for some packages
```

### Problem: ModuleNotFoundError after installation
**Symptom:** `ModuleNotFoundError: No module named 'sklearn'`

**Diagnosis & Solution:**
```bash
# Verify venv is activated (look for prefix in terminal)
which python  # Should point to venv/bin/python

# Re-install packages
pip install -r requirements.txt

# Verify installation
python -c "import sklearn; print(sklearn.__version__)"

# Clear Python bytecode cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete

# Restart terminal/IDE
```

---

## Runtime Issues

### Problem: Port 5000 already in use
**Symptom:** `Address already in use` or `Cannot bind to port 5000`

**Solution:**

**Windows:**
```cmd
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or use different port
python app.py --port 8080
```

**Linux/macOS:**
```bash
# Find process
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
python app.py --port 8080
```

### Problem: Application crashes immediately
**Symptom:** Process starts then exits silently

**Solution:**
```bash
# Enable debug mode to see errors
export FLASK_ENV=development
export LOG_LEVEL=DEBUG
python app.py

# Or check logs
python app.py 2>&1 | tee debug.log

# Check specific error by importing module
python -c "from app import app; print('Import OK')"
```

### Problem: Model artifacts not found
**Symptom:** `FileNotFoundError: models_artifacts not found` or `random_forest.joblib`

**Solution:**
```bash
# Check directory structure
ls -la models_artifacts/

# Required files must exist:
# - random_forest.joblib (trained model)
# - logistic_regression.joblib (backup model)
# - scaler.joblib (feature scaler)
# - features.json (feature specification)
# - training_results.json (model metrics)

# If missing, run notebook to generate models
jupyter notebook grace.ipynb  # Execute training cells

# Or download from backup
# (Ensure you have backup of trained models)
```

### Problem: Out of memory error
**Symptom:** `MemoryError` or process killed unexpectedly

**Diagnosis & Solution:**
```bash
# Check available memory
# Windows: wmic OS get TotalVisibleMemorySize,TotalVisibleMemoryFree
# Linux: free -h
# macOS: vm_stat

# Monitor during execution
# Windows: Task Manager
# Linux/macOS: top -p <PID>

# Reduce batch size in app.py
# From: MAX_BATCH_SIZE = 10000
# To: MAX_BATCH_SIZE = 1000

# Enable memory profiling
pip install memory-profiler
python -m memory_profiler app.py
```

---

## API Issues

### Problem: API returns 400 Bad Request
**Symptom:** `{error: "Bad Request"}` on POST request

**Solution:**
```bash
# Verify JSON format
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d @request.json  # Read from file for validation

# Check for required fields
curl http://localhost:5000/features  # Get feature list

# Validate JSON
python -m json.tool request.json

# Common issues:
# - Missing quotes around strings
# - Comma at end of object {"key": "value",}
# - Incorrect data types (string instead of number)
```

### Problem: API returns 422 Unprocessable Entity
**Symptom:** `{error: "Unprocessable Entity"}`

**Solution:**
```bash
# Feature mismatch - verify exact features required
curl http://localhost:5000/features | python -m json.tool

# Check feature count
# Should be exactly 14 required features

# Verify feature names match exactly (case-sensitive)
# Use this template for testing:
cat > test_request.json << 'EOF'
{
  "customer_id": "TEST001",
  "monthly_kwh_consumption": 150,
  "bill_pay_rate": 0.95,
  "days_since_meter_installation": 1500,
  "final_spread_value": 2.5,
  "interior_equipment_status": 1,
  "interior_lights_status": 0,
  "tamper_indicator": 0,
  "reactive_power_import": 50,
  "reactive_power_export": 10,
  "neutral_current": 1.2,
  "peak_voltage_deviation": 5,
  "non_technical_losses": 0.15,
  "phase_imbalance_percentage": 8
}
EOF

curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

### Problem: API returns 500 Internal Server Error
**Symptom:** `{error: "Internal Server Error"}`

**Solution:**
```bash
# Check server logs
# Look for error messages in terminal output

# Enable debug mode
export FLASK_DEBUG=True
export LOG_LEVEL=DEBUG
python app.py

# Check model loading
python -c "
from power_theft_detector import PowerTheftDetector
detector = PowerTheftDetector('./models_artifacts')
print('Model loaded successfully')
"

# Check specific endpoint
python -c "
from app import app
with app.app_context():
    # Test endpoint logic
    print('App context OK')
"
```

### Problem: Slow API response time
**Symptom:** Predictions take >500ms or API becomes unresponsive

**Solution:**
```bash
# Profile request time
time curl http://localhost:5000/predict \
  -X POST -H "Content-Type: application/json" \
  -d @request.json

# Check system resources
# Windows: Task Manager > Performance
# Linux: top, htop
# macOS: Activity Monitor

# Reduce model complexity or use Logistic Regression
# In request: {"use_model": "logistic_regression"}

# Run with Gunicorn for better performance
gunicorn -w 4 -b 0.0.0.0:5000 \
  --timeout 30 \
  --workers-class sync \
  app:app

# Increase workers based on CPU count
gunicorn -w $(nproc) -b 0.0.0.0:5000 app:app
```

---

## Docker Issues

### Problem: Docker command not found
**Symptom:** `docker: command not found` or `Docker daemon not running`

**Solution:**
```bash
# Check Docker installation
docker --version

# Start Docker daemon
# Windows: Docker Desktop app
# macOS: Docker Desktop > Preferences > Docker Daemon
# Linux: sudo systemctl start docker

# Verify Docker is running
docker ps

# Fix permission issues (Linux)
sudo usermod -aG docker $USER
newgrp docker
```

### Problem: Build fails with "no such file or directory"
**Symptom:** `COPY failed: file not found`

**Solution:**
```bash
# Verify files exist before build
ls -la requirements.txt power_theft_detector.py app.py config.py

# Build from correct directory
cd /path/to/project
docker build -t power-theft-detector .

# Check Dockerfile syntax
docker build --no-cache -t power-theft-detector .

# View build output
docker build -t power-theft-detector . --progress=plain
```

### Problem: Container fails to start
**Symptom:** Container exits immediately with error

**Solution:**
```bash
# View container logs
docker logs <container_id>

# Run with interactive terminal
docker run -it power-theft-detector /bin/bash

# Test image layers
docker build -t power-theft-detector . --progress=plain

# Verify Python in container
docker run power-theft-detector python --version

# Check installed packages
docker run power-theft-detector pip list
```

### Problem: Port mapping not working
**Symptom:** Cannot connect to http://localhost:5000 from host

**Solution:**
```bash
# Verify port is exposed
docker ps  # Check PORTS column

# Correct port mapping syntax
# From: docker run -p 5000:5000 power-theft-detector
# Correct: docker run -p 5000:5000 power-theft-detector

# Test from inside container
docker run -it power-theft-detector bash
curl http://localhost:5000/health

# Check firewall
# Windows: Windows Defender Firewall > Allow an app
# Linux: sudo ufw allow 5000
# macOS: System Preferences > Security & Privacy
```

### Problem: Docker Compose fails to start
**Symptom:** `ERROR: Service 'power-theft-api' failed to build`

**Solution:**
```bash
# Validate docker-compose.yml syntax
docker-compose config

# Build services explicitly
docker-compose build --no-cache

# Check for port conflicts
docker ps
lsof -i :5000  # Port 5000
lsof -i :9090  # Port 9090
lsof -i :5601  # Port 5601

# View service logs
docker-compose logs power-theft-api
docker-compose logs prometheus
docker-compose logs elasticsearch

# Recreate containers
docker-compose down
docker-compose up -d --force-recreate
```

---

## Performance Issues

### Problem: Model predictions are slow
**Symptom:** Batch predictions taking >10s for 1000 records

**Diagnosis:**

```bash
# Profile model loading time
python -c "
import time
from power_theft_detector import PowerTheftDetector

start = time.time()
detector = PowerTheftDetector('./models_artifacts')
print(f'Model load: {time.time() - start:.2f}s')

start = time.time()
result = detector.predict({...})
print(f'Single prediction: {time.time() - start:.4f}s')
"

# Check model file size
ls -lh models_artifacts/random_forest.joblib

# Monitor resource usage
top -p <python_pid>
```

**Solution:**

```bash
# Use Logistic Regression (faster)
detector.predict(data, use_model='logistic_regression')

# Reduce number of trees in Random Forest (if retraining)
# RandomForestClassifier(n_estimators=50)  # from 100

# Enable model caching
# Implement Redis cache for repeated predictions

# Use batch predictions instead of loop
# From: for record in records: detector.predict(record)
# To: detector.predict_batch(records)

# Upgrade hardware or cloud resources
# Increase CPU cores and RAM allocation
```

### Problem: Jupyter notebook runs very slowly
**Symptom:** Cell execution time > 5 minutes for training

**Solution:**
```bash
# Check available memory
python -c "
import psutil
print(f'Available RAM: {psutil.virtual_memory().available / 1e9:.1f}GB')
"

# Reduce dataset size for testing
# Instead of: df = pd.read_csv('file.csv')  # 1GB file
# Use: df = pd.read_csv('file.csv', nrows=10000)

# Disable unnecessary features
# Skip visualization cells until final validation

# Optimize data types
# From: df = pd.read_csv('file.csv', dtype='float64')
# To: df = pd.read_csv('file.csv', dtype='float32')

# Use sampling for large datasets
# df_sample = df.sample(n=50000, random_state=42)

# Close unused notebooks and applications
```

---

## Model/Data Issues

### Problem: Model accuracy is low
**Symptom:** ROC-AUC < 0.80 or F1-score declining

**Diagnosis:**
```bash
# Check model metrics
python -c "
import json
with open('models_artifacts/training_results.json') as f:
    metrics = json.load(f)
    print(f'ROC-AUC: {metrics[\"roc_auc\"]:.4f}')
    print(f'Precision: {metrics[\"precision\"]:.4f}')
    print(f'Recall: {metrics[\"recall\"]:.4f}')
    print(f'F1-Score: {metrics[\"f1_score\"]:.4f}')
"

# Check feature distribution
# Plot histograms of features in training data
# Verify features have expected ranges

# Check for data drift
# Compare recent data distribution vs training data

# Check model version
# Ensure using latest trained model files
```

**Solution:**
```bash
# Retrain model with updated data
jupyter notebook grace.ipynb
# Execute training cells 1-68

# Tune hyperparameters
# In training notebook:
# RandomForestClassifier(n_estimators=150, max_depth=15, ...)

# Add new features or engineer existing ones
# Remove noisy or low-importance features

# Balance dataset if imbalanced
# from sklearn.utils.class_weight import compute_class_weight
```

### Problem: Feature validation errors
**Symptom:** `ValueError: Feature mismatch` or `KeyError: feature not found`

**Solution:**
```bash
# Check features.json for exact feature names
cat models_artifacts/features.json

# Verify prediction input matches exactly
# The 14 required features are:
curl http://localhost:5000/features | python -m json.tool

# Case-sensitive: "monthly_kwh_consumption" not "Monthly_KWh_Consumption"

# Missing features in request
jq '.require_fieldnames' models_artifacts/features.json
```

### Problem: Data loading errors in notebook
**Symptom:** `FileNotFoundError` or `pd.read_csv fails`

**Solution:**
```bash
# Check data files exist
ls -la *.csv

# Required CSV files:
# - power_multi_household_daily.csv (main power data)
# - nairobi_weather_2007_2008.csv (weather data)
# - kplc_planned_outages.csv (outages schedule)
# - KPLC_Inspection_Report_2007_2008.csv (inspection data)
# - kplc_daily_schedule.csv (schedule data)
# - lead1.0-small.csv (lead indicators)

# Check file size and corruption
file power_multi_household_daily.csv

# Verify CSV format
head -5 power_multi_household_daily.csv

# Re-download if corrupted
# (Ensure backup data sources available)
```

---

## Deployment Issues

### Problem: AWS Elastic Beanstalk deployment fails
**Symptom:** `EnvironmentUpdateFailed`

**Solution:**
```bash
# Check deployment logs
eb logs

# Verify requirements.txt format
pip freeze > requirements.txt

# Check for binary dependencies
# Model files must be in git-ignored path or S3

# Reduce app bundle size
# Remove notebooks and unnecessary files from deployment
eb create --ignore-version-conflict

# Test locally first
eb local run

# Check for environment variable issues
eb config
# Ensure MODEL_PATH and other vars set correctly
```

### Problem: GCP Cloud Run deployment fails
**Symptom:** `Cloud Build fails` or `container fails to start`

**Solution:**
```bash
# Test build locally first
docker build -t gcr.io/PROJECT_ID/power-theft-detector .

# Check Cloud Build logs
gcloud builds log <BUILD_ID>

# Verify Dockerfile is multi-platform compatible
docker buildx build --platform linux/amd64 -t gcr.io/<PROJECT>/power-theft-detector .

# Check Secret Manager for credentials
gcloud secrets list

# Verify service account permissions
# Cloud Run needs: roles/run.admin, roles/iam.serviceAccountUser

# Test Cloud Run locally
gcloud beta run local-source-deploy \
  --source=. \
  --region=us-central1
```

### Problem: Azure App Service deployment fails
**Symptom:** `Deployment from local Git failed`

**Solution:**
```bash
# Check deployment logs
az webapp log stream --resource-group <RG> --name <APP_NAME>

# Verify Python version in Azure
# App Service > Configuration > Stack settings

# Check .gitignore doesn't exclude important files
cat .gitignore

# Deploy via ZIP file instead
zip -r app.zip . -x "venv/*" ".git/*" "__pycache__/*"
az webapp deployment source config-zip \
  --resource-group <RG> \
  --name <APP_NAME> \
  --src-path app.zip

# Verify startup script
az webapp config show --resource-group <RG> --name <APP_NAME>
```

---

## Advanced Debugging

### Enable Verbose Logging

```bash
# Python logging
export LOG_LEVEL=DEBUG
python app.py

# Flask debug mode
export FLASK_DEBUG=True
export FLASK_ENV=development
python app.py

# Scikit-learn warnings
import warnings
warnings.simplefilter('always')

# Pandas display options
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
```

### Memory Profiling

```bash
pip install memory-profiler

# Run with memory profiling
python -m memory_profiler app.py

# Profile specific function
@profile
def predict(self, data):
    # function code
    pass
```

### Database Connection Issues (if applicable)

```bash
# Test database connectivity
python -c "
import os
import sqlite3
db_path = os.getenv('DB_PATH', './app.db')
conn = sqlite3.connect(db_path)
print(f'Connected to {db_path}')
"

# Check database file size and permissions
ls -la app.db
```

### Network Debugging

```bash
# Check API connectivity
curl -v http://localhost:5000/health

# Test from different host
curl -v http://<server_ip>:5000/health

# Check open ports
netstat -tuln | grep 5000

# Firewall issues
sudo iptables -L
```

### Git/Version Control Issues

```bash
# Check git status
git status

# View recent commits
git log --oneline -10

# Reset to known good state
git reset --hard origin/main

# Clear git cache if modified files not showing
git rm -r --cached .
git add .
```

---

## Getting Help

If none of these solutions work:

1. **Check Logs**
   - `power_theft.log` (if logging enabled)
   - Docker logs: `docker logs <container>`
   - Application console output

2. **Verify Setup**
   - Run `python test_deployment.py`
   - Check model artifacts exist
   - Verify all dependencies installed

3. **Consult Documentation**
   - [README.md](README.md)
   - [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
   - [QUICKSTART.md](QUICKSTART.md)

4. **Reproduce Issue**
   - Minimal test case
   - Clear steps to reproduce
   - Error messages and logs

5. **Contact Support**
   - Include version info: `python --version`, `docker --version`
   - Include error logs and stack traces
   - Describe environment: OS, hardware, network setup
