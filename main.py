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
    return new_url

@app.get("/{short_code}")
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    url_entry = db.query(URL).filter(URL.short_code == short_code).first()
    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")
    url_entry.clicks += 1
    db.commit()
    return RedirectResponse(url=url_entry.original_url)