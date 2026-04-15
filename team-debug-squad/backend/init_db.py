import psycopg2

import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
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
    print("Table ensured.")
except Exception as e:
    print("Error:", e)
finally:
    if 'cur' in locals(): cur.close()
    if 'conn' in locals(): conn.close()
