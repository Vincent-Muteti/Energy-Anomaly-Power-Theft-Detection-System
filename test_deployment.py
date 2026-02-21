#!/usr/bin/env python
"""
Deployment Verification Script
===============================
Tests all components before production deployment.

Usage:
    python test_deployment.py [--verbose]
"""

import sys
import json
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(msg):
    print(f"\n{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BLUE}{msg}{Colors.END}")
    print(f"{Colors.BLUE}{'='*80}{Colors.END}")

def print_pass(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_fail(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_warn(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def test_imports():
    """Test all required imports."""
    print_header("Testing Imports")
    
    try:
        import pandas
        print_pass("pandas imported")
    except ImportError as e:
        print_fail(f"pandas import failed: {e}")
        return False
    
    try:
        import numpy
        print_pass("numpy imported")
    except ImportError as e:
        print_fail(f"numpy import failed: {e}")
        return False
    
    try:
        import sklearn
        print_pass("scikit-learn imported")
    except ImportError as e:
        print_fail(f"scikit-learn import failed: {e}")
        return False
    
    try:
        import joblib
        print_pass("joblib imported")
    except ImportError as e:
        print_fail(f"joblib import failed: {e}")
        return False
    
    try:
        import flask
        print_pass("Flask imported")
    except ImportError as e:
        print_fail(f"Flask import failed: {e}")
        return False
    
    return True

def test_model_artifacts():
    """Test if all model artifacts exist."""
    print_header("Testing Model Artifacts")
    
    artifacts = [
        'models_artifacts/random_forest.joblib',
        'models_artifacts/logistic_regression.joblib',
        'models_artifacts/scaler.joblib',
        'models_artifacts/features.json',
        'models_artifacts/training_results.json'
    ]
    
    all_exist = True
    for artifact in artifacts:
        if Path(artifact).exists():
            size = Path(artifact).stat().st_size / (1024*1024)
            print_pass(f"{artifact} ({size:.2f} MB)")
        else:
            print_fail(f"{artifact} NOT FOUND")
            all_exist = False
    
    return all_exist

def test_detector():
    """Test PowerTheftDetector initialization."""
    print_header("Testing PowerTheftDetector")
    
    try:
        from power_theft_detector import PowerTheftDetector
        print_pass("PowerTheftDetector imported")
    except Exception as e:
        print_fail(f"Failed to import PowerTheftDetector: {e}")
        return False
    
    try:
        detector = PowerTheftDetector('models_artifacts')
        print_pass("PowerTheftDetector initialized")
    except Exception as e:
        print_fail(f"Failed to initialize PowerTheftDetector: {e}")
        return False
    
    # Test model info
    try:
        info = detector.get_model_info()
        print_pass(f"Model info retrieved ({len(info['features'])} features)")
    except Exception as e:
        print_fail(f"Failed to get model info: {e}")
        return False
    
    # Test top features
    try:
        top_feats = detector.get_top_features(5)
        print_pass(f"Top features: {', '.join(top_feats['Feature'].head(3).tolist())}")
    except Exception as e:
        print_fail(f"Failed to get top features: {e}")
        return False
    
    return True

def test_predictions():
    """Test making predictions."""
    print_header("Testing Predictions")
    
    try:
        from power_theft_detector import PowerTheftDetector
        detector = PowerTheftDetector('models_artifacts')
    except Exception as e:
        print_fail(f"Failed to load detector: {e}")
        return False
    
    # Create sample data
    try:
        n_samples = 5
        n_features = len(detector.features)
        sample_data = np.random.randn(n_samples, n_features)
        
        predictions, probabilities = detector.predict(sample_data)
        print_pass(f"Single predictions: {predictions}")
        print_pass(f"Probabilities: {probabilities.round(3)}")
    except Exception as e:
        print_fail(f"Failed to make predictions: {e}")
        return False
    
    # Test batch predictions
    try:
        df = pd.DataFrame(
            np.random.randn(10, n_features),
            columns=detector.features
        )
        results = detector.predict_batch(df)
        print_pass(f"Batch predictions: {len(results)} records processed")
        print_pass(f"Fraud cases detected: {(results['prediction'] == 1).sum()}")
    except Exception as e:
        print_fail(f"Failed to make batch predictions: {e}")
        return False
    
    return True

def test_api():
    """Test Flask API endpoints."""
    print_header("Testing Flask API (Local)")
    
    try:
        from app import app
        app.config['TESTING'] = True
        client = app.test_client()
        print_pass("Flask app loaded")
    except Exception as e:
        print_fail(f"Failed to load Flask app: {e}")
        return False
    
    # Test health endpoint
    try:
        response = client.get('/health')
        if response.status_code == 200:
            print_pass("GET /health: 200 OK")
        else:
            print_fail(f"GET /health: {response.status_code}")
            return False
    except Exception as e:
        print_fail(f"Failed to test /health: {e}")
        return False
    
    # Test model info endpoint
    try:
        response = client.get('/model_info')
        if response.status_code == 200:
            data = json.loads(response.data)
            print_pass(f"GET /model_info: 200 OK ({len(data['features'])} features)")
        else:
            print_fail(f"GET /model_info: {response.status_code}")
            return False
    except Exception as e:
        print_fail(f"Failed to test /model_info: {e}")
        return False
    
    # Test features endpoint
    try:
        response = client.get('/features')
        if response.status_code == 200:
            data = json.loads(response.data)
            print_pass(f"GET /features: 200 OK ({data['feature_count']} features)")
        else:
            print_fail(f"GET /features: {response.status_code}")
            return False
    except Exception as e:
        print_fail(f"Failed to test /features: {e}")
        return False
    
    return True

def test_documentation():
    """Test if documentation exists."""
    print_header("Testing Documentation")
    
    docs = [
        ('README.md', 'README'),
        ('DEPLOYMENT_GUIDE.md', 'Deployment Guide'),
        ('requirements.txt', 'Requirements'),
        ('config.py', 'Configuration'),
        ('power_theft_detector.py', 'Detector Module'),
        ('app.py', 'Flask API'),
        ('Felo.ipynb', 'Analysis Notebook')
    ]
    
    all_exist = True
    for doc, name in docs:
        if Path(doc).exists():
            print_pass(f"{name}: {doc}")
        else:
            print_fail(f"{name}: {doc} NOT FOUND")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests."""
    print("\n")
    print_header("POWER THEFT DETECTION SYSTEM - DEPLOYMENT VERIFICATION")
    
    tests = [
        ("Imports", test_imports),
        ("Model Artifacts", test_model_artifacts),
        ("PowerTheftDetector", test_detector),
        ("Predictions", test_predictions),
        ("Flask API", test_api),
        ("Documentation", test_documentation)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print_fail(f"Test '{test_name}' failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {test_name:<30} {status}")
    
    print()
    status_msg = f"{Colors.GREEN}✓ READY FOR DEPLOYMENT{Colors.END}" if passed == total else f"{Colors.RED}✗ NOT READY{Colors.END}"
    print(f"Overall: {passed}/{total} tests passed - {status_msg}")
    
    if passed == total:
        print("\n" + Colors.GREEN + "="*80)
        print("✓ All verification tests passed!")
        print("✓ System is ready for production deployment")
        print("="*80 + Colors.END)
        return 0
    else:
        print("\n" + Colors.RED + "="*80)
        print("✗ Some tests failed")
        print("✗ Please fix the issues before deploying")
        print("="*80 + Colors.END)
        return 1

if __name__ == '__main__':
    sys.exit(main())
