# OrderFlow

A RESTful Order Management API built with **Python, FastAPI, and PostgreSQL**.

## Tech Stack
- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Alembic
- JWT Authentication

## Features
- User registration and login
- Password hashing
- Product management (CRUD)
- Order and order-item management
- Stock validation and updates
- Database relationships
- API validation and error handling
- Database migrations with Alembic

## Installation

```bash
git clone YOUR_REPOSITORY_URL
cd OrderFlow

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

Create a `.env` file and configure your database and JWT secret.

Run database migrations:

```bash
alembic upgrade head
```

Start the server:

```bash
uvicorn main:app --reload
```

## API Documentation

Once the server is running:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

**Developed by Okasha**
