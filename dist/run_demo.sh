#!/bin/bash

# Action Anticipation Demo Runner
# This script starts the complete application for demonstration

echo "=========================================="
echo "  Ballet Action Anticipation Demo"
echo "  Using GRU and Transformer Models"
echo "=========================================="
echo ""

# checks if the script is being run from the correct directory
if [ ! -f "../src/server.py" ]; then
    echo "Error: Please run this script from the project root directory"
    echo "   Usage: cd /path/to/action-anticipation-annchor && ./dist/run_demo.sh"
    exit 1
fi

# checks if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# checks if the virtual environment exists
if [ ! -d "../venv" ]; then
    echo "Error: Virtual environment not found"
    echo "   Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements_backend.txt"
    exit 1
fi

# checks if the model files exist
if [ ! -f "action_anticipation_model.onnx" ] || [ ! -f "transformer_model.onnx" ]; then
    echo "Error: Model files not found in dist/ directory"
    echo "   Required files: action_anticipation_model.onnx, transformer_model.onnx"
    exit 1
fi

echo "All checks passed!"

# activates the virtual environment
echo "Activating virtual environment..."
source ../venv/bin/activate

# checks if the dependencies are installed
echo "Checking dependencies..."
pip install -q -r ../requirements_backend.txt

# starts the application
echo "Starting the application..."
echo "Backend API will be available at: http://localhost:8001"
echo "Frontend will be available at: http://localhost:3000"
echo "API Documentation: http://localhost:8001/docs"
echo ""
echo "Switch between GRU and Transformer models to compare results"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# starts the backend server
echo "Starting backend server..."
cd .. && python start_backend.py
