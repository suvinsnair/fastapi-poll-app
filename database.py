"""
database.py - connects SQLAlchemy to the database.

We use SQLite, so the whole database is one file (polls.db) created next
to this code the first time the app starts. Nothing extra to install.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./polls.db"

# The engine is the actual connection to the database.
# check_same_thread=False is needed only for SQLite, because FastAPI
# may handle one request across different threads.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal() gives us a new "session": a workspace where we read rows,
# add rows, and finally commit (save) our changes.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Every model (table) in models.py inherits from Base.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency: opens a session for one request and always
    closes it afterwards, even if the request fails.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
