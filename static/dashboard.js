
// Function to show the loading overlay
function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    overlay.style.display = 'flex';
    setTimeout(() => {
        overlay.classList.add('visible');
    }, 10);
}

// Function to hide the loading overlay
function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.remove('visible');
    setTimeout(() => {
        overlay.style.display = 'none';
    }, 500);
}

// Attach loading screen to all internal links
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('a[href^="/"]').forEach(link => {
        link.addEventListener('click', () => {
            showLoading();
        });
    });
});document.addEventListener('DOMContentLoaded', () => {
    const username = localStorage.getItem('username');
    const email = localStorage.getItem('email');

    if (username && email) {
        document.getElementById('username').textContent = username;
        document.getElementById('email-display').textContent = email;
    } else {
        window.location.href = '/login';
    }

    document.getElementById('logout-button').addEventListener('click', () => {
        localStorage.removeItem('username');
        localStorage.removeItem('email');
        window.location.href = '/login';
    });
});