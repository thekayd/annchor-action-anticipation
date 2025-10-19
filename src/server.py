"""
FastAPI Server for Action Anticipation
Provides API endpoints for the frontend to call
"""

from fastapi import FastAPI, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import numpy as np
import cv2
import os
import sys

# Add src directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model_loader import ActionAnticipationModel
from video_processor import VideoProcessor

# Initialize FastAPI app
app = FastAPI(
    title="Action Anticipation API",
    description="API for predicting next ballet actions from I3D features",
    version="1.0.0"
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model and video processor variables
model_gru = None
model_transformer = None
video_processor = None

# Pydantic models for request/response
class PredictionRequest(BaseModel):
    # this class defines what data we need for making predictions
    features: List[List[float]]  # Shape: (10, 2048)
    
    class Config:
        schema_extra = {
            "example": {
                "features": [[0.1] * 2048] * 10  # Example with 10 time steps, 2048 features each
            }
        }

class PredictionResponse(BaseModel):
    # this class defines what data we send back after making predictions
    top_prediction: Dict[str, Any]
    top5_predictions: List[Dict[str, Any]]
    all_predictions: List[float]
    model_info: Dict[str, Any]

class HealthResponse(BaseModel):
    # this class defines what data we send back for health checks
    status: str
    model_loaded: bool
    model_info: Dict[str, Any] = None

# Startup event
@app.on_event("startup")
async def startup_event():
    # this function loads the models when the server starts up
    global model_gru, model_transformer, video_processor
    
    try:
        # Get current working directory
        cwd = os.getcwd()
        print(f"Current working directory: {cwd}")
        
        # Paths to model files (in dist folder)
        gru_model_path = "dist/action_anticipation_model.onnx"
        gru_info_path = "dist/model_info.json"
        transformer_model_path = "dist/transformer_model.onnx"
        transformer_info_path = "dist/transformer_info.json"
        
        print("Loading GRU model...")
        print(f"   Model: {os.path.abspath(gru_model_path)}")
        print(f"   Info: {os.path.abspath(gru_info_path)}")
        
        # this checks if the GRU model files exist
        if not os.path.exists(gru_model_path):
            raise FileNotFoundError(f"GRU model not found: {gru_model_path}")
        if not os.path.exists(gru_info_path):
            raise FileNotFoundError(f"GRU info not found: {gru_info_path}")
        
        # this loads the GRU model
        model_gru = ActionAnticipationModel(gru_model_path, gru_info_path)
        print(f"   GRU loaded: {model_gru.accuracy}% accuracy")
        
        # this then loads the Transformer model if it exists
        if os.path.exists(transformer_model_path) and os.path.exists(transformer_info_path):
            print("\nLoading Transformer model...")
            print(f"   Model: {os.path.abspath(transformer_model_path)}")
            print(f"   Info: {os.path.abspath(transformer_info_path)}")
            model_transformer = ActionAnticipationModel(transformer_model_path, transformer_info_path)
            print(f"   Transformer loaded: {model_transformer.accuracy}% accuracy")
        else:
            print("\nTransformer model not found (optional)")
            model_transformer = None
        
        # create the video processor
        video_processor = VideoProcessor(target_frames=10, feature_dim=2048)
        
        # this tests if the GRU model is working properly
        if not model_gru.health_check():
            raise Exception("GRU model health check failed")
        
        # this tests if the Transformer model is working, if we loaded it
        if model_transformer and not model_transformer.health_check():
            raise Exception("Transformer model health check failed")
            
        print("\nAction Anticipation API started successfully!")
        print(f"   GRU Model: {model_gru.accuracy}% accuracy")
        if model_transformer:
            print(f"   Transformer Model: {model_transformer.accuracy}% accuracy")
        print(f"   Classes: {len(model_gru.class_names)}")
        print(f"   Video processor initialized")
        
    except Exception as e:
        print(f"Failed to load model: {e}")
        import traceback
        traceback.print_exc()
        model = None

# API Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    # this is the main page of the API
    return {
        "message": "Action Anticipation API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    # this function checks if the server and models are working
    if model_gru is None:
        return HealthResponse(
            status="unhealthy",
            model_loaded=False
        )
    
    # Test model
    is_healthy = model_gru.health_check()
    
    return HealthResponse(
        status="healthy" if is_healthy else "unhealthy",
        model_loaded=True,
        model_info=model_gru.get_model_info() if is_healthy else None
    )

@app.get("/classes", response_model=Dict[str, List[str]])
async def get_classes():
    # this function returns a list of all the action classes the model can predict
    if model_gru is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    return {"classes": model_gru.class_names}

@app.get("/model-info", response_model=Dict[str, Any])
async def get_model_info():
    # this function returns information about the model
    if model_gru is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    return model_gru.get_model_info()

@app.get("/models-comparison", response_model=Dict[str, Any])
async def get_models_comparison():
    # this function compares the two models and shows which one is better
    if model_gru is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Models not loaded"
        )
    
    comparison = {
        "pipeline_1": {
            "name": "GRU",
            "accuracy": model_gru.accuracy,
            "description": "Recurrent Neural Network with sequential processing"
        }
    }
    
    if model_transformer:
        comparison["pipeline_2"] = {
            "name": "Transformer",
            "accuracy": model_transformer.accuracy,
            "description": "Attention-based architecture with parallel processing"
        }
        comparison["winner"] = "GRU" if model_gru.accuracy > model_transformer.accuracy else "Transformer"
        comparison["difference"] = abs(model_gru.accuracy - model_transformer.accuracy)
    
    return comparison

@app.post("/predict", response_model=PredictionResponse)
async def predict_action(request: PredictionRequest, model_type: str = "gru"):
    # this function makes predictions using the features from a video
    # this chooses which model to use which is the GRU model by default
    if model_type.lower() == "transformer" and model_transformer:
        model = model_transformer
    else:
        model = model_gru
    
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    try:
        # converts the features to a numpy array
        features_array = np.array(request.features, dtype=np.float32)
        
        # adds a batch dimension if needed
        if features_array.shape == (10, 2048):
            features_array = features_array.reshape(1, 10, 2048)
        
        # check if the shape is correct
        expected_shape = tuple(model.input_shape)
        if features_array.shape != expected_shape:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Expected shape {expected_shape}, got {features_array.shape}"
            )
        
        # this then makes the prediction
        result = model.predict(features_array)
        
        return PredictionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )

@app.post("/predict-batch", response_model=List[PredictionResponse])
async def predict_batch(requests: List[PredictionRequest], model_type: str = "gru"):
    # this function makes predictions for multiple videos at once
    # choose which model to use
    if model_type.lower() == "transformer" and model_transformer:
        model = model_transformer
    else:
        model = model_gru
    
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    try:
        results = []
        
        for request in requests:
            # convert the features to a numpy array
            features_array = np.array(request.features, dtype=np.float32)
            
            # add a batch dimension if needed
            if features_array.shape == (10, 2048):
                features_array = features_array.reshape(1, 10, 2048)
            
            # check if the shape is correct
            expected_shape = tuple(model.input_shape)
            if features_array.shape != expected_shape:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Expected shape {expected_shape}, got {features_array.shape}"
                )
            
            # make the prediction
            result = model.predict(features_array)
            results.append(PredictionResponse(**result))
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {str(e)}"
        )

@app.post("/predict-continuous")
async def predict_continuous(file: UploadFile = File(...), model_type: str = "gru"):
    # this function analyzes a video and makes predictions every 10 seconds
    # this chooses which model to use which is the GRU model by default
    if model_type.lower() == "transformer" and model_transformer:
        model = model_transformer
    else:
        model = model_gru
    
    if model is None or video_processor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model or video processor not loaded"
        )
    
    temp_path = None
    
    try:
        print(f"Processing video for continuous predictions: {file.filename}")
        
        # Read and save video
        content = await file.read()
        file_ext = os.path.splitext(file.filename)[1].lower()
        temp_path = video_processor.save_temp_video(content, suffix=file_ext)
        
        # Get video duration
        cap = cv2.VideoCapture(temp_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        cap.release()
        
        print(f"   Video duration: {duration:.1f}s")
        
        # Generate predictions every 10 seconds
        predictions = []
        current_time = 0
        
        while current_time < duration - 10:  # Need at least 10 seconds
            print(f"   Analyzing segment: {current_time}s - {current_time + 10}s")
            
            # Extract features from this 10-second segment
            features = video_processor.extract_features_from_video_segment(
                temp_path, 
                start_time=current_time, 
                duration=10
            )
            
            # Reshape and predict
            features = features.reshape(1, 10, 2048).astype(np.float32)
            result = model.predict(features)
            
            # Add timestamp to result
            result['timestamp'] = current_time
            result['segment'] = f"{current_time}s - {current_time + 10}s"
            predictions.append(result)
            
            # Move to next segment
            current_time += 10
        
        print(f"   Generated {len(predictions)} predictions")
        
        return {
            "video_duration": duration,
            "num_predictions": len(predictions),
            "predictions": predictions
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed: {str(e)}"
        )
    finally:
        if temp_path:
            video_processor.cleanup_temp_file(temp_path)

@app.post("/predict-from-video", response_model=PredictionResponse)
async def predict_from_video(file: UploadFile = File(...), model_type: str = "gru"):
    # this function takes a video file and predicts what action is happening
    # this chooses which model to use which is the GRU model by default
    if model_type.lower() == "transformer" and model_transformer:
        model = model_transformer
    else:
        model = model_gru
    
    if model is None or video_processor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model or video processor not loaded"
        )
    
    temp_path = None
    
    try:
        # Validate file type
        allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        print(f"Processing video: {file.filename}")
        
        # this reads the video file content
        content = await file.read()
        
        # this saves         the video to a temporary file
        temp_path = video_processor.save_temp_video(content, suffix=file_ext)
        
        print(f"   Extracting features from video...")
        
        # gets the I3D features from the video
        features = video_processor.extract_features_from_video(temp_path)
        
        print(f"   Features extracted: {features.shape}")
        
        # adds a batch dimension to the features
        features = features.reshape(1, 10, 2048).astype(np.float32)
        
        # make the prediction
        result = model.predict(features)
        
        print(f"   Prediction: {result['top_prediction']['action_name']}")
        
        return PredictionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video processing failed: {str(e)}"
        )
    finally:
        # Cleanup temporary file
        if temp_path:
            video_processor.cleanup_temp_file(temp_path)

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "status": 404}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "status": 500}

if __name__ == "__main__":
    import uvicorn
    
    print("Starting Action Anticipation API...")
    print("   Server will be available at: http://localhost:8001")
    print("   API docs at: http://localhost:8001/docs")
    
    uvicorn.run(
        "src.server:app", 
        host="0.0.0.0", 
        port=8001,  # Changed to port 8001
        reload=True  # Auto-reload on code changes
    )
