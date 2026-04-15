const API_BASE = "http://localhost:8000";

const form = document.getElementById('generator-form');
const generateBtn = document.getElementById('generate-btn');
const resultContainer = document.getElementById('result-container');
const resultContent = document.getElementById('result-content');
const historyContainer = document.getElementById('history-container');
const historyLoader = document.getElementById('history-loader');
const copyBtn = document.getElementById('btn-copy-result');

// Drawer Toggle Logic
const btnHistoryToggle = document.getElementById('btn-history-toggle');
const btnCloseHistory = document.getElementById('btn-close-history');
const historyPanel = document.getElementById('history-panel');
const historyOverlay = document.getElementById('history-overlay');

function openHistory() {
    historyPanel.classList.add('active');
    historyOverlay.classList.add('active');
    loadHistory(); // Refresh history when opened
}

function closeHistory() {
    historyPanel.classList.remove('active');
    historyOverlay.classList.remove('active');
}

btnHistoryToggle.addEventListener('click', openHistory);
btnCloseHistory.addEventListener('click', closeHistory);
historyOverlay.addEventListener('click', closeHistory);

// Form Submit Handler
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const product = document.getElementById('product').value.trim();
    const audience = document.getElementById('audience').value.trim();
    const tone = document.getElementById('tone').value;

    if (!product || !audience || !tone) return;

    // Loading State
    generateBtn.classList.add('loading');
    resultContainer.classList.remove('appear');
    setTimeout(() => resultContainer.classList.add('hidden'), 300);

    try {
        const response = await fetch(`${API_BASE}/campaign-copy`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product, audience, tone })
        });

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }

        const data = await response.json();
        
        // Show result
        resultContent.textContent = data.copy;
        resultContainer.classList.remove('hidden');
        // Force reflow
        void resultContainer.offsetWidth;
        resultContainer.classList.add('appear');

        // Reload history
        loadHistory();
    } catch (error) {
        console.error("Failed to generate:", error);
        resultContent.innerHTML = `<span style="color: var(--error);">Error: Could not generate copy. Please ensure the backend server is running.</span>`;
        resultContainer.classList.remove('hidden');
        void resultContainer.offsetWidth;
        resultContainer.classList.add('appear');
    } finally {
        generateBtn.classList.remove('loading');
    }
});

// Copy to Clipboard
copyBtn.addEventListener('click', () => {
    const text = resultContent.textContent;
    if (text) {
        navigator.clipboard.writeText(text);
        copyBtn.style.color = "var(--accent)";
        setTimeout(() => {
            copyBtn.style.color = "var(--text-muted)";
        }, 2000);
    }
});

// Load History
async function loadHistory() {
    historyLoader.style.display = 'flex';
    
    try {
        const response = await fetch(`${API_BASE}/campaign-copy`);
        if (!response.ok) throw new Error('History fetch failed');

        const copies = await response.json();
        
        if (copies.length === 0) {
            historyContainer.innerHTML = '<div class="empty-state">No archived campaigns yet.</div>';
            return;
        }

        historyContainer.innerHTML = copies.map(item => `
            <div class="history-chat-item">
                <div class="chat-avatar">
                   <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                </div>
                <div class="chat-content">
                    <div class="chat-header">
                        <span class="chat-product">${escapeHtml(item.product)}</span>
                        <span class="chat-tone">${escapeHtml(item.tone)}</span>
                    </div>
                    <div class="chat-bubble">
                        ${escapeHtml(item.copy)}
                    </div>
                    <div class="chat-footer">Target: ${escapeHtml(item.audience)}</div>
                </div>
            </div>
        `).join('');

    } catch (error) {
        historyContainer.innerHTML = '<div class="empty-state" style="color: var(--error)">Failed to load archive.</div>';
    } finally {
        historyLoader.style.display = 'none';
    }
}

// Utility to escape HTML to prevent XSS
function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
    loadHistory();
});
