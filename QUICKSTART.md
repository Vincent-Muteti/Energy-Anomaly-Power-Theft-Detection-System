# Quick Start Guide - Power Theft Detection System

## 📋 Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Running Locally](#running-locally)
4. [Testing](#testing)
5. [Docker Deployment](#docker-deployment)
6. [Cloud Deployment](#cloud-deployment)
7. [API Usage](#api-usage)
8. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements
- **CPU:** 2 cores (4+ recommended)
- **RAM:** 4GB minimum (8GB recommended)
- **Storage:** 2GB free space
- **Network:** Internet connection for cloud deployment
- **Python:** 3.8+ (3.9+ recommended)

### Optional
- **Docker:** For containerized deployment
- **Docker Compose:** For stack orchestration
- **Git:** For version control

---

## Installation

### Windows
**Option 1: Batch Script (Recommended)**
```cmd
cd /path/to/project
setup.bat
```

**Option 2: PowerShell Script**
```powershell
cd /path/to/project
.\setup.ps1
```

**Option 3: Manual Setup**
```cmd
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
python test_deployment.py
```

### Linux / macOS
**Option 1: Bash Script (Recommended)**
```bash
cd /path/to/project
chmod +x setup.sh
./setup.sh
```

**Option 2: Manual Setup**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python test_deployment.py
```

---

## Running Locally

### 1. Activate Virtual Environment

**Windows:**
```cmd
venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 2. Run API Server

**Development Mode:**
```bash
python app.py
```

**Production Mode (Gunicorn):**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**With Custom Port:**
```bash
python app.py --port 8080
```

### 3. Verify Server is Running

```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

---

## Testing

### Run All Tests
```bash
python test_deployment.py
```

### Run Specific Tests
```bash
python -m pytest test_deployment.py::TestImports -v
python -m pytest test_deployment.py::TestPowerTheftDetector -v
python -m pytest test_deployment.py::TestFlaskAPI -v
```

### Manual API Testing

**Health Check:**
```bash
curl http://localhost:5000/health
```

**Get Model Info:**
```bash
curl http://localhost:5000/model_info
```

**Get Required Features:**
```bash
curl http://localhost:5000/features
```

**Single Prediction:**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST001",
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
  }'
```

**Batch Prediction (up to 10 records):**
```bash
curl -X POST http://localhost:5000/predict_batch \
  -H "Content-Type: application/json" \
  -d '{
    "records": [
      {
        "customer_id": "CUST001",
        "monthly_kwh_consumption": 150,
        ...
      },
      {
        "customer_id": "CUST002",
        "monthly_kwh_consumption": 450,
        ...
      }
    ],
    "threshold": 0.5
  }'
```

### Python Module Testing

```python
from power_theft_detector import PowerTheftDetector

# Initialize detector
detector = PowerTheftDetector('./models_artifacts')

# Get model info
info = detector.get_model_info()
print(info)

# Single prediction
result = detector.predict({
    'monthly_kwh_consumption': 150,
    'bill_pay_rate': 0.95,
    # ... other features
})
print(f"Fraud Probability: {result['probability']:.4f}")
print(f"Prediction: {result['prediction']}")

# Batch prediction
results = detector.predict_batch(df_records)
print(results)

# Feature importance
features = detector.get_top_features(n=10)
for feature, importance in features:
    print(f"{feature}: {importance:.4f}")
```

---

## Docker Deployment

### Build Docker Image
```bash
docker build -t power-theft-detector .
```

### Run Container Locally
```bash
docker run -p 5000:5000 power-theft-detector
```

### Run with Environment Variables
```bash
docker run -p 5000:5000 \
  -e FLASK_ENV=production \
  -e LOG_LEVEL=INFO \
  power-theft-detector
```

### Push to Docker Registry (AWS ECR)
```bash
# Authenticate
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag power-theft-detector:latest \
  123456789.dkr.ecr.us-east-1.amazonaws.com/power-theft-detector:latest

# Push
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/power-theft-detector:latest
```

### Docker Compose (Full Stack with Monitoring)
```bash
docker-compose up -d
```

Services:
- API: http://localhost:5000
- Prometheus: http://localhost:9090
- Kibana: http://localhost:5601

---

## Cloud Deployment

### AWS Elastic Beanstalk
```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.9 power-theft-detector

# Create environment
eb create production-env

# Deploy
eb deploy
```

### AWS ECS/ECR
```bash
# Create ECR repository
aws ecr create-repository --repository-name power-theft-detector

# Build and push
docker build -t power-theft-detector .
docker tag power-theft-detector:latest <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/power-theft-detector:latest
docker push <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/power-theft-detector:latest

# Deploy with ECS (use CloudFormation/Terraform)
```

### Google Cloud Run
```bash
# Authenticate
gcloud auth login

# Build and push
gcloud builds submit --tag gcr.io/<PROJECT_ID>/power-theft-detector

# Deploy
gcloud run deploy power-theft-detector \
  --image gcr.io/<PROJECT_ID>/power-theft-detector \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2
```

### Azure App Service
```bash
# Using Azure CLI
az group create --name power-theft-rg --location eastus

az appservice plan create --name power-theft-plan \
  --resource-group power-theft-rg --sku B2

az webapp create --resource-group power-theft-rg \
  --plan power-theft-plan --name power-theft-app

# Deploy from local Git
git remote add azure https://<username>@power-theft-app.scm.azurewebsites.net/power-theft-app.git
git push azure main
```

---

## API Usage

### Endpoint Summary

| Method | Endpoint | Purpose | Response |
|--------|----------|---------|----------|
| GET | `/health` | System health check | `{status, timestamp, version}` |
| GET | `/model_info` | Model configuration | `{model_type, features_count, metrics}` |
| GET | `/features` | List required features | `[{name, importance, data_type}]` |
| POST | `/predict` | Single prediction | `{customer_id, probability, prediction, risk_level}` |
| POST | `/predict_batch` | Batch prediction (≤10k) | `{records: [{...}], summary:{total, flagged, timestamp}}` |

### Response Codes
- `200`: Success
- `400`: Invalid request (missing/malformed data)
- `422`: Validation error (feature mismatch)
- `500`: Server error

### Example: Complete Workflow

```python
import requests
import json

BASE_URL = "http://localhost:5000"

# 1. Check health
response = requests.get(f"{BASE_URL}/health")
print("API Status:", response.json()['status'])

# 2. Get model info
response = requests.get(f"{BASE_URL}/model_info")
print("Model Info:", response.json())

# 3. Get required features
response = requests.get(f"{BASE_URL}/features")
features = response.json()
print(f"Required features: {len(features)}")

# 4. Make prediction
customer_data = {
    "customer_id": "METER_12345",
    "monthly_kwh_consumption": 250,
    "bill_pay_rate": 0.92,
    "days_since_meter_installation": 1200,
    "final_spread_value": 3.2,
    "interior_equipment_status": 1,
    "interior_lights_status": 1,
    "tamper_indicator": 0,
    "reactive_power_import": 75,
    "reactive_power_export": 20,
    "neutral_current": 1.5,
    "peak_voltage_deviation": 8,
    "non_technical_losses": 0.2,
    "phase_imbalance_percentage": 12
}

response = requests.post(
    f"{BASE_URL}/predict",
    json=customer_data,
    headers={"Content-Type": "application/json"}
)
prediction = response.json()
print(f"Fraud Probability: {prediction['probability']:.2%}")
print(f"Risk Level: {prediction['risk_level']}")

# 5. Batch predictions
batch_data = {
    "records": [customer_data, customer_data],  # Multiple records
    "threshold": 0.5
}

response = requests.post(
    f"{BASE_URL}/predict_batch",
    json=batch_data
)
results = response.json()
print(f"Batch processed: {results['summary']['total']} records")
print(f"Suspicious: {results['summary']['flagged']} records")
```

---

## Troubleshooting

### Common Issues

**Issue: Port 5000 already in use**
```bash
# Find process using port
# Windows: netstat -ano | findstr :5000
# Linux: lsof -i :5000

# Kill process or use different port
python app.py --port 8080
```

**Issue: Model artifacts not found**
```bash
# Ensure model files exist
ls -la models_artifacts/

# Required files:
# - random_forest.joblib
# - logistic_regression.joblib
# - scaler.joblib
# - features.json
# - training_results.json
```

**Issue: Import errors**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Verify installation
python -c "import sklearn, pandas, numpy; print('OK')"
```

**Issue: Docker build fails**
```bash
# Clear cache and rebuild
docker build --no-cache -t power-theft-detector .

# Check Docker daemon
docker ps
```

**Issue: API returns 422 error**
```bash
# Check required features
curl http://localhost:5000/features

# Ensure all 14 features in request
# Validate data types (numeric values required)
```

### Debug Mode

```bash
# Enable verbose logging
export FLASK_ENV=development
export LOG_LEVEL=DEBUG
python app.py
```

### Performance Monitoring

```bash
# Monitor system resources
# Windows: Task Manager or: wmic os get totalvisiblememoryfSize,totalvisiblememoryFReeFSize
# Linux: top, htop, or: free -h

# Monitor API endpoints
curl http://localhost:8000/metrics  # Prometheus metrics
```

### Log Files

- **Flask Logs:** `power_theft.log` (when logging enabled)
- **Docker Logs:** `docker logs <container_id>`
- **Elasticsearch:** `docker logs <elasticsearch_container_id>`
- **Nginx Access:** `/var/log/nginx/access.log`

---

## Security Checklist Before Production

- [ ] Remove debug mode (`FLASK_DEBUG=False`)
- [ ] Enable CORS only for trusted domains
- [ ] Set strong API authentication credentials
- [ ] Configure HTTPS/SSL certificates
- [ ] Enable rate limiting
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerting
- [ ] Enable application logging
- [ ] Regular security updates for dependencies
- [ ] Database credentials in environment variables
- [ ] Regular backups of model artifacts
- [ ] Load testing on staging environment

---

## Performance Benchmarks

| Operation | Latency | Throughput |
|-----------|---------|-----------|
| Single Prediction | <100ms | - |
| Batch (1k records) | <5s | - |
| Batch (10k records) | <50s | 10k+/min |
| Model Load | ~2s | once/startup |
| Health Check | <10ms | unlimited |

---

## Support & Documentation

- **README.md** - Project overview and quick reference
- **DEPLOYMENT_GUIDE.md** - Detailed deployment procedures for all platforms
- **Jupyter Notebooks** - Data analysis and model development
  - `grace.ipynb` - Main analysis pipeline
  - `Felo.ipynb` - Production model with visualizations
  - `group5.ipynb` - Team collaboration notebook

---

## Version Info

- **System Version:** 1.0.0
- **Python Version:** 3.8+ (tested on 3.9, 3.10, 3.11)
- **Last Updated:** January 2024
- **License:** Private (KPLC)

---

**For detailed deployment procedures, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**
