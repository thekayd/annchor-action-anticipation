@echo off
REM Action Anticipation Demo Runner for Windows
REM This script starts the complete application for demonstration

echo ==========================================
echo   Ballet Action Anticipation Demo
echo   Using GRU and Transformer Models
echo ==========================================
echo.

REM checks if the script is being run from the correct directory
if not exist "..\src\server.py" (
    echo Error: Please run this script from the project root directory
    echo    Usage: cd C:\path\to\action-anticipation-annchor & .\dist\run_demo.bat
    pause
    exit /b 1
)

REM checks if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM checks if the virtual environment exists
if not exist "..\venv" (
    echo Error: Virtual environment not found
    echo    Please run: python -m venv venv ^&^& venv\Scripts\activate ^&^& pip install -r requirements_backend.txt
    pause
    exit /b 1
)

REM checks if the model files exist
if not exist "action_anticipation_model.onnx" (
    echo Error: GRU model file not found
    pause
    exit /b 1
)

if not exist "transformer_model.onnx" (
    echo Error: Transformer model file not found
    pause
    exit /b 1
)

echo All checks passed!
echo.

REM activates the virtual environment
echo Activating virtual environment...
call ..\venv\Scripts\activate.bat

REM checks if the dependencies are installed
echo Checking dependencies...
pip install -q -r ..\requirements_backend.txt

echo.
echo Starting the application...
echo.
echo Backend API will be available at: http://localhost:8001
echo Frontend will be available at: http://localhost:3000
echo API Documentation: http://localhost:8001/docs
echo.
echo Switch between GRU and Transformer models to compare results
echo.
echo Press Ctrl+C to stop the application
echo.

REM starts the backend server
echo Starting backend server...
cd ..
python start_backend.py
