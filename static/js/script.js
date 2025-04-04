document.addEventListener("DOMContentLoaded", function () {
    let signupForm = document.querySelector("form[action='signup']");
    if (signupForm) {
        signupForm.addEventListener("submit", function (event) {
            let password = document.querySelector("input[name='password']").value;
            let confirmPassword = document.querySelector("input[name='confirm_password']").value;
            
            if (password !== confirmPassword) {
                event.preventDefault();
                alert("Passwords do not match!");
            }
        });
    }
});
