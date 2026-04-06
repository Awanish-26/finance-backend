## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- JWT auth (python-jose)

## Setup

1. Create virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Copy env template:

```bash
copy .env.example .env
```

create finance.db in root directory

3. Seed demo data:

```bash
python seed.py
```

4. Run server:

```bash
uvicorn app.main:app --reload
```

## Demo Credentials

- `admin@example.com` / `Admin@123`
- `analyst@example.com` / `Analyst@123`
- `viewer@example.com` / `Viewer@123`

## API Overview

### Auth

- `POST /api/auth/login`
- `GET /api/auth/me`

### Users

- `POST /api/users` (admin only)
- `GET /api/users` (admin only)
- `GET /api/users/{user_id}` (self or admin)
- `PATCH /api/users/{user_id}` (self for name; admin for role/status)
- `DELETE /api/users/{user_id}` (admin only, sets inactive)

### Records

- `POST /api/records` (analyst/admin)
- `GET /api/records`
- `GET /api/records/{record_id}`
- `PATCH /api/records/{record_id}` (owner analyst/admin)
- `DELETE /api/records/{record_id}` (soft delete)

### Summaries

- `GET /api/summaries/totals`
- `GET /api/summaries/by-category`
- `GET /api/summaries/recent`
- `GET /api/summaries/trends`
