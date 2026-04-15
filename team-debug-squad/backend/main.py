from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg
from datetime import datetime
import os
from dotenv import load_dotenv
from groq import Groq
from contextlib import asynccontextmanager

load_dotenv()

# Database connection
DB_URL = os.getenv("DATABASE_URL")

def get_db():
    return psycopg.connect(DB_URL)

def init_db():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS campaign_copies (
                id SERIAL PRIMARY KEY,
                product VARCHAR(255) NOT NULL,
                audience VARCHAR(255) NOT NULL,
                tone VARCHAR(100) NOT NULL,
                copy TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL
            );
            """)
        conn.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class CampaignRequest(BaseModel):
    product: str
    audience: str
    tone: str

@app.post("/campaign-copy")
async def generate_copy(req: CampaignRequest):
    # LLM prompt
    prompt = f"""Write a short ad copy (max 3 sentences) for:
Product: {req.product}
Target audience: {req.audience}
Tone: {req.tone}

Be creative and persuasive."""

    try:
        # Call Groq
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        
        copy_text = response.choices[0].message.content.strip()
        
        # Save to DB
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO campaign_copies (product, audience, tone, copy, created_at) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (req.product, req.audience, req.tone, copy_text, datetime.utcnow())
        )
        copy_id = cur.fetchone()[0]
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
    
    return {"id": copy_id, "copy": copy_text}

@app.get("/campaign-copy")
async def list_copies():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, product, audience, tone, copy, created_at FROM campaign_copies ORDER BY created_at DESC LIMIT 50")
        rows = cur.fetchall()
        
        return [
            {
                "id": r[0],
                "product": r[1],
                "audience": r[2],
                "tone": r[3],
                "copy": r[4],
                "created_at": r[5].isoformat()
            }
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
