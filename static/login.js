document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('#login-form');
    const messageDiv = document.querySelector('#message');

    if (loginForm) {
        loginForm.addEventListener('submit', async function(event) {
            event.preventDefault(); // منع إعادة تحميل الصفحة

            const usernameInput = loginForm.querySelector('#username');
            const passwordInput = loginForm.querySelector('#password');

            const username = usernameInput.value.trim();
            const password = passwordInput.value.trim();

            if (!username || !password) {
                messageDiv.textContent = 'الرجاء إدخال اسم المستخدم وكلمة المرور.';
                messageDiv.style.color = 'red';
                return;
            }

            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();

                if (response.ok) {
                    window.location.href = '/ai_tool';
                } else {
                    messageDiv.textContent = data.message;
                    messageDiv.style.color = 'red';
                }
            } catch (error) {
                console.error('An error occurred:', error);
                messageDiv.textContent = 'حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.';
                messageDiv.style.color = 'red';
            }
        });
    }
});