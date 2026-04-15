const API_BASE = "http://localhost:8000";

// ── DOM References ───────────────────────────────────────────────────────────
const form            = document.getElementById('generator-form');
const generateBtn     = document.getElementById('generate-btn');
const resultContainer = document.getElementById('result-container');
const resultContent   = document.getElementById('result-content');
const copyBtn         = document.getElementById('btn-copy-result');

// ── Tab Switching ─────────────────────────────────────────────────────────────
const tabs = document.querySelectorAll('.nav-tab');
const sections = {
    campaign: document.getElementById('campaign-section'),
    followup: document.getElementById('followup-section')
};

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        Object.values(sections).forEach(s => s.classList.add('hidden'));
        sections[tab.dataset.target].classList.remove('hidden');
    });
});

// ── Campaign Copy Form ────────────────────────────────────────────────────────
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const product  = document.getElementById('product').value.trim();
    const audience = document.getElementById('audience').value.trim();
    const tone     = document.getElementById('tone').value;

    if (!product || !audience || !tone) return;

    generateBtn.classList.add('loading');
    resultContainer.classList.add('hidden');

    try {
        const res = await fetch(`${API_BASE}/campaign-copy`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product, audience, tone })
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `Server error ${res.status}`);
        }

        const data = await res.json();
        resultContent.textContent = data.copy;
        resultContainer.classList.remove('hidden');
        void resultContainer.offsetWidth;
        resultContainer.classList.add('appear');
    } catch (error) {
        console.error("Campaign generation failed:", error);
        resultContent.innerHTML = `<span style="color:var(--error)">Error: ${error.message}</span>`;
        resultContainer.classList.remove('hidden');
    } finally {
        generateBtn.classList.remove('loading');
    }
});

// ── Follow-up Form ────────────────────────────────────────────────────────────
const followupForm          = document.getElementById('followup-form');
const followupBtn           = document.getElementById('f-generate-btn');
const followupResultContainer = document.getElementById('f-result-container');
const followupResultContent   = document.getElementById('f-result-content');
const followupCopyBtn         = document.getElementById('f-btn-copy-result');

followupForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const prospect         = document.getElementById('f-prospect').value.trim();
    const email            = document.getElementById('f-email').value.trim();
    const last_interaction = document.getElementById('f-interaction').value.trim();
    const days_since       = parseInt(document.getElementById('f-days').value);

    followupBtn.classList.add('loading');
    followupResultContainer.classList.add('hidden');

    try {
        const res = await fetch(`${API_BASE}/generate-followup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prospect, email, last_interaction, days_since })
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `Server error ${res.status}`);
        }

        const data = await res.json();
        followupResultContent.textContent = data.email_text;
        followupResultContainer.classList.remove('hidden');
        void followupResultContainer.offsetWidth;
        followupResultContainer.classList.add('appear');
    } catch (error) {
        console.error("Follow-up generation failed:", error);
        followupResultContent.innerHTML = `<span style="color:var(--error)">Error: ${error.message}</span>`;
        followupResultContainer.classList.remove('hidden');
    } finally {
        followupBtn.classList.remove('loading');
    }
});

// ── Copy Buttons ──────────────────────────────────────────────────────────────
function setupCopy(btn, contentEl) {
    btn.addEventListener('click', () => {
        const text = contentEl.textContent;
        if (!text) return;
        navigator.clipboard.writeText(text);
        btn.style.color = "var(--accent)";
        setTimeout(() => { btn.style.color = "var(--text-muted)"; }, 2000);
    });
}

setupCopy(copyBtn, resultContent);
setupCopy(followupCopyBtn, followupResultContent);
