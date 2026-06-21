# Task Jet

A multi-tenant task management API built with **FastAPI**, **PostgreSQL**, **Redis**, and **Celery**, fully containerized with Docker. Database migrations are managed with **Alembic**.

---

## Tech Stack

| Concern              | Technology                          |
| -------------------- | ----------------------------------- |
| Web framework        | FastAPI + Uvicorn                   |
| Database             | PostgreSQL 16                       |
| ORM                  | SQLAlchemy 2.x                      |
| Migrations           | Alembic                             |
| Cache / broker       | Redis 7                             |
| Background tasks     | Celery                              |
| Auth                 | python-jose (JWT) + passlib (bcrypt)|
| Config               | pydantic-settings                   |
| Containerization     | Docker + Docker Compose             |

---

## Project Structure

```
task_jet/
├── app/
│   ├── api/v1/          # API route handlers (versioned)
│   ├── core/            # Config, database, security
│   │   ├── config.py    # Settings loaded from .env (pydantic-settings)
│   │   ├── database.py  # SQLAlchemy engine, SessionLocal, Base, get_db()
│   │   └── security.py  # Auth/JWT helpers
│   ├── middleware/      # Custom middleware
│   ├── models/          # SQLAlchemy ORM models (User, Tenant, ...)
│   ├── repositories/    # Data-access layer
│   ├── schemas/         # Pydantic request/response schemas
│   ├── services/        # Business logic
│   └── main.py          # FastAPI app entrypoint
├── alembic/             # Migration environment
│   └── versions/        # Generated migration scripts
├── alembic.ini          # Alembic configuration
├── docker-compose.yml   # postgres, redis, api services
├── Dockerfile           # API image (python:3.12-slim)
├── requirements.txt
└── .env                 # Environment variables (not committed)
```

---

## Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose
- (Optional, for local non-Docker dev) Python 3.12+

---

## Environment Variables

A template is provided in [`.env.example`](.env.example). Copy it to `.env` and fill in
your own values:

```powershell
Copy-Item .env.example .env
```

The required variables are documented in `.env.example`. Never commit your real `.env`.

> **Note:** `app/core/config.py` requires `refresh_token_expire_minutes`. Make sure your
> `.env` key is `REFRESH_TOKEN_EXPIRE_MINUTES` (not `..._DAYS`), or the app will fail to start.

The `DATABASE_URL` / `REDIS_URL` hosts (`postgres`, `redis`) are the Docker Compose service
names — they only resolve from inside the Docker network. For local (non-Docker) runs use
`localhost` instead.

---

## Running with Docker

### Start all services
```powershell
docker compose up --build
```

### Start in the background
```powershell
docker compose up -d --build
```

### Stop services
```powershell
docker compose down
```

### Stop and wipe the database volume
```powershell
docker compose down -v
```

### View logs
```powershell
docker compose logs -f api
```

The API runs with `--reload`, and the project root is mounted into the container
(`.:/app` in `docker-compose.yml`), so code changes on the host hot-reload automatically.

Once up, the API is available at:

- API root: http://localhost:8000
- Health check: http://localhost:8000/health
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Database Migrations (Alembic)

Run Alembic commands inside the `api` container so they use the container's environment
and can reach the `postgres` service.

### Create a new migration (autogenerate from models)
```powershell
docker compose run --rm api alembic revision --autogenerate -m "describe your change"
```

### Apply migrations
```powershell
docker compose run --rm api alembic upgrade head
```

### Roll back the last migration
```powershell
docker compose run --rm api alembic downgrade -1
```

### Show current revision / history
```powershell
docker compose run --rm api alembic current
docker compose run --rm api alembic history
```

### Re-initialize the migration environment (already done)
```powershell
docker compose run --rm api alembic init alembic
```

> For autogenerate to detect all tables, `alembic/env.py` must import a single shared
> `Base` and set `target_metadata = Base.metadata`, and every model module must be
> imported so its tables register on that `Base`.

---

## Useful Container Commands

### Open a shell in the API container
```powershell
docker compose run --rm api bash
```

### Run an arbitrary command
```powershell
docker compose run --rm api python -c "import app.main; print('ok')"
```

### Connect to Postgres via psql
```powershell
docker compose exec postgres psql -U task_jet_user -d task_jet_db
```

### Connect to Redis CLI
```powershell
docker compose exec redis redis-cli
```

---

## Local Development (without Docker)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Set `.env` hosts to `localhost`, then run:

```powershell
uvicorn app.main:app --reload
```

---

## Command Cheat Sheet

Every command used while working on this project, in one place.

### Environment setup
```powershell
# Copy the env template and fill in values
Copy-Item .env.example .env

# (Local, non-Docker) create and activate a virtualenv, install deps
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

### Docker Compose
```powershell
docker compose up --build           # build + start all services (foreground)
docker compose up -d --build        # build + start in background
docker compose up -d postgres       # start only postgres
docker compose down                 # stop services (keeps volumes)
docker compose down -v              # stop services + delete volumes (wipes DB)
docker compose logs -f api          # follow API logs
docker compose ps                   # list running services
docker compose run --rm api bash    # one-off shell in the api container
docker compose exec postgres psql -U task_jet_user -d task_jet_db   # psql shell
docker compose exec postgres psql -U task_jet_user -d task_jet_db -c "\dt"        # list tables
docker compose exec postgres psql -U task_jet_user -d task_jet_db -c "\d users"   # describe the users table
docker compose exec redis redis-cli # redis shell
```

### Alembic (run inside the api container)
```powershell
docker compose run --rm api alembic init alembic                                  # initialize migration env (one-time)
docker compose run --rm api alembic revision --autogenerate -m "create tenants and users"  # new migration from models
docker compose run --rm api alembic upgrade head                                  # apply all migrations
docker compose run --rm api alembic downgrade -1                                  # roll back one migration
docker compose run --rm api alembic current                                       # show current revision
docker compose run --rm api alembic history                                       # show migration history
```

### Run the API locally (without Docker)
```powershell
uvicorn app.main:app --reload
```

### Git
```powershell
git checkout -b chore/dev-environment   # create a working branch
```

---

## Troubleshooting

**`password authentication failed for user "task_jet_user"`**
Postgres only applies `POSTGRES_USER` / `POSTGRES_PASSWORD` when it first initializes an
empty data directory. If you changed the password after the `postgres_data` volume was
created, the old credentials persist. Recreate the volume:
```powershell
docker compose down -v
docker compose up -d postgres
```
Avoid URL-special characters (`@ : / ? # %`) in `POSTGRES_PASSWORD`, or URL-encode them in
`DATABASE_URL` (e.g. `@` → `%40`).

**`alembic init` files don't appear on the host**
The container's working directory (`/app`) must be bind-mounted to the host. `docker-compose.yml`
mounts `.:/app` for the `api` service so generated files land in your project root.

**`Import "sqlalchemy..." could not be resolved` in the editor**
The dependencies aren't installed in the interpreter your editor is using. Create a local
virtualenv and install `requirements.txt` (see *Environment setup*), then select
`.venv` as the Python interpreter.

---

## API Endpoints

| Method | Path      | Description           |
| ------ | --------- | --------------------- |
| GET    | `/health` | Service health check  |

More endpoints will be added under `app/api/v1/`.
