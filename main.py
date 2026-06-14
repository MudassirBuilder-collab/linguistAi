from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles  # --- Added for frontend connection ---
from fastapi.responses import FileResponse  # --- Added for frontend connection ---
from fastapi.middleware.cors import CORSMiddleware  # --- Added for frontend connection ---
from pydantic import BaseModel
from schemas import (
    Model_Input, Model_Output,
    GroqTranslation, ZenTranslation,
    ComparisonResult, CompareInput
)
from database import (
    create_db, get_groq_session, get_zen_session, get_compare_session
)
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from groq import Groq
from sqlmodel import Session, select
from datetime import datetime
import os

# Setup
load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://opencode.ai/zen/v1",
    model="deepseek-v4-flash-free",
    max_tokens=100,
    temperature=0
)

app = FastAPI()
create_db()

# --- Added for frontend connection ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/Statics", StaticFiles(directory="Statics"), name="statics")


@app.get("/")
def root():
    return FileResponse("Statics/index.html")


# ── Time calculate karne ka function ──
def calculate_time(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes} min {secs:.2f} sec"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours} hr {minutes} min"


# Helper — time string ko seconds mein convert karo (compare ke liye)
def time_to_seconds(time_str: str) -> float:
    if "seconds" in time_str:
        return float(time_str.split()[0])
    elif "min" in time_str:
        parts = time_str.split()
        return int(parts[0]) * 60 + float(parts[2])
    elif "hr" in time_str:
        parts = time_str.split()
        return int(parts[0]) * 3600 + int(parts[2]) * 60
    return 0.0


# =====================================
# GROQ ENDPOINTS
# =====================================

import time  # ← top pe add karo

@app.post("/ask", response_model=Model_Output)
def ask_llm_groq(translate_message: Model_Input, session: Session = Depends(get_groq_session)):
    start_time = datetime.now()

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": f"Just translate from {translate_message.source_lang} to {translate_message.target_lang}: {translate_message.original_text}"}
        ],
    )
    answer_text = response.choices[0].message.content

    time.sleep(0)  

    time_taken = calculate_time((datetime.now() - start_time).total_seconds())

    record = GroqTranslation(
        original_text=translate_message.original_text,
        translation=answer_text,
        source_lang=translate_message.source_lang,
        target_lang=translate_message.target_lang,
        created_at=start_time.strftime("%Y-%m-%d %H:%M:%S"),
        time_taken=time_taken,
        model_used="Groq (LLaMA)"
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record

@app.get("/history")
def get_groq_history(session: Session = Depends(get_groq_session)):
    records = session.exec(select(GroqTranslation)).all()
    return records


@app.delete("/history/{id}")
def delete_groq_one(id: int, session: Session = Depends(get_groq_session)):
    record = session.get(GroqTranslation, id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    session.delete(record)
    session.commit()
    return {"message": f"Groq record with ID {id} deleted successfully"}


@app.delete("/history/all/clear")
def delete_groq_all(session: Session = Depends(get_groq_session)):
    records = session.exec(select(GroqTranslation)).all()
    for record in records:
        session.delete(record)
    session.commit()
    return {"message": "All Groq history deleted successfully"}


# =====================================
# ZEN ENDPOINTS
# =====================================
@app.post("/ask/zen", response_model=Model_Output)
async def ask_llm_zen(translate_message: Model_Input, session: Session = Depends(get_zen_session)):
    start_time = datetime.now()

    response = llm.invoke(
        f"Just translate from {translate_message.source_lang} to {translate_message.target_lang}: {translate_message.original_text}. Just translate word by word, don't add extra lines"
    )
    answer_text = response.content  # ← yeh line missing thi!

    time_taken = calculate_time((datetime.now() - start_time).total_seconds())

    record = ZenTranslation(
        original_text=translate_message.original_text,
        translation=answer_text,
        source_lang=translate_message.source_lang,
        target_lang=translate_message.target_lang,
        created_at=start_time.strftime("%Y-%m-%d %H:%M:%S"),
        time_taken=time_taken,
        model_used="Zen (DeepSeek)"
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record

@app.get("/history/zen")
def get_zen_history(session: Session = Depends(get_zen_session)):
    records = session.exec(select(ZenTranslation)).all()
    return records


@app.delete("/history/zen/{id}")
def delete_zen_one(id: int, session: Session = Depends(get_zen_session)):
    record = session.get(ZenTranslation, id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    session.delete(record)
    session.commit()
    return {"message": f"Zen record with ID {id} deleted successfully"}


@app.delete("/history/zen/all/clear")
def delete_zen_all(session: Session = Depends(get_zen_session)):
    records = session.exec(select(ZenTranslation)).all()
    for record in records:
        session.delete(record)
    session.commit()
    return {"message": "All Zen history deleted successfully"}


# =====================================
# COMPARISON ENDPOINTS (3rd database)
# =====================================

# ── Compare — IDs leke history se time uthao, save karo ──
@app.post("/compare", response_model=ComparisonResult)
def compare(
    data: CompareInput,
    groq_session: Session = Depends(get_groq_session),
    zen_session: Session = Depends(get_zen_session),
    compare_session: Session = Depends(get_compare_session)
):
    # Groq history se record uthao
    groq_record = groq_session.get(GroqTranslation, data.groq_id)
    if not groq_record:
        raise HTTPException(status_code=404, detail="Groq record not found")

    # Zen history se record uthao
    zen_record = zen_session.get(ZenTranslation, data.zen_id)
    if not zen_record:
        raise HTTPException(status_code=404, detail="Zen record not found")

    # Dono ka time seconds mein convert karo
    groq_seconds = time_to_seconds(groq_record.time_taken)
    zen_seconds = time_to_seconds(zen_record.time_taken)

    # Winner decide karo
    winner = "Groq" if groq_seconds < zen_seconds else "Zen"

    # Result save karo
    result = ComparisonResult(
        groq_id=data.groq_id,
        zen_id=data.zen_id,
        groq_time=groq_record.time_taken,
        zen_time=zen_record.time_taken,
        winner=winner
    )
    compare_session.add(result)
    compare_session.commit()
    compare_session.refresh(result)
    return result


# ── Comparison History ──
@app.get("/compare/history")
def get_compare_history(session: Session = Depends(get_compare_session)):
    records = session.exec(select(ComparisonResult)).all()
    return records


# ── Delete one comparison ──
@app.delete("/compare/{id}")
def delete_compare_one(id: int, session: Session = Depends(get_compare_session)):
    record = session.get(ComparisonResult, id)
    if not record:
        raise HTTPException(status_code=404, detail="Comparison record not found")
    session.delete(record)
    session.commit()
    return {"message": f"Comparison record with ID {id} deleted successfully"}


# ── Delete all comparisons ──
@app.delete("/compare/all/clear")
def delete_compare_all(session: Session = Depends(get_compare_session)):
    records = session.exec(select(ComparisonResult)).all()
    for record in records:
        session.delete(record)
    session.commit()
    return {"message": "All comparison history deleted successfully"}