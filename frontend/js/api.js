/**
 * API Service Layer for Student Performance Prediction System
 * Directly communicates with the Flask Machine Learning Backend API.
 * Uses relative URLs so this works both locally (Flask on :5000) and on Render.
 */

// Always use relative path - Flask serves frontend + API on same domain
const API_BASE = '/api';

export const StudentAPI = {
  /**
   * Send student parameters to the ML Backend API for prediction
   * @param {Object} studentData 
   * @returns {Promise<Object>}
   */
  async predict(studentData) {
    const payload = {
      study_hours: Number(studentData.studyHours),
      attendance: Number(studentData.attendance),
      previous_score: Number(studentData.previousScore),
      assignments_completed: Number(studentData.assignmentsCompleted),
      participation: studentData.participation,
      sleep_hours: Number(studentData.sleepHours)
    };

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 15000);

      const response = await fetch(`${API_BASE}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(payload),
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || `API error (Status ${response.status})`);
      }

      return {
        success: true,
        ...result
      };
    } catch (error) {
      console.error('API Error in StudentAPI.predict:', error);
      let errorMsg = error.message;
      if (error.name === 'AbortError') {
        errorMsg = 'Prediction request timed out. The server may be starting up (free tier spin-up takes ~30s). Please try again.';
      } else if (error.message.includes('Failed to fetch')) {
        errorMsg = 'Unable to connect to the prediction server. Please refresh and try again.';
      }
      return {
        success: false,
        error: errorMsg
      };
    }
  },

  /**
   * Check if the backend Flask ML server is online and retrieve model health
   * @returns {Promise<{isOnline: boolean, details: Object|null}>}
   */
  async checkHealth() {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(`${API_BASE}/health`, {
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (response.ok) {
        const data = await response.json();
        return { isOnline: true, details: data };
      }
      return { isOnline: false, details: null };
    } catch (e) {
      return { isOnline: false, details: null };
    }
  }
};
