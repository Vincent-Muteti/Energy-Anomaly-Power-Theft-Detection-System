"""
Power Theft Detection API
==========================
Flask REST API for real-time fraud detection on KPLC smart meter data.

Endpoints:
  - GET  /health              : System health check
  - POST /predict             : Single record prediction
  - POST /predict_batch       : Batch predictions
  - GET  /features            : List required features
  - GET  /model_info          : Model metadata

Author: KPLC Data Science Team
Date: 2026-02-21
"""

import json
import logging
import traceback
from datetime import datetime
from functools import wraps

import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

from power_theft_detector import PowerTheftDetector, load_detector

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global detector instance
detector = None


def initialize_detector():
    """Initialize the detector on app startup."""
    global detector
    try:
        detector = load_detector('models_artifacts')
        logger.info("✓ Detector initialized successfully")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to initialize detector: {str(e)}")
        return False


def require_detector(f):
    """Decorator to ensure detector is initialized."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if detector is None or not detector.is_initialized:
            return jsonify({'error': 'Detector not initialized'}), 500
        return f(*args, **kwargs)
    return decorated_function


@app.route('/health', methods=['GET'])
def health_check():
    """System health check endpoint."""
    status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'detector_initialized': detector is not None and detector.is_initialized,
        'service': 'Power Theft Detection API',
        'version': '1.0.0'
    }
    return jsonify(status), 200


@app.route('/model_info', methods=['GET'])
@require_detector
def model_info():
    """Return model metadata and configuration."""
    try:
        info = detector.get_model_info()
        info['timestamp'] = datetime.now().isoformat()
        return jsonify(info), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/features', methods=['GET'])
@require_detector
def get_features():
    """Return list of required input features."""
    try:
        top_features = detector.get_top_features(15).to_dict('records')
        return jsonify({
            'feature_count': len(detector.features),
            'all_features': detector.features,
            'top_15_features': top_features,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/predict', methods=['POST'])
@require_detector
def predict():
    """
    Predict fraud for a single meter record.
    
    Request JSON:
    {
        "meter_id": "METER001",
        "features": {
            "Electricity:Facility [kW](Hourly)": 2.5,
            "Fans:Electricity [kW](Hourly)": 0.3,
            ...
        },
        "model": "random_forest"  # Optional, default: random_forest
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({'error': 'Empty request body'}), 400
        
        if 'features' not in data:
            return jsonify({'error': 'Missing "features" key'}), 400
        
        features_dict = data.get('features', {})
        model = data.get('model', 'random_forest')
        meter_id = data.get('meter_id', 'UNKNOWN')
        
        # Create DataFrame from features
        df = pd.DataFrame([features_dict])
        
        # Ensure all required features are present
        missing = set(detector.features) - set(df.columns)
        if missing:
            return jsonify({
                'error': f'Missing features: {list(missing)}'
            }), 400
        
        # Make prediction
        predictions, probabilities = detector.predict(df, use_model=model)
        
        result = {
            'meter_id': meter_id,
            'prediction': int(predictions[0]),
            'prediction_label': 'THEFT' if predictions[0] == 1 else 'NORMAL',
            'fraud_probability': float(probabilities[0]),
            'confidence': float(max(predictions[0], 1 - predictions[0])),
            'risk_level': 'High' if probabilities[0] > 0.7 else 'Medium' if probabilities[0] > 0.3 else 'Low',
            'model': model,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Prediction for {meter_id}: {result['prediction_label']} ({result['fraud_probability']:.4f})")
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@app.route('/predict_batch', methods=['POST'])
@require_detector
def predict_batch():
    """
    Predict fraud for multiple meter records.
    
    Request JSON:
    {
        "records": [
            {
                "meter_id": "METER001",
                "Electricity:Facility [kW](Hourly)": 2.5,
                "Fans:Electricity [kW](Hourly)": 0.3,
                ...
            },
            ...
        ],
        "model": "random_forest",
        "threshold": 0.5
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'records' not in data:
            return jsonify({'error': 'Missing "records" key'}), 400
        
        records = data.get('records', [])
        if not records:
            return jsonify({'error': 'No records provided'}), 400
        
        if len(records) > 10000:
            return jsonify({'error': 'Batch size exceeds maximum (10000)'}), 400
        
        model = data.get('model', 'random_forest')
        threshold = data.get('threshold', 0.5)
        
        # Create DataFrame from records
        df = pd.DataFrame(records)
        
        # Check required features
        missing = set(detector.features) - set(df.columns)
        if missing:
            return jsonify({
                'error': f'Missing features: {list(missing)}'
            }), 400
        
        # Make predictions
        results_df = detector.predict_batch(df, threshold=threshold)
        
        # Convert to JSON-serializable format
        results = results_df.to_dict('records')
        
        summary = {
            'total_records': len(results),
            'fraud_cases': int((results_df['prediction'] == 1).sum()),
            'normal_cases': int((results_df['prediction'] == 0).sum()),
            'high_risk': int((results_df['risk_level'] == 'High').sum()),
            'avg_fraud_probability': float(results_df['fraud_probability'].mean()),
            'model': model,
            'threshold': threshold,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Batch prediction: {summary['total_records']} records, {summary['fraud_cases']} fraud cases")
        
        return jsonify({
            'summary': summary,
            'predictions': results
        }), 200
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Initialize detector
    if not initialize_detector():
        logger.error("Failed to initialize detector. Exiting.")
        exit(1)
    
    # Start Flask app
    logger.info("Starting Power Theft Detection API on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
