from sqlmodel import SQLModel, create_engine, Session

groq_engine = create_engine("sqlite:///groq_translator.db")
zen_engine = create_engine("sqlite:///zen_translator.db")
compare_engine = create_engine("sqlite:///comparison.db")

def create_db():
    SQLModel.metadata.create_all(groq_engine)
    SQLModel.metadata.create_all(zen_engine)
    SQLModel.metadata.create_all(compare_engine)

def get_groq_session():
    with Session(groq_engine) as session:
        yield session

def get_zen_session():
    with Session(zen_engine) as session:
        yield session

def get_compare_session():
    with Session(compare_engine) as session:
        yield session