/**
 * Main Application Controller for Student Performance Prediction System
 * Coordinates Form, Validation, Presets, API layer, and Live ML Result rendering.
 */

import { FormValidator } from './formValidation.js';
import { StudentAPI } from './api.js';
import { UIComponents } from './uiComponents.js';

// Profile Presets for quick evaluation & college project demonstrations
const PRESETS = {
  high: {
    studyHours: 7.5,
    attendance: 92,
    previousScore: 85,
    assignmentsCompleted: 9,
    participation: 'High',
    sleepHours: 7.5
  },
  average: {
    studyHours: 5.0,
    attendance: 75,
    previousScore: 58,
    assignmentsCompleted: 6,
    participation: 'Medium',
    sleepHours: 6.8
  },
  risk: {
    studyHours: 2.0,
    attendance: 55,
    previousScore: 35,
    assignmentsCompleted: 2,
    participation: 'Low',
    sleepHours: 5.0
  }
};

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('studentPredictionForm');
  const resultsContainer = document.getElementById('resultsContainer');
  const btnPredict = document.getElementById('btnPredict');
  const btnReset = document.getElementById('btnReset');
  const backendStatusBadge = document.getElementById('backendStatusBadge');
  const presetButtons = document.querySelectorAll('.preset-btn');

  // 1. Initial State
  UIComponents.renderEmptyState(resultsContainer);
  checkBackendStatus();

  // Periodic health check
  setInterval(checkBackendStatus, 10000);

  // 2. Attach Real-Time Input Validation
  const inputs = form.querySelectorAll('input, select');
  inputs.forEach((input) => {
    const handleValidation = () => {
      const group = input.closest('.form-group');
      const result = FormValidator.validateField(input);
      if (group) {
        FormValidator.setFieldState(group, result.isValid, result.message);
      }
    };

    input.addEventListener('input', handleValidation);
    input.addEventListener('change', handleValidation);
    input.addEventListener('blur', handleValidation);
  });

  // 3. Preset Buttons Handler
  presetButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const presetType = btn.dataset.preset;
      const data = PRESETS[presetType];
      if (data) {
        Object.entries(data).forEach(([key, val]) => {
          const input = form.querySelector(`[name="${key}"]`);
          if (input) {
            input.value = val;
            const group = input.closest('.form-group');
            if (group) FormValidator.setFieldState(group, true);
          }
        });
      }
    });
  });

  // 4. Form Submission & Performance Prediction
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Validate all fields
    const validation = FormValidator.validateForm(form);
    if (!validation.isValid) {
      const firstError = form.querySelector('.form-group.has-error input, .form-group.has-error select');
      if (firstError) firstError.focus();
      return;
    }

    // Set Loading UI State
    setLoading(true);

    try {
      // Send real data to Flask ML API endpoint
      const response = await StudentAPI.predict(validation.data);

      if (response && response.success && response.prediction) {
        // Render the actual ML classification & diagnostic recommendations
        UIComponents.renderPredictionResult(resultsContainer, response);
      } else {
        // Display error message from server
        UIComponents.renderErrorState(resultsContainer, response.error || 'Prediction service returned an error.');
      }

      // Smooth scroll to results on mobile viewports
      if (window.innerWidth < 1024) {
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    } catch (error) {
      console.error('Prediction error:', error);
      UIComponents.renderErrorState(resultsContainer, error.message || 'An unexpected error occurred during prediction.');
    } finally {
      setLoading(false);
    }
  });

  // 5. Reset Form Handler
  btnReset.addEventListener('click', () => {
    form.reset();
    FormValidator.clearValidation(form);
    UIComponents.renderEmptyState(resultsContainer);
  });

  /**
   * Toggle button loading state
   * @param {boolean} isLoading 
   */
  function setLoading(isLoading) {
    if (isLoading) {
      btnPredict.classList.add('is-loading');
      btnPredict.setAttribute('disabled', 'true');
    } else {
      btnPredict.classList.remove('is-loading');
      btnPredict.removeAttribute('disabled');
    }
  }

  /**
   * Check backend health and update status indicator
   */
  async function checkBackendStatus() {
    if (!backendStatusBadge) return;
    const health = await StudentAPI.checkHealth();
    
    if (health.isOnline) {
      const acc = health.details?.accuracy ? ` (${Math.round(health.details.accuracy * 100)}% Acc)` : '';
      backendStatusBadge.innerHTML = `
        <span class="pulse-dot"></span>
        <span>ML Model: Active${acc}</span>
      `;
      backendStatusBadge.className = 'badge badge-status';
    } else {
      backendStatusBadge.innerHTML = `
        <span class="pulse-dot" style="background-color: var(--accent-amber); box-shadow: 0 0 8px var(--accent-amber);"></span>
        <span>Connecting to ML Model...</span>
      `;
      backendStatusBadge.className = 'badge badge-pbl';
    }
  }
});
