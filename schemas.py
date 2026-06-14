from pydantic import BaseModel
from sqlmodel import SQLModel, Field

# ── Groq Table ──
class GroqTranslation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    original_text: str
    translation: str
    source_lang: str
    target_lang: str
    created_at: str
    time_taken: str
    model_used: str

# ── Zen Table ──
class ZenTranslation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    original_text: str
    translation: str
    source_lang: str
    target_lang: str
    created_at: str
    time_taken: str
    model_used: str

# ── Comparison Table (3rd database) ──
class ComparisonResult(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    groq_id: int
    zen_id: int
    groq_time: str
    zen_time: str
    winner: str

# ── Input Models ──
class Model_Input(BaseModel):
    original_text: str
    source_lang: str
    target_lang: str

class Model_Output(BaseModel):
    id: int
    original_text: str
    translation: str
    source_lang: str
    target_lang: str
    created_at: str
    time_taken: str
    model_used: str

# ── Compare Input — sirf 2 IDs ──
class CompareInput(BaseModel):
    groq_id: int
    zen_id: int