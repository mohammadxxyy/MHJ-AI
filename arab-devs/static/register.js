document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.querySelector('#register-form');
    const messageDiv = document.querySelector('#message');

    if (registerForm) {
        registerForm.addEventListener('submit', async function(event) {
            event.preventDefault();

            const usernameInput = registerForm.querySelector('#username');
            const emailInput = registerForm.querySelector('#email');
            const passwordInput = registerForm.querySelector('#password');

            const username = usernameInput.value.trim();
            const email = emailInput.value.trim();
            const password = passwordInput.value.trim();

            if (!username || !email || !password) {
                messageDiv.textContent = 'الرجاء إدخال اسم المستخدم والبريد الإلكتروني وكلمة المرور.';
                messageDiv.style.color = 'red';
                return;
            }

            // تحقق من تنسيق البريد الإلكتروني
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                messageDiv.textContent = 'الرجاء إدخال بريد إلكتروني صحيح.';
                messageDiv.style.color = 'red';
                return;
            }

            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, email, password })
                });

                const data = await response.json();

                if (response.ok) {
                    messageDiv.textContent = 'تم التسجيل بنجاح! سيتم تحويلك إلى صفحة تسجيل الدخول.';
                    messageDiv.style.color = 'green';
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 2000);
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