document.addEventListener("DOMContentLoaded", () => {
    // Input fields
    const fullnameInput = document.getElementById("fullname");
    const usernameInput = document.getElementById("username");
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");

    // Error message containers
    const fullnameError = createErrorMessageElement(fullnameInput);
    const usernameError = createErrorMessageElement(usernameInput);
    const emailError = createErrorMessageElement(emailInput);
    const passwordError = createErrorMessageElement(passwordInput);

    // Add event listeners for real-time validation
    fullnameInput.addEventListener("input", () => validateFullname(fullnameInput, fullnameError));
    usernameInput.addEventListener("input", () => validateUsername(usernameInput, usernameError));
    emailInput.addEventListener("input", () => validateEmail(emailInput, emailError));
    passwordInput.addEventListener("input", () => validatePassword(passwordInput, passwordError));
});

// Create error message element
function createErrorMessageElement(inputField) {
    const errorMessage = document.createElement("div");
    errorMessage.className = "error-message";
    errorMessage.style.color = "red";
    inputField.parentElement.appendChild(errorMessage);
    return errorMessage;
}

// Validation functions
function validateFullname(input, errorElement) {
    if (!/^[a-zA-Z\s]{2,}$/.test(input.value)) {
        errorElement.textContent = "Full name must contain at least 2 characters and only letters.";
    } else {
        errorElement.textContent = "";
    }
}

function validateUsername(input, errorElement) {
    if (!/^[a-zA-Z0-9]{3,}$/.test(input.value)) {
        errorElement.textContent = "Username must be at least 3 characters long and contain only letters and numbers.";
    } else {
        errorElement.textContent = "";
    }
}

function validateEmail(input, errorElement) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(input.value)) {
        errorElement.textContent = "Please enter a valid email address.";
    } else {
        errorElement.textContent = "";
    }
}

function validatePassword(input, errorElement) {
    const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$/;
    if (!passwordRegex.test(input.value)) {
        errorElement.textContent = "Password must be at least 6 characters long and include at least one letter and one number.";
    } else {
        errorElement.textContent = "";
    }
}
