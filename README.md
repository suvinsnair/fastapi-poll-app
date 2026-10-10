# Pollroom: a Mentimeter clone with FastAPI + SQLAlchemy

A small live-polling app: the presenter creates a question with options,
the audience votes from their phones, and the results screen updates every 2 seconds.

## Project structure

```
mentimeter-clone/
├── database.py      # connects SQLAlchemy to SQLite, gives each request a session
├── models.py        # tables: Question, Option, Answer
├── schemas.py       # Pydantic: what JSON the API accepts and returns
├── crud.py          # functions that read/write the database
├── main.py          # FastAPI app: all the endpoints
├── static/
│   └── index.html   # the UI (plain HTML + JavaScript, no build step)
└── requirements.txt
```

How a request flows through the code:

```
Browser ──HTTP──> main.py (endpoint) ──> schemas.py (validate JSON)
                        │
                        └──> crud.py ──> models.py ──> polls.db (SQLite)
```

## Run it

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

- UI: http://127.0.0.1:8000
- Interactive API docs (Swagger): http://127.0.0.1:8000/docs

`polls.db` is created automatically on first start. Delete the file to start fresh.

### Let students vote from their phones

Run the server on your network and use your laptop's IP address instead of 127.0.0.1:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Students on the same Wi-Fi open `http://<your-laptop-ip>:8000/#/vote/1`.
(Find your IP with `ipconfig` on Windows or `ifconfig` / `ip addr` on Mac/Linux.)

## Endpoints

| Method | URL                                   | What it does                         |
|--------|---------------------------------------|--------------------------------------|
| POST   | `/api/questions`                      | Create a question with its options   |
| GET    | `/api/questions`                      | List all questions                   |
| GET    | `/api/questions/{id}`                 | Get one question with its options    |
| DELETE | `/api/questions/{id}`                 | Delete a question (and its votes)    |
| POST   | `/api/questions/{id}/answers`         | Record a vote                        |
| GET    | `/api/questions/{id}/results`         | Vote counts per option               |
| DELETE | `/api/questions/{id}/answers`         | Reset all votes for a question       |

### Try it with curl

```bash
# create a question
curl -X POST http://127.0.0.1:8000/api/questions \
  -H "Content-Type: application/json" \
  -d '{"text": "Tabs or spaces?", "options": ["Tabs", "Spaces"]}'

# vote for option 1
curl -X POST http://127.0.0.1:8000/api/questions/1/answers \
  -H "Content-Type: application/json" \
  -d '{"option_id": 1}'

# see results
curl http://127.0.0.1:8000/api/questions/1/results
```

Example results response:

```json
{
  "question_id": 1,
  "question": "Tabs or spaces?",
  "total_votes": 3,
  "results": [
    {"option_id": 1, "text": "Tabs",   "votes": 2},
    {"option_id": 2, "text": "Spaces", "votes": 1}
  ]
}
```

## The three UI screens

| URL             | Who sees it            | What it shows                               |
|-----------------|------------------------|---------------------------------------------|
| `/#/`           | Presenter              | Create questions, copy voting links         |
| `/#/vote/1`     | Audience (phones)      | Pick an option and submit                   |
| `/#/results/1`  | Projector              | Live bar chart, refreshes every 2 seconds   |

## Things worth pointing out in the session

- **Models vs schemas**: `models.py` is the database shape, `schemas.py` is the API shape. They look similar but have different jobs.
- **Dependency injection**: `db: Session = Depends(get_db)` gives every request its own database session and closes it afterwards.
- **Validation for free**: send `{"text": "", "options": ["A"]}` and FastAPI returns a 422 with a clear error, without any `if` statements in the endpoint.
- **Never trust the client**: `submit_answer` checks that the option actually belongs to the question (try voting `option_id: 99`).
- **Relationships and cascade**: `question.options` is a Python list, and deleting a question deletes its options and answers.
- **GROUP BY**: `crud.get_results` counts votes with one SQL query instead of looping in Python.

## Exercises for students

1. Add `PUT /api/questions/{id}` to edit a question's text.
2. Add an `is_open` column to `Question` and reject votes when it is `False`.
3. Add a "word cloud" question type where students submit free text instead of choosing an option.
4. Stop one person from voting twice (hint: store a random voter id in the browser and send it with the vote).
