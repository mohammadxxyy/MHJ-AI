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
});
document.getElementById('aiForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const userPrompt = document.getElementById('user_prompt').value;
    const responseArea = document.getElementById('aiResponseArea');
    
    responseArea.innerHTML = '<p>الذكاء الاصطناعي يفكر... <span class="loading-dots"></span></p>';
    
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt: userPrompt })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            responseArea.innerHTML = `<p>${result.response}</p>`;
        } else {
            responseArea.innerHTML = `<p style="color: red;">خطأ: ${result.error}</p>`;
        }
        
    } catch (error) {
        console.error('Error:', error);
        responseArea.innerHTML = `<p style="color: red;">حدث خطأ في الاتصال بالخادم. حاول مرة أخرى.</p>`;
    }
});