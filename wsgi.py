"""
WSGI entry point for Student Performance Prediction System.
Used by Gunicorn (Render production server).
"""
import sys
import os
from pathlib import Path

# Add backend directory to Python path
BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

# Import the Flask app from backend
from app import app

if __name__ == "__main__":
    app.run()
