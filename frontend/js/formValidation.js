/**
 * Form Validation Module for Student Performance Prediction System
 * Handles strict client-side constraints and real-time field feedback.
 */

export const FormValidator = {
  // Field validation rules
  rules: {
    studyHours: {
      min: 0,
      max: 24,
      required: true,
      label: 'Study Hours',
      errorEmpty: 'Study hours are required',
      errorRange: 'Study hours must be between 0 and 24 hours/day'
    },
    attendance: {
      min: 0,
      max: 100,
      required: true,
      label: 'Attendance',
      errorEmpty: 'Attendance percentage is required',
      errorRange: 'Attendance must be between 0% and 100%'
    },
    previousScore: {
      min: 0,
      max: 100,
      required: true,
      label: 'Previous Score',
      errorEmpty: 'Previous score is required',
      errorRange: 'Previous score must be between 0 and 100 marks'
    },
    assignmentsCompleted: {
      min: 0,
      max: 50,
      required: true,
      label: 'Assignments Completed',
      errorEmpty: 'Completed assignments count is required',
      errorRange: 'Assignments must be between 0 and 50'
    },
    participation: {
      required: true,
      label: 'Participation',
      allowedValues: ['High', 'Medium', 'Low'],
      errorEmpty: 'Please select student classroom participation level'
    },
    sleepHours: {
      min: 0,
      max: 24,
      required: true,
      label: 'Sleep Hours',
      errorEmpty: 'Sleep hours are required',
      errorRange: 'Sleep hours must be between 0 and 24 hours/day'
    }
  },

  /**
   * Validate a single form input element
   * @param {HTMLInputElement|HTMLSelectElement} inputElement 
   * @returns {{isValid: boolean, message: string}}
   */
  validateField(inputElement) {
    const fieldName = inputElement.name || inputElement.id;
    const rule = this.rules[fieldName];
    const value = inputElement.value.trim();

    if (!rule) {
      return { isValid: true, message: '' };
    }

    // Required check
    if (rule.required && (value === '' || value === null || value === undefined)) {
      return { isValid: false, message: rule.errorEmpty };
    }

    // Dropdown / Select check
    if (rule.allowedValues) {
      if (!rule.allowedValues.includes(value)) {
        return { isValid: false, message: rule.errorEmpty };
      }
      return { isValid: true, message: '' };
    }

    // Numeric checks
    const numValue = Number(value);
    if (isNaN(numValue)) {
      return { isValid: false, message: `${rule.label} must be a valid numeric value` };
    }

    if (numValue < rule.min || numValue > rule.max) {
      return { isValid: false, message: rule.errorRange };
    }

    return { isValid: true, message: '' };
  },

  /**
   * Display or clear error for a specific field
   * @param {HTMLElement} formGroup 
   * @param {boolean} isValid 
   * @param {string} message 
   */
  setFieldState(formGroup, isValid, message = '') {
    const errorContainer = formGroup.querySelector('.error-message');

    if (!isValid) {
      formGroup.classList.add('has-error');
      formGroup.classList.remove('is-valid');
      if (errorContainer) {
        errorContainer.textContent = message;
      }
    } else {
      formGroup.classList.remove('has-error');
      formGroup.classList.add('is-valid');
      if (errorContainer) {
        errorContainer.textContent = '';
      }
    }
  },

  /**
   * Validate entire form
   * @param {HTMLFormElement} form 
   * @returns {{isValid: boolean, data: Object|null, errors: Object}}
   */
  validateForm(form) {
    let isValid = true;
    const errors = {};
    const data = {};

    const inputs = form.querySelectorAll('input, select');
    inputs.forEach((input) => {
      const fieldName = input.name || input.id;
      if (!fieldName) return;

      const group = input.closest('.form-group');
      const result = this.validateField(input);

      if (!result.isValid) {
        isValid = false;
        errors[fieldName] = result.message;
        if (group) this.setFieldState(group, false, result.message);
      } else {
        if (group) this.setFieldState(group, true);
        data[fieldName] = input.type === 'number' ? parseFloat(input.value) : input.value;
      }
    });

    return { isValid, data: isValid ? data : null, errors };
  },

  /**
   * Clear all error states from form
   * @param {HTMLFormElement} form 
   */
  clearValidation(form) {
    const groups = form.querySelectorAll('.form-group');
    groups.forEach((group) => {
      group.classList.remove('has-error', 'is-valid');
      const errorContainer = group.querySelector('.error-message');
      if (errorContainer) errorContainer.textContent = '';
    });
  }
};
