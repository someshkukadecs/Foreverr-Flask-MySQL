/**
 * =============================================================================
 * FOREVERR - FRONTEND JAVASCRIPT
 * Simple, vanilla, beginner-friendly client-side scripts.
 * =============================================================================
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Mobile Menu Navigation Toggle
  const mobileToggle = document.getElementById('mobileToggle');
  const navMenu = document.getElementById('navMenu');
  if (mobileToggle && navMenu) {
    mobileToggle.addEventListener('click', function () {
      navMenu.classList.toggle('open');
    });
  }

  // 2. Quantity Selector (+ / - buttons on Product and Cart pages)
  setupQuantityButtons();

  // 3. Checkout Payment Mode Dynamic Field Switcher
  setupPaymentModeSwitcher();

  // 4. Client-side 6-digit Password Validation
  setupPasswordValidation();

  // 5. Image URL Live Preview for Add / Edit Product forms
  setupImagePreview();

  // 6. Delete Confirmation Safeguard
  setupDeleteConfirmations();
});

/**
 * Handles increment and decrement buttons for quantity inputs
 */
function setupQuantityButtons() {
  const qtyWrappers = document.querySelectorAll('.quantity-control');
  qtyWrappers.forEach((wrapper) => {
    const btnMinus = wrapper.querySelector('.qty-minus');
    const btnPlus = wrapper.querySelector('.qty-plus');
    const input = wrapper.querySelector('.qty-input');

    if (btnMinus && btnPlus && input) {
      btnMinus.addEventListener('click', function (e) {
        e.preventDefault();
        let val = parseInt(input.value) || 1;
        if (val > 1) {
          input.value = val - 1;
          input.dispatchEvent(new Event('change'));
        }
      });

      btnPlus.addEventListener('click', function (e) {
        e.preventDefault();
        let val = parseInt(input.value) || 1;
        let max = parseInt(input.getAttribute('max')) || 99;
        if (val < max) {
          input.value = val + 1;
          input.dispatchEvent(new Event('change'));
        } else {
          alert('Maximum available stock limit reached: ' + max);
        }
      });
    }
  });
}

/**
 * Switches payment-specific input fields depending on chosen method
 * (COD, UPI, CARD, NET_BANKING)
 */
function setupPaymentModeSwitcher() {
  const paymentInputs = document.querySelectorAll('input[name="payment_method"]');
  const detailsUpi = document.getElementById('payment-details-upi');
  const detailsCard = document.getElementById('payment-details-card');
  const detailsNet = document.getElementById('payment-details-netbanking');
  const detailsCod = document.getElementById('payment-details-cod');

  if (!paymentInputs.length) return;

  function updatePaymentVisibility(selectedMethod) {
    // Hide all first
    if (detailsUpi) detailsUpi.style.display = 'none';
    if (detailsCard) detailsCard.style.display = 'none';
    if (detailsNet) detailsNet.style.display = 'none';
    if (detailsCod) detailsCod.style.display = 'none';

    // Highlight selected card styling
    document.querySelectorAll('.payment-option-label').forEach((lbl) => {
      lbl.classList.remove('active');
    });

    const activeLabel = document.querySelector(`label[for="pay_${selectedMethod}"]`);
    if (activeLabel) activeLabel.classList.add('active');

    // Show appropriate fields
    if (selectedMethod === 'UPI' && detailsUpi) {
      detailsUpi.style.display = 'block';
    } else if (selectedMethod === 'CARD' && detailsCard) {
      detailsCard.style.display = 'block';
    } else if (selectedMethod === 'NET_BANKING' && detailsNet) {
      detailsNet.style.display = 'block';
    } else if (selectedMethod === 'COD' && detailsCod) {
      detailsCod.style.display = 'block';
    }
  }

  paymentInputs.forEach((input) => {
    input.addEventListener('change', function () {
      updatePaymentVisibility(this.value);
    });
    // Initialize checked one
    if (input.checked) {
      updatePaymentVisibility(input.value);
    }
  });
}

/**
 * Validates 6-character / 6-digit passwords on registration and password change forms
 */
function setupPasswordValidation() {
  const authForm = document.querySelector('form.validate-password-form');
  if (!authForm) return;

  authForm.addEventListener('submit', function (e) {
    const pwdInput = authForm.querySelector('input[name="password"]');
    const confirmInput = authForm.querySelector('input[name="confirm_password"]');

    if (pwdInput) {
      const pwdVal = pwdInput.value.trim();
      // Validate exact 6 length rule
      if (pwdVal.length !== 6) {
        e.preventDefault();
        alert('Password must be exactly 6 characters or digits long.');
        pwdInput.focus();
        return false;
      }
    }

    if (pwdInput && confirmInput) {
      if (pwdInput.value !== confirmInput.value) {
        e.preventDefault();
        alert('Passwords do not match. Please re-enter.');
        confirmInput.focus();
        return false;
      }
    }
  });
}

/**
 * Shows live preview when seller/admin enters an Image URL
 */
function setupImagePreview() {
  const imageUrlInput = document.getElementById('productImageUrl');
  const previewImg = document.getElementById('imagePreviewTarget');

  if (imageUrlInput && previewImg) {
    imageUrlInput.addEventListener('input', function () {
      const url = this.value.trim();
      if (url.startsWith('http://') || url.startsWith('https://')) {
        previewImg.src = url;
        previewImg.style.display = 'block';
      }
    });
  }
}

/**
 * Prompts user before destructive actions (delete product, delete user)
 */
function setupDeleteConfirmations() {
  const deleteLinks = document.querySelectorAll('.confirm-delete');
  deleteLinks.forEach((link) => {
    link.addEventListener('click', function (e) {
      const item = this.getAttribute('data-item-name') || 'this item';
      const confirmed = confirm(`Are you sure you want to permanently delete ${item}?`);
      if (!confirmed) {
        e.preventDefault();
      }
    });
  });
}
