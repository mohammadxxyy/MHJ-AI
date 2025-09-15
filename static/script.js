document.addEventListener('DOMContentLoaded', () => {
    const signupForm = document.getElementById('signupForm');
    const loadingOverlay = document.getElementById('loading-overlay');

    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = signupForm.username.value;
        const email = signupForm.email.value;
        const password = signupForm.password.value;

        // Show loading spinner
        if (loadingOverlay) loadingOverlay.classList.add('visible');

        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, email, password })
            });

            const result = await response.json();

            // Hide loading spinner
            if (loadingOverlay) loadingOverlay.classList.remove('visible');

            if (response.ok) {
                alert(result.message);
                window.location.href = '/login';
            } else {
                alert(result.message);
            }
        } catch (error) {
            console.error('Error:', error);
            if (loadingOverlay) loadingOverlay.classList.remove('visible');
            alert('حدث خطأ في الاتصال بالخادم. حاول مرة أخرى.');
        }
    });
});