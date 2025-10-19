# Ballet Action Anticipation

A machine learning system that predicts next ballet movements from video sequences using GRU and Transformer neural networks trained on the AnnChor dataset.

## Project Structure

```
action-anticipation-annchor/
├── src/                    # Source code files
├── dist/                   # Executable files and models
├── data/                   # Sample videos and dataset info
└── ss/                     # Project presentation
```

## Quick Start

### Option 1: Using Executable Scripts

**On macOS/Linux:**

```bash
./dist/run_demo.sh
```

**On Windows:**

```cmd
.\dist\run_demo.bat
```

### Option 2: Manual Setup

1. **Install Python Dependencies:**

```bash
pip install -r requirements_backend.txt
```

2. **Start Backend Server:**

```bash
source venv/bin/activate
python start_backend.py
```

3. **Start Frontend (in new terminal):**

```bash
cd frontend
npm install
npm run dev
```

## Usage

1. Open http://localhost:3000 in your browser
2. Upload a ballet video file (MP4, AVI, MOV, MKV, WebM)
3. Switch between GRU and Transformer models to compare predictions
4. View continuous predictions for different time segments

## API Endpoints

- **Backend API:** http://localhost:8001
- **API Documentation:** http://localhost:8001/docs
- **Health Check:** http://localhost:8001/health

## Models

- **GRU Model:** 66.88% accuracy, 22.6 MB
- **Transformer Model:** 52.57% accuracy, 30.0 MB
- **Input:** 10 frames × 2048 features
- **Output:** 11 ballet action classes

## Dataset

**AnnChor Dataset:** https://github.com/dvanderhaar/UJAnnChor

- 1,020 ballet performance videos
- 11 action classes (Pirouette, Grand Jeté, Arabesque, etc.)
- Pre-extracted I3D RGB features

## Requirements

- Python 3.9+
- Node.js 16+
- 2GB RAM minimum
- 100MB disk space

## Troubleshooting

**Model files not found:**

- Ensure `dist/` directory contains both ONNX model files

**Port already in use:**

- Backend uses port 8001, frontend uses port 3000
- Change ports in `start_backend.py` and `frontend/package.json` if needed

**Dependencies issues:**

- Use virtual environment: `python -m venv venv && source venv/bin/activate`
- Install requirements: `pip install -r requirements_backend.txt`
