from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import URL
from schemas import URLCreate, URLOut
from shortener import encode

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/shorten", response_model=URLOut)
def shorten_url(url: URLCreate, db: Session = Depends(get_db)):
    new_url = URL(original_url=url.original_url, short_code="")
    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    new_url.short_code = encode(new_url.id)
    db.commit()
    db.refresh(new_url)

    redis_client.set(new_url.short_code, new_url.original_url, ex=3600)

    return new_url

from cache import redis_client

@app.get("/{short_code}")
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    cached_url = redis_client.get(short_code)

    if cached_url:
        # Cache hit — skip the database entirely
        url_entry = db.query(URL).filter(URL.short_code == short_code).first()
        if url_entry:
            url_entry.clicks += 1
            db.commit()
        return RedirectResponse(url=cached_url)

    # Cache miss — fall back to Postgres
    url_entry = db.query(URL).filter(URL.short_code == short_code).first()
    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")

    url_entry.clicks += 1
    db.commit()

    # Store in cache for next time, expire after 1 hour
    redis_client.set(short_code, url_entry.original_url, ex=3600)

    return RedirectResponse(url=url_entry.original_url)



@app.get("/stats/{short_code}", response_model=URLOut)
def get_stats(short_code: str, db: Session = Depends(get_db)):
    url_entry = db.query(URL).filter(URL.short_code == short_code).first()
    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return url_entry 