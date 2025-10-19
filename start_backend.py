#!/usr/bin/env python3
"""
Startup script for Action Anticipation API
Handles model file setup and server startup
"""

import os
import sys
import shutil
from pathlib import Path

def setup_model_files():
    #  this function checks if the dist directory exists and if the model files are present
    print("Checking model files...")
    
    # Check for model files in dist directory
    dist_dir = Path("dist")
    model_files = {
        dist_dir / "action_anticipation_model.onnx": "ONNX model file",
        dist_dir / "model_info.json": "Model info JSON file"
    }
    
    missing_files = []
    
    for filepath, description in model_files.items():
        if filepath.exists():
            print(f"   Found: {description}: {filepath}")
        else:
            missing_files.append(str(filepath))
            print(f"   Missing: {filepath}")
    
    if missing_files:
        print(f"\nMissing files in dist/ folder!")
        print("   Required files:")
        print("   - dist/action_anticipation_model.onnx")
        print("   - dist/model_info.json")
        return False
    
    print("   All model files ready!")
    return True

def check_dependencies():
    #  this function checks if the required packages are installed
    print("\nChecking dependencies...")
    
    required_packages = [
        "fastapi",
        "uvicorn", 
        "onnxruntime",
        "numpy",
        "pandas"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   Found: {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   Missing: {package}")
    
    if missing_packages:
        print(f"\nMissing packages: {missing_packages}")
        print("   Install with: pip install -r requirements_backend.txt")
        return False
    
    print("   All dependencies ready!")
    return True

def start_server():
    #  this function starts the FastAPI server
    print("\nStarting Action Anticipation API...")
    
    # Add src directory to Python path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
    
    # Import and run server
    try:
        import uvicorn
        
        print("   Server will be available at: http://localhost:8001")
        print("   API docs at: http://localhost:8001/docs")
        print("   Press Ctrl+C to stop the server")
        print("\n" + "="*50)
        
        uvicorn.run(
            "src.server:app",
            host="0.0.0.0",
            port=8001,
            reload=True
        )
        
    except ImportError as e:
        print(f"   Import error: {e}")
        print("   Make sure all dependencies are installed")
    except Exception as e:
        print(f"   Server error: {e}")

def main():
    #  this function is the main startup function
    print("Action Anticipation API Startup")
    print("=" * 50)
    
    # Setup model files
    if not setup_model_files():
        return
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
