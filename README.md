# URL Shortener + Analytics API

A URL shortening service with Redis-backed caching and rate limiting, built with FastAPI, PostgreSQL, and Redis.

## Features
- Shorten long URLs into base62-encoded short codes
- Redirect from short code to original URL
- Click tracking / analytics per short URL
- Redis caching (cache-aside pattern with TTL) for fast repeat redirects
- Redis-based rate limiting on URL creation
- Automated tests with pytest

## Tech Stack
- **Backend:** FastAPI, SQLAlchemy, Pydantic
- **Database:** PostgreSQL (Dockerized)
- **Cache/Rate Limiting:** Redis (Dockerized)
- **Testing:** pytest

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|--------------|
| GET | /health | Health check |
| POST | /shorten | Create a short URL (rate-limited) |
| GET | /{short_code} | Redirect to original URL |
| GET | /stats/{short_code} | View click analytics for a short URL |

## Key Design Notes
- Short codes are generated via base62 encoding of the database auto-increment ID — guarantees uniqueness with no separate collision checks needed.
- Redirect lookups use a cache-aside pattern: check Redis first, fall back to Postgres on a miss, then populate the cache (1-hour TTL).
- Rate limiting uses a Redis counter per client IP with a 60-second expiring window (5 requests/minute).

## Running Locally
1. Clone the repo
2. Create a virtual environment and install dependencies:

python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic pytest httpx redis

3. Start PostgreSQL and Redis via Docker:

docker run --name url-db -e POSTGRES_PASSWORD=devpass -e POSTGRES_DB=urldb -p 5556:5432 -d postgres
docker run --name url-redis -p 6379:6379 -d redis

4. Run the server:

uvicorn main:app --reload --port 8001

5. Visit `http://localhost:8001/docs` for interactive API docs.

## Running Tests

docker exec -it url-redis redis-cli FLUSHALL
pytest test_main.py -v


## Notes
Built as part of a structured backend engineering learning plan, focused on caching strategy and rate limiting patterns commonly tested in backend interviews.