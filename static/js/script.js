
function togglePasswordVisibility() {
    var x = document.getElementById("password");
    if (x.type === "password") {
        x.type = "text";
    } else {
        x.type = "password";
    }
}


// Affiche les données sauvegardées si 'remember me' était coché
window.onload = function() {
    var savedEmail = localStorage.getItem('email');
    var savedPassword = localStorage.getItem('password');
    if (savedEmail && savedPassword) {
        document.querySelector('input[type="email"]').value = savedEmail;
        document.querySelector('input[type="password"]').value = savedPassword;
        document.querySelector('input[type="checkbox"]').checked = true;
    }
};
