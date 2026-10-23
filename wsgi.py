"""
WSGI entry point for Student Performance Prediction System.
Used by Gunicorn (Render production server).
"""
import sys
import os
from pathlib import Path

# Add backend directory to Python path so 'from app import app' works
BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

# Also set PYTHONPATH env var for subprocesses
os.environ.setdefault("PYTHONPATH", str(BACKEND_DIR))

# Import the Flask app from backend
try:
    from app import app
except ImportError as e:
    raise ImportError(
        f"Failed to import Flask app from backend/app.py. "
        f"BACKEND_DIR={BACKEND_DIR}, sys.path={sys.path[:3]}. "
        f"Original error: {e}"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
