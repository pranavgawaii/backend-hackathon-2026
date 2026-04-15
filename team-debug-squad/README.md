# 🚀 Hapticware Backend Hackathon Submission

<div align="center">
  <img src="frontend/assets/ui-screenshot.png" alt="Premium AI Campaign Copy Generator UI" />
</div>

<br/>

> **Team Debug Squad**
> * **Pranav Gawai**
> * **Sanika Shriram Chavan**

## 📖 Executive Summary
The **Premium AI Campaign Copy Generator** is an enterprise-grade, high-performance web application engineered to instantly compose professional, persuasive marketing copy using advanced LLMs. Built with an uncompromising focus on scalable backend architecture, the solution leverages Groq's high-speed inference engine, a distributed DigitalOcean PostgreSQL cluster, and a pristine UI system built on Vercel's Geist typography.

---

## 🧠 Our Approach & Methodology

When tackling this hackathon, we prioritized **production readiness, decoupled architecture, and speed**:

1. **Robust Data Layer First:** Rather than relying on simple SQLite or in-memory stores, we designed the backend to scale. We established a synchronous connection to a remote **DigitalOcean PostgreSQL cluster** using robust `psycopg` (v3) bindings.
2. **Resilience & Automation:** We mitigated deployment friction by implementing an automated FastAPI `lifespan` hook. Upon boot, the server checks the remote schema and transparently provisions the `campaign_copies` table if it's missing, guaranteeing zero runtime faults.
3. **Optimized AI Inference:** Instead of slower legacy endpoints, we routed the generation requests through **Groq's LPU inference engine** using `Llama 3.3 70B`. This reduces latency to mere milliseconds, giving users real-time feedback.
4. **Premium Frontend Layer:** A backend is only as brilliant as the interface interacting with it. We eschewed basic HTML for a **"Clean White" minimalist design system**. Utilizing the professional `Geist` sans-serif typeface, soft shadows, and a sliding chat-history interface, the frontend simulates a high-end SaaS product.

---

## 🛠️ Core Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend API** | FastAPI (Python 3) | High-concurrency async routing and request validation. |
| **Database** | PostgreSQL (`psycopg` v3) | Reliable, ACID-compliant persistence housed on DigitalOcean. |
| **Intelligence** | Groq SDK (Llama 3.3) | Millisecond-latency LLM completions for campaign copy. |
| **Frontend UI** | HTML5, CSS3, Vanilla JS | Zero-dependency, Vercel-inspired clean white aesthetic. |

---

## 🚀 Quick Start & Installation

### 1. Initialize the Environment
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Local Secrets
Ensure your `backend/.env` file is populated securely. (Our backend code maps directly to `os.getenv` to avoid hardcoding credentials):
```env
GROQ_API_KEY=your_production_key_here
DATABASE_URL=postgresql://doadmin:password@db-host.../defaultdb?sslmode=require
```

### 3. Start the Backend Server
```bash
cd backend
uvicorn main:app --reload
```
Navigate to **`http://127.0.0.1:8000/docs`** to view the interactive Swagger UI and test API payloads directly.

### 4. Experience the Dashboard
No frontend build-step required! Simply open `frontend/index.html` in your browser of choice.

---

## 🔮 Future Scope & ML Expansion Roadmap

While V1 utilizes Groq's impressive API for speed, our engineering roadmap for V2 transitions aggressively into bespoke Machine Learning capabilities to widen our competitive moat:

1. **Jupyter Notebook Parameterization & Fine-Tuning** 
   We plan to export our highest-converting historical campaign copies directly back into **Jupyter Notebooks**. Applying `HuggingFace LoRA adapters`, we intend to mathematically fine-tune smaller, local models (`Llama-8B` or `Mistral`) entirely on our "golden dataset," achieving zero-shot superiority without massive API overheads.
2. **Retrieval-Augmented Generation (RAG)**
   Integrating a Vector Database (like Pinecone, or simply utilizing `pgvector` inside our existing Postgres stack) to cross-reference the user's previously generated campaigns. This ensures the LLM generates future templates that rigorously adhere to specific brand-voice vectors.
3. **Sentiment & Conversion Predictive Scoring**
   Routing the generated outputs through a lightweight NLP classifier in PyTorch before rendering on the frontend. This will dynamically provide users with a "Predicted Conversion Score" / "Readability Index," ensuring the campaign copy strikes the optimal emotional cadence. 
4. **Agentic Workflows**
   Scaling our single-node generation into an AI Swarm. For example: A "Writer" agent drafts the copy, while an isolated "Reviewer" agent critiques it against a strict set of marketing heuristics recursively before returning the finalized response to the frontend.
