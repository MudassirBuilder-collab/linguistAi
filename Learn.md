# LinguistAI — Key Concepts & Code Snippets

All code snippets below are taken directly from my project files. You can copy, adapt, or upgrade them for your own use — they're working examples, not just theory.

---

## 1. Groq SDK Direct Call

```python
response = groq_client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": f"Just translate from {translate_message.source_lang} to {translate_message.target_lang}: {translate_message.original_text}"}
    ],
)
answer_text = response.choices[0].message.content
```

We call Groq's API directly using their Python SDK. The response object has a `.choices[0].message.content` path to grab the generated text. ⚡

**Output example:**
```json
{
  "translation": "Hola, ¿cómo estás?",
  "model_used": "Groq (LLaMA)",
  "time_taken": "6.25 seconds"
}
```

---

## 2. LangChain ChatOpenAI — Zen AI Setup

```python
llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://opencode.ai/zen/v1",
    model="DeepSeek V4 Flash Free",
    max_tokens=100,
    temperature=0
)
```

We use LangChain's `ChatOpenAI` class but point it to a custom `base_url` (Zen AI) instead of OpenAI's servers. `temperature=0` makes responses deterministic, and `max_tokens=100` keeps translations short. 🚀

---

## 3. SQLModel Table Definition

```python
class GroqTranslation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    original_text: str
    translation: str
    source_lang: str
    target_lang: str
    created_at: str
    time_taken: str
    model_used: str
```

SQLModel combines Pydantic + SQLAlchemy — one class acts as both a **request schema** and a **database table**. Set `table=True` to tell SQLModel to create a DB table for it. We have three tables: `GroqTranslation`, `ZenTranslation`, and `ComparisonResult`. ✅

---

## 4. Depends + Session Pattern

```python
from sqlmodel import Session, select

def get_groq_session():
    with Session(groq_engine) as session:
        yield session

# Used in endpoints like:
@app.post("/ask", response_model=Model_Output)
def ask_llm_groq(translate_message: Model_Input, session: Session = Depends(get_groq_session)):
    ...
```

FastAPI's `Depends()` injects a fresh database session into every request. The `yield` pattern ensures the session is properly closed after the request ends. We have three separate SQLite databases, so three separate session generators. 🗄️

---

## 5. Time Tracking Helper

```python
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
```

We record `datetime.now()` before and after the API call, subtract them to get elapsed seconds, then format the result into a human-readable string. Used in every translate endpoint. ⏱️

---

## 6. HTTPException for 404 Errors

```python
record = session.get(GroqTranslation, id)
if not record:
    raise HTTPException(status_code=404, detail="Record not found")
session.delete(record)
session.commit()
```

When a user tries to delete a record that doesn't exist, we raise `HTTPException` with status 404. FastAPI automatically returns a proper JSON error response instead of crashing. Used in all delete endpoints. ❌

**Output example:**
```json
{
  "detail": "Record not found"
}
```

---

## 7. async/await in FastAPI

```python
@app.post("/ask/zen", response_model=Model_Output)
async def ask_llm_zen(translate_message: Model_Input, session: Session = Depends(get_zen_session)):
    ...
    response = llm.invoke(...)
    answer_text = response.content
```

The Zen endpoint is `async` because LangChain's `.invoke()` can be awaited. The Groq endpoint is synchronous (`def`) because the Groq SDK is used with `.create()`. FastAPI supports both — sync endpoints run in a thread pool automatically. 🔄

---

## 8. Compare Logic — Two Records, One Winner

```python
@app.post("/compare", response_model=ComparisonResult)
def compare(data: CompareInput, groq_session, zen_session, compare_session):
    groq_record = groq_session.get(GroqTranslation, data.groq_id)
    zen_record = zen_session.get(ZenTranslation, data.zen_id)

    groq_seconds = time_to_seconds(groq_record.time_taken)
    zen_seconds = time_to_seconds(zen_record.time_taken)

    winner = "Groq" if groq_seconds < zen_seconds else "Zen"

    result = ComparisonResult(
        groq_id=data.groq_id, zen_id=data.zen_id,
        groq_time=groq_record.time_taken, zen_time=zen_record.time_taken,
        winner=winner
    )
    compare_session.add(result)
    compare_session.commit()
    return result
```

This endpoint accepts two IDs (one Groq, one Zen), fetches both records from their respective databases, converts their time strings to seconds, picks the faster one as winner, and saves the result to a third `comparison.db` database. ⚔️

**Output example:**
```json
{
  "id": 1,
  "groq_id": 3,
  "zen_id": 5,
  "groq_time": "6.25 seconds",
  "zen_time": "2.10 seconds",
  "winner": "Zen"
}
```

---

## 9. Frontend-Backend Connection

```python
# 1. CORS — allows browser to call API from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Mount static files — makes Statics/ folder accessible
app.mount("/Statics", StaticFiles(directory="Statics"), name="statics")

# 3. Root route — serves the HTML when you visit /
@app.get("/")
def root():
    return FileResponse("Statics/index.html")
```

Three things are needed to connect the frontend to the backend:

1. **CORS Middleware** — browsers block cross-origin requests by default. Since the frontend and backend run on the same server but different routes, CORS needs to allow it. `allow_origins=["*"]` means any origin can call our API (fine for local dev).

2. **StaticFiles Mount** — makes all files inside the `Statics/` folder accessible at `http://localhost:8000/Statics/...`. If we had CSS/images/JS files, they'd be served from here.

3. **Root Route** — when you visit `http://localhost:8000/`, FastAPI returns `index.html`. Without this, you'd see a 404 or have to manually open the HTML file. 🌐

---

## What I Used

| Concept | Where Used | Why Used |
|---|---|---|
| Groq SDK | `POST /ask` | Call LLaMA 3.3 model for translation |
| LangChain ChatOpenAI | `POST /ask/zen` | Call Zen AI (DeepSeek) via OpenAI-compatible API |
| SQLModel | `schemas.py` tables | Define DB tables + Pydantic schemas in one class |
| FastAPI Depends | All endpoints using DB | Inject database sessions automatically |
| `calculate_time()` | `/ask`, `/ask/zen` | Format elapsed seconds into readable time |
| `HTTPException` | All delete endpoints | Return proper 404 JSON when record missing |
| `async/await` | `POST /ask/zen` | Handle non-blocking API call to Zen AI |
| 3-database compare | `POST /compare` | Fetch from two DBs, compare times, save to third |
| CORS + StaticFiles + FileResponse | `main.py` setup | Serve HTML frontend from same FastAPI server |
