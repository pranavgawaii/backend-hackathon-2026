from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from psycopg_pool import ConnectionPool
from datetime import datetime
import os
from dotenv import load_dotenv
from groq import Groq
from contextlib import asynccontextmanager

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# ── Config ───────────────────────────────────────────────────────────────────
DB_URL       = os.getenv("DATABASE_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not DB_URL:
    print("❌ ERROR: DATABASE_URL not found!")
else:
    safe = DB_URL.split('@')[-1] if '@' in DB_URL else DB_URL
    print(f"✅ DB: ...@{safe}")

if not GROQ_API_KEY:
    print("❌ ERROR: GROQ_API_KEY not found!")
else:
    print(f"✅ Groq key: {GROQ_API_KEY[:8]}...")

# ── Connection Pool (max 3 connections — stays within DigitalOcean limits) ───
pool = ConnectionPool(DB_URL, min_size=1, max_size=3, open=False)

def get_db():
    """Get a connection from the pool."""
    return pool.connection()

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS campaign_copies (
                id SERIAL PRIMARY KEY,
                product TEXT NOT NULL,
                audience TEXT NOT NULL,
                tone TEXT NOT NULL,
                copy TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS followups (
                id SERIAL PRIMARY KEY,
                prospect TEXT NOT NULL,
                last_interaction TEXT NOT NULL,
                days_since INTEGER NOT NULL,
                email TEXT NOT NULL,
                email_content TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)
        conn.execute("ALTER TABLE followups ADD COLUMN IF NOT EXISTS email_content TEXT;")
        conn.commit()
    print("✅ DB tables verified.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open()
    print("✅ Connection pool opened.")
    init_db()
    yield
    pool.close()
    print("✅ Connection pool closed.")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
groq_client = Groq(api_key=GROQ_API_KEY)

# ── Models ────────────────────────────────────────────────────────────────────
class CampaignRequest(BaseModel):
    product: str
    audience: str
    tone: str

class FollowupRequest(BaseModel):
    prospect: str
    last_interaction: str
    days_since: int
    email: str

# ── POST /campaign-copy ───────────────────────────────────────────────────────
@app.post("/campaign-copy")
async def generate_copy(req: CampaignRequest):
    prompt = f"""Write a short, persuasive ad copy (3 sentences max) for:
Product: {req.product}
Target Audience: {req.audience}
Tone: {req.tone}

Return ONLY the ad copy text. Be creative and compelling."""

    try:
        llm_res = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        copy_text = llm_res.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

    try:
        with get_db() as conn:
            row = conn.execute(
                "INSERT INTO campaign_copies (product, audience, tone, copy, created_at) VALUES (%s,%s,%s,%s,%s) RETURNING id",
                (req.product, req.audience, req.tone, copy_text, datetime.utcnow())
            ).fetchone()
            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    return {"id": row[0], "copy": copy_text}

# ── POST /generate-followup ──────────────────────────────────────────────────
@app.post("/generate-followup")
async def generate_followup(req: FollowupRequest):
    prompt = f"""You are a B2B sales professional writing a natural, human-like follow-up email.

Prospect: {req.prospect}
Last Interaction: {req.last_interaction}
Days Since: {req.days_since}

Write a 3-4 line follow-up email. Be friendly, conversational, and include a soft CTA.
Avoid "I wanted to follow up". Do NOT use placeholder brackets.
Return ONLY the email text."""

    try:
        llm_res = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250
        )
        email_text = llm_res.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

    try:
        with get_db() as conn:
            row = conn.execute(
                "INSERT INTO followups (prospect, last_interaction, days_since, email, email_content, created_at) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
                (req.prospect, req.last_interaction, req.days_since, req.email, email_text, datetime.utcnow())
            ).fetchone()
            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    return {"id": row[0], "email_text": email_text}

# ── GET /campaign-copy ────────────────────────────────────────────────────────
@app.get("/campaign-copy")
async def list_copies():
    try:
        with get_db() as conn:
            rows = conn.execute(
                "SELECT id, product, audience, tone, copy, created_at FROM campaign_copies ORDER BY created_at DESC LIMIT 50"
            ).fetchall()
        return [
            {"id": r[0], "product": r[1], "audience": r[2], "tone": r[3], "copy": r[4],
             "created_at": r[5].isoformat() if r[5] else ""}
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

# ── GET /followups ────────────────────────────────────────────────────────────
@app.get("/followups")
async def list_followups():
    try:
        with get_db() as conn:
            rows = conn.execute(
                "SELECT id, prospect, last_interaction, days_since, email, email_content, created_at FROM followups ORDER BY created_at DESC LIMIT 50"
            ).fetchall()
        return [
            {"id": r[0], "prospect": r[1], "last_interaction": r[2], "days_since": r[3],
             "email": r[4], "email_content": r[5] or "", "created_at": r[6].isoformat() if r[6] else ""}
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")
