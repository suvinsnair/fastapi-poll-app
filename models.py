"""
models.py - the database tables, written as Python classes.

    questions                 options                    answers
    ---------                 -------                    -------
    id                        id                         id
    text           1 ---< *   text                       question_id
    created_at                question_id   1 ---< *   option_id
                                                         created_at

- One Question has many Options.
- Every vote is one row in Answers, pointing at the question and the option chosen.
"""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(200), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # question.options -> list of Option objects.
    # cascade="all, delete-orphan" means: delete a question and its
    # options and answers are deleted too.
    options = relationship(
        "Option",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="Option.id",
    )
    answers = relationship(
        "Answer", back_populates="question", cascade="all, delete-orphan"
    )


class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(100), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)

    question = relationship("Question", back_populates="options")
    answers = relationship(
        "Answer", back_populates="option", cascade="all, delete-orphan"
    )


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    option_id = Column(Integer, ForeignKey("options.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    question = relationship("Question", back_populates="answers")
    option = relationship("Option", back_populates="answers")
