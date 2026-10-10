"""
crud.py - functions that Create, Read, Update and Delete rows.

The endpoints in main.py call these functions, so all the database
code sits in one place and main.py stays short and readable.
"""
from sqlalchemy import func
from sqlalchemy.orm import Session

import models
import schemas


# ---------- Questions ----------

def create_question(db: Session, data: schemas.QuestionCreate) -> models.Question:
    question = models.Question(text=data.text)
    for option_text in data.options:
        # Appending to question.options sets option.question_id for us.
        question.options.append(models.Option(text=option_text))

    db.add(question)
    db.commit()           # save to the database
    db.refresh(question)  # reload to get the new id and created_at
    return question


def get_questions(db: Session) -> list[models.Question]:
    return db.query(models.Question).order_by(models.Question.id.desc()).all()


def get_question(db: Session, question_id: int) -> models.Question | None:
    return db.get(models.Question, question_id)


def delete_question(db: Session, question: models.Question) -> None:
    db.delete(question)  # options and answers go too (cascade in models.py)
    db.commit()


# ---------- Answers ----------

def create_answer(db: Session, question_id: int, option_id: int) -> models.Answer:
    answer = models.Answer(question_id=question_id, option_id=option_id)
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer


def delete_answers(db: Session, question_id: int) -> None:
    db.query(models.Answer).filter(models.Answer.question_id == question_id).delete()
    db.commit()


def get_results(db: Session, question: models.Question) -> dict:
    """
    Count the votes for each option. The SQL behind this is roughly:

        SELECT option_id, COUNT(id) FROM answers
        WHERE question_id = ? GROUP BY option_id;
    """
    rows = (
        db.query(models.Answer.option_id, func.count(models.Answer.id))
        .filter(models.Answer.question_id == question.id)
        .group_by(models.Answer.option_id)
        .all()
    )
    votes_by_option = dict(rows)  # e.g. {1: 4, 3: 2}; options with 0 votes are missing

    results = [
        {"option_id": option.id, "text": option.text, "votes": votes_by_option.get(option.id, 0)}
        for option in question.options
    ]
    return {
        "question_id": question.id,
        "question": question.text,
        "total_votes": sum(r["votes"] for r in results),
        "results": results,
    }
