document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const loadingOverlay = document.getElementById('loading-overlay');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = loginForm.email.value;
        const password = loginForm.password.value;

        // Show loading spinner
        if (loadingOverlay) loadingOverlay.classList.add('visible');

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });

            const result = await response.json();

            // Hide loading spinner
            if (loadingOverlay) loadingOverlay.classList.remove('visible');

            if (response.ok) {
                alert(result.message);
                window.location.href = '/ai_tool';
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