# Student Performance Prediction System (College PBL Project)

An end-to-end Machine Learning web application designed for college Project-Based Learning (PBL). The system evaluates student academic and behavioral factors to predict academic outcomes (**Pass/Fail**), diagnose performance bottlenecks, and generate actionable, personalized improvement recommendations using a trained **Logistic Regression classification model** (85.0% accuracy).

---

## 📁 Project Architecture & Directory Structure

```
Student_Performance_Prediction/
│
├── frontend/                        # Client-Side User Interface
│   ├── index.html                  # Main academic dashboard entry point
│   ├── css/
│   │   ├── style.css               # Core design tokens, dark slate theme & responsive grid
│   │   └── components.css          # Form inputs, preset buttons, status gauges & result cards
│   └── js/
│       ├── app.js                  # Main controller coordinating validation, presets & live ML rendering
│       ├── api.js                  # Connected API client calling /api/predict
│       ├── formValidation.js       # Client-side input validation and real-time field feedback
│       └── uiComponents.js         # Dynamic UI renderers (Empty, ML Results, Error states)
│
├── backend/                         # Machine Learning & Flask API Server
│   ├── app.py                      # Flask API server (/api/predict, /api/health, /api/model-info)
│   ├── predictor.py                # ML inference pipeline (StandardScaler + Model + Recommendations)
│   ├── train_model.py              # ML training, evaluation & artifact serialization pipeline
│   ├── requirements.txt            # Python dependencies (Flask, scikit-learn, pandas, numpy, joblib)
│   ├── data/
│   │   └── student_data.csv        # Actual training dataset (400 student records)
│   └── model/
│       ├── student_model.joblib    # Trained Logistic Regression classifier (85.0% accuracy)
│       ├── scaler.joblib           # Fitted StandardScaler for numerical features
│       └── model_metadata.json     # Model metadata, confusion matrix & evaluation metrics
│
├── run.py                          # One-command runner for integrated server & quick mode
└── README.md                       # Comprehensive PBL project documentation
```

---

## 🌟 Key Features

1. **Integrated Machine Learning Classification**:
   - Trained on 400 real student performance records using Stratified Train/Test split.
   - Evaluated across Accuracy (85.0%), Precision (0.8611), Recall (0.8158), and F1-score (0.8378).
   - Real-time inference through `POST /api/predict`.
2. **Comprehensive Student Assessment Inputs**:
   - **Study Hours** (Daily study duration, 0–24 hrs/day)
   - **Attendance (%)** (Classroom presence, 0–100%)
   - **Previous Score** (Prior exam performance, 0–100 marks)
   - **Assignments Completed** (Submission count, 0–50)
   - **Participation** (Classroom engagement: High, Medium, Low)
   - **Sleep Hours** (Rest schedule, 0–24 hrs/night)
3. **Automated Diagnostic & Personalized Recommendation Engine**:
   - Identifies attendance deficits, study duration gaps, and submission trends.
   - Generates targeted, student-specific actionable advice with categorized icons.
4. **Interactive Demo Presets**:
   - Quick-load buttons for *High Performer*, *Average Student*, and *At-Risk Student* profiles.
5. **Modern Academic Dashboard**:
   - Dark slate glassmorphism aesthetic with Google Fonts (*Outfit* and *Inter*).

---

## 🚀 How to Run the Application

### 1. Launch the Application
In your terminal / command prompt:
```bash
python run.py
```
*This launches the integrated Flask server with live ML prediction capabilities.*

### 2. Open in Browser
Navigate to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔌 API Reference

### `POST /api/predict`
**Request Payload (JSON):**
```json
{
  "study_hours": 7.5,
  "attendance": 90,
  "previous_score": 85,
  "assignments_completed": 9,
  "participation": "High",
  "sleep_hours": 7.5
}
```

**Response Payload (JSON):**
```json
{
  "status": "success",
  "prediction": "Pass",
  "confidence": 0.9989,
  "probabilities": {
    "pass": 0.9989,
    "fail": 0.0011
  },
  "summary": "The model predicts the student will PASS with 99.9% confidence.",
  "areas_to_improve": [...],
  "personalized_suggestions": [...],
  "model_used": "LogisticRegression"
}
```

### `GET /api/health`
Returns backend and ML model operational status.
