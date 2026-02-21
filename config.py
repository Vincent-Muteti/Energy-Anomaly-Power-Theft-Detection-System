"""
Configuration file for Power Theft Detection System
====================================================
Centralized configuration for all settings.
"""

import os
from pathlib import Path

# Environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')
DEBUG = ENVIRONMENT != 'production'

# Model Configuration
MODEL_DIR = Path('models_artifacts')
MODEL_PARAMS = {
    'random_forest': {
        'n_estimators': 100,
        'max_depth': 12,
        'class_weight': 'balanced',
        'random_state': 42
    },
    'logistic_regression': {
        'max_iter': 1000,
        'class_weight': 'balanced',
        'random_state': 42,
        'solver': 'saga'
    }
}

# API Configuration
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', 5000))
API_WORKERS = int(os.getenv('API_WORKERS', 4))
API_TIMEOUT = int(os.getenv('API_TIMEOUT', 300))
API_BATCH_SIZE_MAX = 10000

# Security
API_KEY = os.getenv('API_KEY', None)
ENABLE_CORS = os.getenv('ENABLE_CORS', 'true').lower() == 'true'
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')

# Logging
LOG_FILE = 'power_theft_detection.log'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Database (Optional)
DB_ENABLED = os.getenv('DB_ENABLED', 'false').lower() == 'true'
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 5432))
DB_NAME = os.getenv('DB_NAME', 'power_theft')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')

# Monitoring
MONITORING_ENABLED = os.getenv('MONITORING_ENABLED', 'true').lower() == 'true'
METRICS_PUSH_INTERVAL = int(os.getenv('METRICS_PUSH_INTERVAL', 60))

# Feature Configuration
REQUIRED_FEATURES_COUNT = 14
PREDICTION_THRESHOLD_DEFAULT = 0.5
RISK_LEVELS = {
    'Low': (0.0, 0.3),
    'Medium': (0.3, 0.7),
    'High': (0.7, 1.0)
}

# Model Retraining
RETRAINING_SCHEDULE = 'quarterly'  # quarterly, monthly, or as-needed
RETRAINING_SAMPLE_SIZE = 100000

# Alert Configuration
ALERT_ENABLED = os.getenv('ALERT_ENABLED', 'true').lower() == 'true'
ALERT_THRESHOLD_HIGH_RISK = 0.8
ALERT_THRESHOLD_MEDIUM_RISK = 0.5
ALERT_EMAIL_RECIPIENTS = os.getenv('ALERT_EMAIL_RECIPIENTS', '').split(',')

# Performance
CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))
CACHE_MAX_SIZE = int(os.getenv('CACHE_MAX_SIZE', 1000))

# Create necessary directories
MODEL_DIR.mkdir(exist_ok=True)

if __name__ == '__main__':
    print(f"Environment: {ENVIRONMENT}")
    print(f"Model Directory: {MODEL_DIR}")
    print(f"API: {API_HOST}:{API_PORT}")
    print(f"Batch Max Size: {API_BATCH_SIZE_MAX}")
    print(f"Monitoring: {MONITORING_ENABLED}")
    print(f"Alerts: {ALERT_ENABLED}")
