"""
Student Performance Prediction System - Backend API Server (Flask)
===================================================================
Production-grade Flask server integrating the trained Machine Learning
model and preprocessing pipeline with the frontend dashboard.
"""

import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure backend directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from predictor import predict_student, get_predictor

# Flask CORS Support
try:
    from flask_cors import CORS
    has_cors = True
except ImportError:
    has_cors = False

FRONTEND_DIR = BASE_DIR.parent / "frontend"

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
if has_cors:
    CORS(app, resources={r"/api/*": {"origins": "*"}})

# ==============================================================================
# STATIC & FRONTEND ROUTING
# ==============================================================================
@app.route("/")
def index():
    return send_from_directory(str(FRONTEND_DIR), "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(str(FRONTEND_DIR), path)

# ==============================================================================
# API ENDPOINTS
# ==============================================================================
@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint to report API status and loaded ML model."""
    try:
        predictor = get_predictor()
        model_name = predictor.metadata.get("model_name", "LogisticRegression") if predictor.metadata else "Loaded"
        accuracy = predictor.metadata.get("metrics", {}).get("accuracy", 0.85) if predictor.metadata else 0.85
        return jsonify({
            "status": "online",
            "service": "Student Performance Prediction API",
            "model_status": "Loaded and Ready",
            "model_name": model_name,
            "accuracy": accuracy
        }), 200
    except Exception as e:
        return jsonify({
            "status": "degraded",
            "error": str(e)
        }), 500

@app.route("/api/model-info", methods=["GET"])
def model_info():
    """Returns trained ML model metadata, evaluation metrics, and feature importances."""
    try:
        predictor = get_predictor()
        if predictor.metadata:
            return jsonify({"status": "success", "data": predictor.metadata}), 200
        return jsonify({"status": "error", "message": "Metadata not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/predict", methods=["POST"])
def predict():
    """
    Primary Prediction Endpoint.
    Receives student academic and behavioral factors, applies preprocessing,
    invokes the trained ML model, and returns Pass/Fail result with diagnostics.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({
                "status": "error",
                "message": "Invalid request payload. Expected JSON object with student metrics."
            }), 400

        # Extract features with flexible key names (snake_case or camelCase)
        study_hours = data.get("study_hours", data.get("studyHours"))
        attendance = data.get("attendance")
        previous_score = data.get("previous_score", data.get("previousScore"))
        assignments_completed = data.get("assignments_completed", data.get("assignmentsCompleted"))
        participation = data.get("participation")
        sleep_hours = data.get("sleep_hours", data.get("sleepHours"))

        # Validation: Check for required fields
        required_fields = {
            "study_hours": study_hours,
            "attendance": attendance,
            "previous_score": previous_score,
            "assignments_completed": assignments_completed,
            "participation": participation,
            "sleep_hours": sleep_hours
        }

        missing = [k for k, v in required_fields.items() if v is None or v == ""]
        if missing:
            return jsonify({
                "status": "error",
                "message": f"Missing required fields: {', '.join(missing)}"
            }), 400

        # Type validation & range bounds
        try:
            cleaned_data = {
                "study_hours": float(study_hours),
                "attendance": float(attendance),
                "previous_score": float(previous_score),
                "assignments_completed": float(assignments_completed),
                "participation": participation,
                "sleep_hours": float(sleep_hours)
            }
        except (ValueError, TypeError) as e:
            return jsonify({
                "status": "error",
                "message": f"Invalid numeric value provided: {str(e)}"
            }), 400

        # Validate realistic ranges
        if not (0 <= cleaned_data["study_hours"] <= 24):
            return jsonify({"status": "error", "message": "Study hours must be between 0 and 24"}), 400
        if not (0 <= cleaned_data["attendance"] <= 100):
            return jsonify({"status": "error", "message": "Attendance must be between 0 and 100%"}), 400
        if not (0 <= cleaned_data["previous_score"] <= 100):
            return jsonify({"status": "error", "message": "Previous score must be between 0 and 100"}), 400
        if not (0 <= cleaned_data["assignments_completed"] <= 50):
            return jsonify({"status": "error", "message": "Assignments completed must be between 0 and 50"}), 400
        if not (0 <= cleaned_data["sleep_hours"] <= 24):
            return jsonify({"status": "error", "message": "Sleep hours must be between 0 and 24"}), 400

        # Run inference through ML pipeline
        result = predict_student(cleaned_data)
        
        response_payload = {
            "status": "success",
            "prediction": result["prediction"],
            "confidence": result["confidence"],
            "confidence_percentage": result.get("confidence_percentage", round(result["confidence"] * 100, 1)),
            "probabilities": result["probabilities"],
            "summary": result["summary"],
            "areas_to_improve": result["areas_to_improve"],
            "personalized_suggestions": result["personalized_suggestions"],
            "model_used": result["model_used"],
            "student_inputs": cleaned_data
        }

        return jsonify(response_payload), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server error during prediction: {str(e)}"
        }), 500

# ==============================================================================
# SERVER ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[+] Starting Student Performance Prediction Server on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)

