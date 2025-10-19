"""
ONNX Model Loader for Action Anticipation
Loads the trained model and handles predictions
"""

import onnxruntime as ort
import numpy as np
import json
import os
from typing import Dict, List, Tuple

class ActionAnticipationModel:
    # this class loads and runs the ONNX model for action anticipation
    
    def __init__(self, model_path: str, model_info_path: str):
        # this function initializes the model loader with the model file paths
        self.model_path = model_path
        self.model_info_path = model_info_path
        
        # loads the model information
        self._load_model_info()
        
        # loads the ONNX model
        self._load_model()
        
        print(f"Model loaded successfully!")
        print(f"   Model: {model_path}")
        print(f"   Classes: {len(self.class_names)}")
        print(f"   Input shape: {self.input_shape}")
    
    def _load_model_info(self):
        # this function loads the model information from a JSON file
        try:
            with open(self.model_info_path, 'r') as f:
                self.info = json.load(f)
            
            self.class_names = self.info['class_names']
            self.input_shape = self.info['input_shape']
            self.num_classes = self.info['num_classes']
            self.accuracy = self.info.get('accuracy', 0)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Model info file not found: {self.model_info_path}")
        except Exception as e:
            raise Exception(f"Error loading model info: {e}")
    
    def _load_model(self):
        # this function loads the ONNX model file
        try:
            # this creates the ONNX runtime session
            self.session = ort.InferenceSession(self.model_path)
            
            # gets the input and output names
            self.input_name = self.session.get_inputs()[0].name
            self.output_name = self.session.get_outputs()[0].name
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        except Exception as e:
            raise Exception(f"Error loading ONNX model: {e}")
    
    def predict(self, features: np.ndarray) -> Dict:
        # this function predicts the action from I3D features
        try:
            # this checks if the input shape is correct
            expected_shape = tuple(self.input_shape)
            if features.shape != expected_shape:
                raise ValueError(f"Expected shape {expected_shape}, got {features.shape}")
            
            # this makes sure the data type is correct
            features = features.astype(np.float32)
            
            # runs the model to get predictions
            result = self.session.run(
                [self.output_name], 
                {self.input_name: features}
            )
            
            predictions = result[0][0]  # this gets the first sample
            
            # this finds the best prediction
            action_id = np.argmax(predictions)
            confidence = float(np.max(predictions))
            
            # this gets the top 5 predictions
            top5_indices = np.argsort(predictions)[-5:][::-1]
            top5_predictions = [
                {
                    'action_id': int(idx),
                    'action_name': self.class_names[idx],
                    'confidence': float(predictions[idx])
                }
                for idx in top5_indices
            ]
            
            # this returns the predictions
            return {
                'top_prediction': {
                    'action_id': int(action_id),
                    'action_name': self.class_names[action_id],
                    'confidence': confidence
                },
                'top5_predictions': top5_predictions,
                'all_predictions': predictions.tolist(),
                'model_info': {
                    'accuracy': self.accuracy,
                    'input_shape': self.input_shape,
                    'num_classes': self.num_classes
                }
            }
            
        except Exception as e:
            raise Exception(f"Error during prediction: {e}")
    
    def get_model_info(self) -> Dict:
        # this function returns information about the model
        return {
            'class_names': self.class_names,
            'input_shape': self.input_shape,
            'num_classes': self.num_classes,
            'accuracy': self.accuracy,
            'model_path': self.model_path
        }
    
    def health_check(self) -> bool:
        # this function checks if the model is working properly
        try:
            # this creates some random input to test the model
            dummy_input = np.random.randn(*self.input_shape).astype(np.float32)
            result = self.predict(dummy_input)
            return True
        except Exception as e:
            print(f"Health check failed: {e}")
            return False

