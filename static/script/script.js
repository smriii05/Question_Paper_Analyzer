function validateFile() {
    const fileInput = document.getElementById('fileInput');
    const errorMessage = document.getElementById('error-message');
    const file = fileInput.files[0];

    if (!file) {
        displayErrorMessage("No file selected. Please upload a text file.");
        return false;
    }

    if ((file.type && file.type !== 'text/plain') || (!file.type && !file.name.endsWith('.txt'))) {
        displayErrorMessage("Please upload a valid .txt file.");
        return false;
    }

    if (file.size === 0) {
        displayErrorMessage("The file is empty. Please upload a valid text file.");
        return false;
    }

    return true;
}

// function isValidQuestionFormat(contents) {
//     const questions = contents.split(/\r?\n/).map(line => line.trim()).filter(line => line.length > 0);
//     const questionPattern = /^[A-Z].*\?$/;
//     const specificTermPattern = /^(Describe|Define|Differentiate|Classify)/;

//     return questions.every(line => {
//         return (
//             (questionPattern.test(line) && !specificTermPattern.test(line)) || 
//             (specificTermPattern.test(line) && line.endsWith('.'))
//         );
//     });
// }

function isValidQuestionFormat(contents) {
    // Define patterns for validation
    const questionPattern = /^[A-Z].*\?$/; 
    const specificTermPattern = /^(Describe|Define|Differentiate|Classify|Explain|Compare|Convert|A| In|The|For|Demonstrate|Write|Discuss)/; 

    // Split contents into lines, then split by whitespace preceded by . or ?
    const questions = contents
        .split(/\\r?\\n/) // Split into lines by newline
        .flatMap(line => line.trim().split(/(?<=[?]|(?<!\d)\.)\s+/))
        .filter(line => line.length > 0); 
    
    return questions.every(question => {
        return (
            (questionPattern.test(question) && !specificTermPattern.test(question)) || // Ends with '?' and doesn't start with specific terms
            (specificTermPattern.test(question) && question.endsWith('.')) // Starts with specific terms and ends with '.'
        );
    });
}

function displayErrorMessage(message) {
    const errorMessage = document.getElementById('error-message');
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';

    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 3000);
}

document.getElementById('analyzeButton').addEventListener('click', function (event) {
    event.preventDefault();

    if (!validateFile()) {
        return;
    }

    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (file) {
        const reader = new FileReader();

        reader.onload = function (event) {
            const contents = event.target.result;

            if (isValidQuestionFormat(contents)) {
                alert("Validation successful! File content is valid.");
                sendFileForAnalysis(file);
            } else {
                displayErrorMessage("Error: The uploaded file does not contain a valid set of questions.");
            }
        };

        reader.readAsText(file);
    }
});

function sendFileForAnalysis(file) {
    const formData = new FormData();
    formData.append("file", file);

    fetch("/analyze", {
        method: "POST",
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        // Handle the success response
        alert(data.message);  // Show the success message

        // Redirect the user to the 'results' page
        window.location.href = data.redirect_url; // Redirect to /results
    })
    .catch(error => {
        alert("Error uploading file:", error.message);
    });
}

function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('active');
}

function confirmDelete(userId) {
    // Display confirmation popup
    const userConfirmation = confirm("Are you sure you want to delete this user?");
    
    if (userConfirmation) {
        // If confirmed, submit the form
        document.getElementById("delete-form-" + userId).submit();
        return true;
    } else {
        // If not confirmed, do nothing (form is not submitted)
        return false;
    }
}

function confirmLogout() {
    // Show a confirmation dialog
    var userConfirmation = confirm("Are you sure you want to log out?");
    
    // If the user confirms, proceed with logout
    if (userConfirmation) {
        window.location.href = "/admin/logout";
    }
}
