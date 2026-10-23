"""
Student Performance Prediction System - Machine Learning Pipeline
==================================================================
This script inspects the actual student dataset, performs preprocessing,
splits into train/test sets, trains a classification model, evaluates it
thoroughly, and serializes the model artifacts.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
import joblib

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "student_data.csv"
MODEL_DIR = BASE_DIR / "model"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

def inspect_dataset(df):
    print("=" * 70)
    print("1. DATASET INSPECTION")
    print("=" * 70)
    print(f"Total Rows: {len(df)}")
    print(f"Total Columns: {len(df.columns)}")
    print("\nColumns & Data Types:")
    for col in df.columns:
        print(f" - {col:25} : {df[col].dtype}")
    
    print("\nMissing Values per Column:")
    null_counts = df.isnull().sum()
    for col, count in null_counts.items():
        print(f" - {col:25} : {count}")
        
    print(f"\nDuplicate Rows: {df.duplicated().sum()}")
    
    print("\nTarget Variable ('Result') Distribution:")
    target_dist = df['Result'].value_counts()
    for val, count in target_dist.items():
        pct = (count / len(df)) * 100
        print(f" - {val:10} : {count:4} ({pct:.1f}%)")
        
    print("\nFeature Summary Statistics (Numerical):")
    feature_cols = [c for c in df.columns if c not in ['Student_ID', 'Result']]
    print(df[feature_cols].describe().to_string())
    print("=" * 70)

def train_and_evaluate():
    # 1. Load actual uploaded dataset
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")
    
    df = pd.read_csv(DATA_PATH)
    inspect_dataset(df)
    
    # 2. Separate Features and Target
    # Student_ID is an identifier and is strictly excluded
    feature_columns = [
        'Study_Hours',
        'Attendance',
        'Previous_Score',
        'Assignments_Completed',
        'Participation',
        'Sleep_Hours'
    ]
    
    X = df[feature_columns].copy()
    y_raw = df['Result'].copy()
    
    # Target encoding: Pass = 1, Fail = 0
    y = y_raw.map({'Pass': 1, 'Fail': 0})
    
    # 3. Train-Test Split (80% Train, 20% Test, Stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"\n2. DATA SPLIT:")
    print(f" - Training Set size: {len(X_train)} samples")
    print(f" - Testing Set size : {len(X_test)} samples")
    
    # 4. Preprocessing: StandardScaler for numerical features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 5. Model Comparison & Training
    models = {
        "RandomForestClassifier": RandomForestClassifier(
            n_estimators=150, max_depth=6, min_samples_split=4, random_state=42
        ),
        "GradientBoostingClassifier": GradientBoostingClassifier(
            n_estimators=100, learning_rate=0.08, max_depth=4, random_state=42
        ),
        "LogisticRegression": LogisticRegression(
            max_iter=1000, random_state=42
        )
    }
    
    best_model_name = None
    best_model = None
    best_f1 = -1.0
    model_evaluations = {}
    
    print("\n3. MODEL TRAINING & COMPARISON:")
    print("-" * 70)
    
    for name, clf in models.items():
        clf.fit(X_train_scaled, y_train)
        y_pred = clf.predict(X_test_scaled)
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        cv_scores = cross_val_score(clf, X_train_scaled, y_train, cv=5, scoring='f1')
        
        model_evaluations[name] = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "cv_f1_mean": round(float(np.mean(cv_scores)), 4),
            "cv_f1_std": round(float(np.std(cv_scores)), 4)
        }
        
        print(f"[{name}]")
        print(f"   Accuracy: {acc:.4f} | Precision: {prec:.4f} | Recall: {rec:.4f} | F1: {f1:.4f} | CV F1: {np.mean(cv_scores):.4f}")
        
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_model = clf

    print("-" * 70)
    print(f"🏆 Best Model Selected: {best_model_name} (F1 Score: {best_f1:.4f})")
    
    # 6. Detailed Evaluation of Selected Best Model
    y_pred_best = best_model.predict(X_test_scaled)
    y_prob_best = best_model.predict_proba(X_test_scaled)[:, 1] if hasattr(best_model, "predict_proba") else None
    
    acc_final = accuracy_score(y_test, y_pred_best)
    prec_final = precision_score(y_test, y_pred_best, zero_division=0)
    rec_final = recall_score(y_test, y_pred_best, zero_division=0)
    f1_final = f1_score(y_test, y_pred_best, zero_division=0)
    cm = confusion_matrix(y_test, y_pred_best)
    
    print("\n4. FINAL MODEL EVALUATION METRICS:")
    print("=" * 70)
    print(f"Model Name        : {best_model_name}")
    print(f"Accuracy          : {acc_final:.4f} ({acc_final * 100:.2f}%)")
    print(f"Precision (Pass)  : {prec_final:.4f}")
    print(f"Recall (Pass)     : {rec_final:.4f}")
    print(f"F1-Score (Pass)   : {f1_final:.4f}")
    print("\nConfusion Matrix:")
    print(f"                 Predicted Fail   Predicted Pass")
    print(f"Actual Fail (0) :      {cm[0][0]:<14} {cm[0][1]:<14}")
    print(f"Actual Pass (1) :      {cm[1][0]:<14} {cm[1][1]:<14}")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred_best, target_names=['Fail', 'Pass']))
    
    # Feature Importance (if available)
    feature_importances = {}
    if hasattr(best_model, "feature_importances_"):
        for col, imp in zip(feature_columns, best_model.feature_importances_):
            feature_importances[col] = round(float(imp), 4)
        print("\nFeature Importances:")
        for col, imp in sorted(feature_importances.items(), key=lambda x: x[1], reverse=True):
            print(f" - {col:25} : {imp:.4f} ({imp*100:.1f}%)")
    
    # 7. Save Model Artifacts
    model_file = MODEL_DIR / "student_model.joblib"
    scaler_file = MODEL_DIR / "scaler.joblib"
    metadata_file = MODEL_DIR / "model_metadata.json"
    
    joblib.dump(best_model, model_file)
    joblib.dump(scaler, scaler_file)
    
    metadata = {
        "model_name": best_model_name,
        "features": feature_columns,
        "target": "Result",
        "target_mapping": {"Fail": 0, "Pass": 1},
        "metrics": {
            "accuracy": float(round(acc_final, 4)),
            "precision": float(round(prec_final, 4)),
            "recall": float(round(rec_final, 4)),
            "f1_score": float(round(f1_final, 4))
        },
        "confusion_matrix": {
            "true_negatives": int(cm[0][0]),
            "false_positives": int(cm[0][1]),
            "false_negatives": int(cm[1][0]),
            "true_positives": int(cm[1][1])
        },
        "feature_importances": feature_importances,
        "all_models_evaluated": model_evaluations,
        "dataset_summary": {
            "total_samples": len(df),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "pass_count": int((y == 1).sum()),
            "fail_count": int((y == 0).sum())
        }
    }
    
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)
        
    print("\n5. ARTIFACTS SAVED:")
    print(f" [+] Model saved to      : {model_file}")
    print(f" [+] Scaler saved to     : {scaler_file}")
    print(f" [+] Metadata saved to   : {metadata_file}")
    print("=" * 70)
    
    return metadata

if __name__ == "__main__":
    train_and_evaluate()
