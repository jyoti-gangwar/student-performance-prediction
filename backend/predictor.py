"""
Student Performance Prediction Pipeline - Inference Module
===========================================================
This module loads the trained ML model and scaler artifacts,
processes raw student input parameters, generates the Pass/Fail
prediction with confidence probabilities, diagnoses weak factors,
and crafts personalized improvement recommendations.
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

MODEL_DIR = Path(__file__).resolve().parent / "model"
MODEL_PATH = MODEL_DIR / "student_model.joblib"
SCALER_PATH = MODEL_DIR / "scaler.joblib"
METADATA_PATH = MODEL_DIR / "model_metadata.json"

class StudentPerformancePredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.metadata = None
        self._load_artifacts()

    def _load_artifacts(self):
        if not MODEL_PATH.exists() or not SCALER_PATH.exists():
            raise FileNotFoundError("Model artifacts not found. Run backend/train_model.py first.")
        
        self.model = joblib.load(MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)
        
        if METADATA_PATH.exists():
            with open(METADATA_PATH, "r") as f:
                self.metadata = json.load(f)

    @staticmethod
    def _parse_participation(val):
        """Map text or numeric participation input into standard 1-10 integer rating."""
        if isinstance(val, (int, float)):
            return float(np.clip(val, 1, 10))
        
        val_str = str(val).strip().lower()
        mapping = {
            'high': 9,
            'medium': 5,
            'low': 2
        }
        return mapping.get(val_str, 5)

    def predict(self, student_data: dict) -> dict:
        """
        Predict Pass/Fail outcome based on student inputs.
        
        Expected keys in student_data:
        - study_hours (float, e.g. 5.5)
        - attendance (float/int, e.g. 85)
        - previous_score (float/int, e.g. 70)
        - assignments_completed (float/int, e.g. 8)
        - participation (string 'High'|'Medium'|'Low' or float 1-10)
        - sleep_hours (float, e.g. 7.0)
        """
        # 1. Extract and sanitize inputs
        study_hours = float(student_data.get("study_hours", 0))
        attendance = float(student_data.get("attendance", 0))
        previous_score = float(student_data.get("previous_score", 0))
        assignments_completed = float(student_data.get("assignments_completed", 0))
        participation_val = self._parse_participation(student_data.get("participation", "Medium"))
        sleep_hours = float(student_data.get("sleep_hours", 7.0))

        # 2. Form numerical feature DataFrame in the exact training order
        feature_names = [
            'Study_Hours',
            'Attendance',
            'Previous_Score',
            'Assignments_Completed',
            'Participation',
            'Sleep_Hours'
        ]
        
        raw_df = pd.DataFrame([{
            'Study_Hours': study_hours,
            'Attendance': attendance,
            'Previous_Score': previous_score,
            'Assignments_Completed': assignments_completed,
            'Participation': participation_val,
            'Sleep_Hours': sleep_hours
        }], columns=feature_names)

        # 3. Apply Standard Scaler
        scaled_features = self.scaler.transform(raw_df)

        # 4. Generate Model Prediction & Probability
        pred_class = int(self.model.predict(scaled_features)[0])
        probabilities = self.model.predict_proba(scaled_features)[0]
        
        prob_fail = float(probabilities[0])
        prob_pass = float(probabilities[1])

        prediction_label = "Pass" if pred_class == 1 else "Fail"
        confidence = prob_pass if pred_class == 1 else prob_fail

        # 5. Diagnostic Analysis - Identify Improvement Areas
        areas_to_improve = []
        suggestions = []

        # Attendance check
        if attendance < 75:
            severity = "critical" if attendance < 60 else "moderate"
            areas_to_improve.append({
                "title": f"Attendance Below Optimal ({attendance:.0f}%)",
                "description": "Class attendance is a key indicator for academic retention and final evaluation.",
                "severity": severity
            })
            suggestions.append({
                "icon": "[Attendance]",
                "title": "Boost Class Attendance",
                "description": "Aim for at least 80% attendance by prioritizing lecture schedules and avoiding unexcused absences."
            })

        # Study hours check
        if study_hours < 4.5:
            severity = "critical" if study_hours < 2.5 else "moderate"
            areas_to_improve.append({
                "title": f"Study Duration Deficit ({study_hours:.1f} hrs/day)",
                "description": "Daily study time is currently below the class cohort average (4.98 hrs/day).",
                "severity": severity
            })
            suggestions.append({
                "icon": "[Study]",
                "title": "Establish Structured Study Blocks",
                "description": "Dedicate at least 2 structured 90-minute focused study sessions per day using active recall techniques."
            })

        # Previous Score check
        if previous_score < 55:
            severity = "critical" if previous_score < 40 else "moderate"
            areas_to_improve.append({
                "title": f"Previous Exam Foundation ({previous_score:.0f}/100)",
                "description": "Prior test performance shows foundational concept gaps that require targeted revision.",
                "severity": severity
            })
            suggestions.append({
                "icon": "[Score]",
                "title": "Targeted Revision on Weak Subjects",
                "description": "Consult course tutors and solve past exam question banks to strengthen core subject topics."
            })

        # Assignments check
        if assignments_completed < 6:
            severity = "critical" if assignments_completed < 4 else "moderate"
            areas_to_improve.append({
                "title": f"Low Assignment Completion ({assignments_completed:.0f} completed)",
                "description": "Assignment submissions directly impact continuous internal assessment and practical mastery.",
                "severity": severity
            })
            suggestions.append({
                "icon": "[Assignment]",
                "title": "Timely Assignment Submission",
                "description": "Break larger homework projects into smaller daily milestones to ensure on-time delivery."
            })

        # Participation check
        if participation_val < 5.0:
            areas_to_improve.append({
                "title": "Low Classroom Engagement",
                "description": "Active in-class participation reinforces conceptual clarity and instructor feedback.",
                "severity": "moderate"
            })
            suggestions.append({
                "icon": "[Participation]",
                "title": "Increase Classroom Engagement",
                "description": "Participate actively in lab discussions, ask questions, and collaborate in peer study groups."
            })

        # Sleep check
        if sleep_hours < 6.0 or sleep_hours > 9.0:
            areas_to_improve.append({
                "title": f"Irregular Sleep Schedule ({sleep_hours:.1f} hrs/night)",
                "description": "Optimal cognitive focus and memory consolidation require 7 to 8 hours of consistent rest.",
                "severity": "moderate"
            })
            suggestions.append({
                "icon": "[Sleep]",
                "title": "Optimize Sleep Hygiene",
                "description": "Maintain a regular 7-8 hour sleep schedule to improve mental stamina during lectures and exams."
            })

        # If everything is high/optimal
        if len(areas_to_improve) == 0:
            areas_to_improve.append({
                "title": "All Academic Metrics in Optimal Range",
                "description": "The student maintains strong study consistency, high attendance, and active participation.",
                "severity": "optimal"
            })
            suggestions.append({
                "icon": "[Optimal]",
                "title": "Maintain High Performance Momentum",
                "description": "Continue following the current academic schedule, mentor peers, and explore advanced coursework."
            })

        confidence_pct = round(confidence * 100, 1)
        summary = (
            f"The model predicts the student will PASS with {confidence_pct:.1f}% confidence."
            if prediction_label == "Pass"
            else f"The model flags the student as AT-RISK of failing with {confidence_pct:.1f}% confidence. Immediate academic intervention recommended."
        )

        return {
            "prediction": prediction_label,
            "confidence": round(confidence, 4),
            "confidence_percentage": confidence_pct,
            "probabilities": {
                "pass": round(prob_pass, 4),
                "fail": round(prob_fail, 4)
            },
            "summary": summary,
            "areas_to_improve": areas_to_improve,
            "personalized_suggestions": suggestions,
            "model_used": self.metadata.get("model_name", "LogisticRegression") if self.metadata else "LogisticRegression"
        }

# Singleton instance
_predictor = None

def get_predictor() -> StudentPerformancePredictor:
    global _predictor
    if _predictor is None:
        _predictor = StudentPerformancePredictor()
    return _predictor

def predict_student(student_data: dict) -> dict:
    predictor = get_predictor()
    return predictor.predict(student_data)

if __name__ == "__main__":
    # Self-test with sample profiles
    test_high = {
        "study_hours": 8.0,
        "attendance": 90,
        "previous_score": 85,
        "assignments_completed": 10,
        "participation": "High",
        "sleep_hours": 7.5
    }
    test_low = {
        "study_hours": 1.5,
        "attendance": 50,
        "previous_score": 35,
        "assignments_completed": 2,
        "participation": "Low",
        "sleep_hours": 5.0
    }
    
    print("Test High Performer Result:")
    print(json.dumps(predict_student(test_high), indent=2))
    print("\nTest Low Performer Result:")
    print(json.dumps(predict_student(test_low), indent=2))
