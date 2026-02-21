"""
Power Theft Detection - Production Prediction Module
====================================================
This module loads pre-trained models and scalers to make real-time
predictions on electricity consumption data for fraud detection.

Author: KPLC Data Science Team
Date: 2026-02-21
"""

import os
import json
import numpy as np
import pandas as pd
import joblib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('power_theft_detection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PowerTheftDetector:
    """
    Production-ready fraud detection system for KPLC power consumption data.
    
    Attributes:
        model_dir: Directory containing trained models and artifacts
        scaler: StandardScaler for feature normalization
        rf_model: Random Forest classifier for predictions
        lr_model: Logistic Regression model for comparison
        features: List of feature names used during training
        feature_importance: Feature importance scores from Random Forest
    """
    
    def __init__(self, model_dir: str = 'models_artifacts'):
        """
        Initialize the PowerTheftDetector by loading all artifacts.
        
        Parameters:
            model_dir (str): Path to directory containing saved models and artifacts
        """
        self.model_dir = Path(model_dir)
        self.scaler = None
        self.rf_model = None
        self.lr_model = None
        self.features = None
        self.feature_importance = {}
        self.is_initialized = False
        
        self._load_artifacts()
    
    def _load_artifacts(self) -> None:
        """Load all trained models, scalers, and feature metadata."""
        try:
            # Check if model directory exists
            if not self.model_dir.exists():
                raise FileNotFoundError(f"Model directory not found: {self.model_dir}")
            
            # Load scaler
            scaler_path = self.model_dir / 'scaler.joblib'
            self.scaler = joblib.load(scaler_path)
            logger.info(f"✓ Loaded scaler from {scaler_path}")
            
            # Load Random Forest model
            rf_path = self.model_dir / 'random_forest.joblib'
            self.rf_model = joblib.load(rf_path)
            logger.info(f"✓ Loaded Random Forest model from {rf_path}")
            
            # Load Logistic Regression model
            lr_path = self.model_dir / 'logistic_regression.joblib'
            self.lr_model = joblib.load(lr_path)
            logger.info(f"✓ Loaded Logistic Regression model from {lr_path}")
            
            # Load features list
            features_path = self.model_dir / 'features.json'
            with open(features_path, 'r') as f:
                self.features = json.load(f)
            logger.info(f"✓ Loaded {len(self.features)} features from {features_path}")
            
            # Extract feature importance
            if hasattr(self.rf_model, 'feature_importances_'):
                self.feature_importance = dict(zip(
                    self.features,
                    self.rf_model.feature_importances_
                ))
                # Sort by importance
                self.feature_importance = dict(sorted(
                    self.feature_importance.items(),
                    key=lambda x: x[1],
                    reverse=True
                ))
            
            self.is_initialized = True
            logger.info("✓ PowerTheftDetector initialized successfully")
            
        except Exception as e:
            logger.error(f"✗ Error loading artifacts: {str(e)}")
            raise
    
    def predict(self, data: Union[pd.DataFrame, np.ndarray], 
                use_model: str = 'random_forest') -> Tuple[np.ndarray, np.ndarray]:
        """
        Make fraud predictions on input data.
        
        Parameters:
            data (DataFrame or array): Input features (n_samples, n_features)
            use_model (str): Model to use ('random_forest' or 'logistic_regression')
        
        Returns:
            Tuple of (predictions, probabilities) where:
                - predictions: Binary class predictions (0=Normal, 1=Theft)
                - probabilities: Probability of fraud (0-1 confidence score)
        """
        if not self.is_initialized:
            raise RuntimeError("Detector not initialized. Load artifacts first.")
        
        # Convert to DataFrame if needed
        if isinstance(data, np.ndarray):
            if data.shape[1] != len(self.features):
                raise ValueError(f"Feature count mismatch: expected {len(self.features)}, got {data.shape[1]}")
            data = pd.DataFrame(data, columns=self.features)
        
        # Validate features
        missing_features = set(self.features) - set(data.columns)
        if missing_features:
            raise ValueError(f"Missing required features: {missing_features}")
        
        # Select and scale features
        X = data[self.features].copy()
        X_scaled = self.scaler.transform(X)
        
        # Select model
        if use_model.lower() == 'random_forest':
            model = self.rf_model
            predictions = model.predict(X)
            probabilities = model.predict_proba(X)[:, 1]
        elif use_model.lower() == 'logistic_regression':
            model = self.lr_model
            predictions = model.predict(X_scaled)
            probabilities = model.predict_proba(X_scaled)[:, 1]
        else:
            raise ValueError(f"Unknown model: {use_model}. Use 'random_forest' or 'logistic_regression'")
        
        return predictions, probabilities
    
    def predict_batch(self, data: pd.DataFrame, 
                      threshold: float = 0.5) -> pd.DataFrame:
        """
        Score multiple records and return detailed results.
        
        Parameters:
            data (DataFrame): Input features with optional 'meter_id' column
            threshold (float): Classification threshold (default: 0.5)
        
        Returns:
            DataFrame with columns: meter_id, prediction, fraud_probability, risk_level
        """
        predictions, probabilities = self.predict(data)
        
        results = pd.DataFrame({
            'prediction': predictions,
            'fraud_probability': probabilities,
            'threshold': threshold
        })
        
        # Add risk level
        results['risk_level'] = pd.cut(
            probabilities,
            bins=[0, 0.3, 0.7, 1.0],
            labels=['Low', 'Medium', 'High'],
            include_lowest=True
        )
        
        # Add meter_id if present in input
        if 'meter_id' in data.columns:
            results.insert(0, 'meter_id', data['meter_id'].values)
        
        # Add timestamp
        results['prediction_timestamp'] = datetime.now().isoformat()
        
        return results
    
    def get_top_features(self, n: int = 10) -> pd.DataFrame:
        """
        Get top N most important features for fraud detection.
        
        Parameters:
            n (int): Number of top features to return
        
        Returns:
            DataFrame with feature names and importance scores
        """
        top_features = list(self.feature_importance.items())[:n]
        df = pd.DataFrame(top_features, columns=['Feature', 'Importance'])
        df['Importance_Percent'] = (df['Importance'] * 100).round(2)
        return df
    
    def get_model_info(self) -> Dict:
        """Get metadata about the trained models."""
        return {
            'random_forest': {
                'n_estimators': self.rf_model.n_estimators,
                'max_depth': self.rf_model.max_depth,
                'feature_count': len(self.features)
            },
            'logistic_regression': {
                'solver': self.lr_model.solver,
                'max_iter': self.lr_model.max_iter,
                'feature_count': len(self.features)
            },
            'scaler_type': type(self.scaler).__name__,
            'features': self.features,
            'loaded_at': datetime.now().isoformat()
        }


def load_detector(model_dir: str = 'models_artifacts') -> PowerTheftDetector:
    """
    Convenience function to load the PowerTheftDetector.
    
    Parameters:
        model_dir (str): Path to model artifacts directory
    
    Returns:
        Initialized PowerTheftDetector instance
    """
    return PowerTheftDetector(model_dir)


if __name__ == '__main__':
    # Example usage
    detector = load_detector()
    
    # Show model info
    print("\n" + "="*80)
    print("MODEL INFORMATION")
    print("="*80)
    info = detector.get_model_info()
    print(json.dumps(info, indent=2))
    
    # Show top features
    print("\n" + "="*80)
    print("TOP 10 MOST IMPORTANT FEATURES")
    print("="*80)
    print(detector.get_top_features(10).to_string(index=False))
    
    print("\n✓ PowerTheftDetector ready for predictions")
