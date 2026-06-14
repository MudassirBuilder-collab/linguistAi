# LinguistAI — Personal Translator

> A FastAPI-powered translation app with dual AI engines (Groq + Zen AI), history tracking, and side-by-side comparison.

**Student:** [Your Name]  
**Roll Number:** [Your Roll Number]

---

## Problem Statement

Build a personal translation tool where users can:
- Translate text using two different AI models (Groq LLaMA and Zen AI DeepSeek)
- View translation history with time taken for each request
- Compare the performance of both models side-by-side
- Delete individual records or clear all history

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI |
| Database | SQLite 3 via SQLModel |
| AI Engine 1 | Groq SDK (LLaMA 3.3 70B) |
| AI Engine 2 | LangChain + ChatOpenAI (Zen AI / DeepSeek) |
| Frontend | HTML, TailwindCSS (CDN), vanilla JS |
| Server | Uvicorn |

---

## Project Structure

```
Project/
├── main.py                  # FastAPI app — all endpoints
├── schemas.py               # SQLModel tables + Pydantic input models
├── database.py              # Engines and session generators (3 DBs)
├── requirements.txt         # Python dependencies
├── .env                     # API keys (not committed)
├── .env.example             # Template for .env
│
├── Statics/
│   └── index.html           # Frontend UI
│
├── groq_translator.db       # Groq translation history (auto-generated)
├── zen_translator.db        # Zen translation history (auto-generated)
├── comparison.db            # Comparison results (auto-generated)
│
├── .venv/                   # Virtual environment
├── learn.md                 # Key concepts & code snippets
└── README.md                # This file
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repo-url>
cd Project
```

### 2. Create virtual environment & activate

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and fill in your keys:

```env
GROQ_API_KEY=gsk_your_groq_api_key_here
OPENAI_API_KEY=your_openai_compatible_api_key_here
```

### 5. Run the server

```bash
uvicorn main:app --reload
```

### 6. Open in browser

Navigate to **http://localhost:8000/**

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | API key for Groq Cloud (LLaMA model) |
| `OPENAI_API_KEY` | Yes | API key for Zen AI (OpenAI-compatible endpoint) |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serve the frontend UI (index.html) |
| `POST` | `/ask` | Translate text using Groq (LLaMA) |
| `GET` | `/history` | Get all Groq translations |
| `DELETE` | `/history/{id}` | Delete one Groq record by ID |
| `DELETE` | `/history/all/clear` | Delete all Groq records |
| `POST` | `/ask/zen` | Translate text using Zen AI (DeepSeek) |
| `GET` | `/history/zen` | Get all Zen AI translations |
| `DELETE` | `/history/zen/{id}` | Delete one Zen record by ID |
| `DELETE` | `/history/zen/all/clear` | Delete all Zen records |
| `POST` | `/compare` | Compare a Groq record vs a Zen record by ID |
| `GET` | `/compare/history` | Get all comparison results |
| `DELETE` | `/compare/{id}` | Delete one comparison record by ID |
| `DELETE` | `/compare/all/clear` | Delete all comparison records |

---

## Sample Requests & Responses

### POST /ask (Groq)

**Request:**
```json
{
  "original_text": "Hello, how are you?",
  "source_lang": "English",
  "target_lang": "Spanish"
}
```

**Response:**
```json
{
  "id": 1,
  "original_text": "Hello, how are you?",
  "translation": "Hola, ¿cómo estás?",
  "source_lang": "English",
  "target_lang": "Spanish",
  "created_at": "2025-06-14 12:30:00",
  "time_taken": "6.25 seconds",
  "model_used": "Groq (LLaMA)"
}
```

### POST /ask/zen (Zen AI)

**Request:**
```json
{
  "original_text": "Good morning, world!",
  "source_lang": "English",
  "target_lang": "French"
}
```

**Response:**
```json
{
  "id": 2,
  "original_text": "Good morning, world!",
  "translation": "Bonjour le monde !",
  "source_lang": "English",
  "target_lang": "French",
  "created_at": "2025-06-14 12:31:00",
  "time_taken": "2.10 seconds",
  "model_used": "Zen (DeepSeek)"
}
```

### POST /compare

**Request:**
```json
{
  "groq_id": 1,
  "zen_id": 2
}
```

**Response:**
```json
{
  "id": 1,
  "groq_id": 1,
  "zen_id": 2,
  "groq_time": "6.25 seconds",
  "zen_time": "2.10 seconds",
  "winner": "Zen"
}
```

---

## Coming Soon

### Smart Input Analyzer

The app will detect whether you typed a **single word**, a **sentence**, or a **paragraph** and automatically adjust the AI prompt accordingly. Short inputs get word-by-word translation, long paragraphs get full-context translation — no manual mode switching.

### AI Accuracy Checker

After translating, a second AI model will review the output and give an **accuracy score** (0-100%) with a visual chart. If the score is low, the app will auto-request a better translation.

### Multi-Language Translation

Translate one input into **multiple target languages at once** — for example, type in English and get Spanish, French, German, and Urdu translations in a single request.
