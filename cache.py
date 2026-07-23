import redis

redis_client = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)

from fastapi import HTTPException, Request

RATE_LIMIT = 5          # max requests
RATE_WINDOW = 60        # per 60 seconds

def check_rate_limit(client_ip: str):
    key = f"rate_limit:{client_ip}"
    current = redis_client.get(key)

    if current is None:
        redis_client.set(key, 1, ex=RATE_WINDOW)
        return

    if int(current) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")

    redis_client.incr(key)