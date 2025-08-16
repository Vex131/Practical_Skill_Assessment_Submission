// main.js

document.addEventListener("DOMContentLoaded", function() {
    // -----------------------------
    // 1. Status -> Discarded Date handling
    // -----------------------------
    const statusField = document.getElementById("status");
    const discardedDateField = document.getElementById("discarded_date");

    function handleStatusChange() {
        if (!statusField || !discardedDateField) return;

        // Only allow editing discarded date if status is "Discarded"
        if (statusField.value === "Discarded" && !statusField.disabled) {
            discardedDateField.removeAttribute("readonly");

            // Auto-fill today's date if empty
            if (!discardedDateField.value) {
                const today = new Date().toISOString().split('T')[0];
                discardedDateField.value = today;
            }
        } else {
            discardedDateField.value = "";
            discardedDateField.setAttribute("readonly", "readonly");
        }
    }

    if (statusField) {
        statusField.addEventListener("change", handleStatusChange);
        handleStatusChange(); // initial check
    }

    // -----------------------------
    // 2. Password toggle
    // -----------------------------
    const togglePasswordBtn = document.getElementById("togglePassword");
    const passwordInput = document.getElementById("password");

    if (togglePasswordBtn && passwordInput) {
        togglePasswordBtn.addEventListener("click", function () {
            if (passwordInput.type === "password") {
                passwordInput.type = "text";
                togglePasswordBtn.textContent = "Hide";
            } else {
                passwordInput.type = "password";
                togglePasswordBtn.textContent = "Show";
            }
        });
    }

    // -----------------------------
    // 3. Alert fade out
    // -----------------------------
    $(".alert").delay(3000).fadeOut(1000); // requires jQuery
});
