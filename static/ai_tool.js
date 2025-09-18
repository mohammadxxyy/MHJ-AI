document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.querySelector('#chat-form');
    const chatBox = document.querySelector('#chat-box');
    const promptInput = document.querySelector('#prompt-input');

    if (chatForm) {
        chatForm.addEventListener('submit', async function(event) {
            event.preventDefault();

            const prompt = promptInput.value.trim();
            if (!prompt) {
                return;
            }

            // عرض رسالة المستخدم
            const userMessageDiv = document.createElement('div');
            userMessageDiv.className = 'chat-message chat-user';
            userMessageDiv.textContent = prompt;
            chatBox.appendChild(userMessageDiv);

            // عرض رسالة فارغة للرد من الذكاء الاصطناعي مع Loader
            const aiMessageDiv = document.createElement('div');
            aiMessageDiv.className = 'chat-message chat-ai';
            aiMessageDiv.innerHTML = '<span class="loader"></span>';
            chatBox.appendChild(aiMessageDiv);

            // تمرير scroll إلى نهاية الدردشة
            chatBox.scrollTop = chatBox.scrollHeight;

            promptInput.value = '';

            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ prompt })
                });

                const data = await response.json();

                // تحديث رسالة الذكاء الاصطناعي
                if (response.ok) {
                    aiMessageDiv.innerHTML = data.response;
                } else {
                    aiMessageDiv.textContent = data.message || 'حدث خطأ غير متوقع.';
                }

                // تمرير scroll إلى نهاية الدردشة بعد الرد
                chatBox.scrollTop = chatBox.scrollHeight;

            } catch (error) {
                console.error('Error generating response:', error);
                aiMessageDiv.textContent = 'حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.';
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        });
    }
});