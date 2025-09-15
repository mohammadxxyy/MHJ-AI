document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const chatMessages = document.getElementById('chatMessages');

    function createMessageElement(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(sender);
        messageDiv.innerHTML = `<p>${text}</p>`;
        return messageDiv;
    }

    async function sendMessage(prompt) {
        // إضافة رسالة المستخدم على الفور
        const userMessage = createMessageElement(prompt, 'user');
        chatMessages.appendChild(userMessage);
        userInput.value = '';
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // إضافة رسالة تحميل للذكاء الاصطناعي
        const loadingMessage = createMessageElement('الذكاء الاصطناعي يكتب...', 'ai');
        loadingMessage.id = 'loading-message';
        chatMessages.appendChild(loadingMessage);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt: prompt })
            });

            const result = await response.json();
            
            // إزالة رسالة التحميل
            loadingMessage.remove();

            if (response.ok) {
                const aiMessage = createMessageElement(result.response, 'ai');
                chatMessages.appendChild(aiMessage);
            } else {
                const errorMessage = createMessageElement(`خطأ: ${result.error}`, 'ai error');
                chatMessages.appendChild(errorMessage);
            }

        } catch (error) {
            console.error('Error:', error);
            loadingMessage.remove();
            const errorMessage = createMessageElement('حدث خطأ في الاتصال بالخادم. حاول مرة أخرى.', 'ai error');
            chatMessages.appendChild(errorMessage);
        }

        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const prompt = userInput.value.trim();
        if (prompt) {
            sendMessage(prompt);
        }
    });
});