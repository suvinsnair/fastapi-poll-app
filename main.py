"""
main.py - the FastAPI app. Every URL the API offers is defined here.

Run:   uvicorn main:app --reload
Open:  http://127.0.0.1:8000        -> the UI
       http://127.0.0.1:8000/docs   -> interactive API docs (try every endpoint)
"""
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import engine, get_db

# Create the tables in polls.db if they don't exist yet.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mentimeter Clone",
    description="Create questions with options, collect votes, and see live results.",
)

STATIC_DIR = Path(__file__).parent / "static"


@app.get("/", include_in_schema=False)
def home():
    """Serve the single-page UI."""
    return FileResponse(STATIC_DIR / "index.html")


def get_question_or_404(db: Session, question_id: int) -> models.Question:
    question = crud.get_question(db, question_id)
    if question is None:
        raise HTTPException(status_code=404, detail=f"Question {question_id} not found")
    return question


# ---------- Questions ----------

@app.post("/api/questions", response_model=schemas.QuestionOut, status_code=201, tags=["Questions"])
def create_question(payload: schemas.QuestionCreate, db: Session = Depends(get_db)):
    """Create a question together with its options."""
    return crud.create_question(db, payload)


@app.get("/api/questions", response_model=list[schemas.QuestionOut], tags=["Questions"])
def list_questions(db: Session = Depends(get_db)):
    """List every question, newest first."""
    return crud.get_questions(db)


@app.get("/api/questions/{question_id}", response_model=schemas.QuestionOut, tags=["Questions"])
def read_question(question_id: int, db: Session = Depends(get_db)):
    """Get one question and its options (the voting page uses this)."""
    return get_question_or_404(db, question_id)


@app.delete("/api/questions/{question_id}", status_code=204, tags=["Questions"])
def delete_question(question_id: int, db: Session = Depends(get_db)):
    """Delete a question, its options and all its answers."""
    question = get_question_or_404(db, question_id)
    crud.delete_question(db, question)


# ---------- Answers ----------

@app.post(
    "/api/questions/{question_id}/answers",
    response_model=schemas.AnswerOut,
    status_code=201,
    tags=["Answers"],
)
def submit_answer(question_id: int, payload: schemas.AnswerCreate, db: Session = Depends(get_db)):
    """Record one vote for an option of this question."""
    question = get_question_or_404(db, question_id)

    # Don't trust the client: the option must belong to THIS question.
    valid_option_ids = [option.id for option in question.options]
    if payload.option_id not in valid_option_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Option {payload.option_id} is not an option of question {question_id}",
        )

    return crud.create_answer(db, question_id, payload.option_id)


@app.get(
    "/api/questions/{question_id}/results",
    response_model=schemas.QuestionResults,
    tags=["Answers"],
)
def read_results(question_id: int, db: Session = Depends(get_db)):
    """Vote count for every option."""
    question = get_question_or_404(db, question_id)
    return crud.get_results(db, question)


@app.delete("/api/questions/{question_id}/answers", status_code=204, tags=["Answers"])
def reset_answers(question_id: int, db: Session = Depends(get_db)):
    """Remove all votes for a question (handy before running it again)."""
    get_question_or_404(db, question_id)
    crud.delete_answers(db, question_id)
