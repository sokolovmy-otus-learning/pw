import string
import random
import os
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import aerospike

ROOT_PATH = os.getenv('ROOT_PATH', '/')
app = FastAPI(root_path=ROOT_PATH)

# Подключение к Aerospike
config = {
    'hosts': [(os.getenv('AEROSPIKE_HOST', 'aerospike'), 3000)],
    'policies': {'timeout': 1000}
}
client = aerospike.client(config).connect()
LINK_TTL_SECONDS = int(os.getenv('LINK_TTL_SECONDS', 86400))

def pretty_ttl(seconds: int, long_format: bool = False) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if long_format:
        parts = []
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds > 0 or not parts:
            parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
        return ", ".join(parts)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

class UrlRequest(BaseModel):
    url: HttpUrl

def generate_short_id():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(6))

@app.post("/shorten")
async def shorten_url(request: UrlRequest):
    url = str(request.url)
    if not re.match(r'^https?://.+', url):
        raise HTTPException(status_code=400, detail="Invalid URL")
    while True:
        short_id = generate_short_id()
        try:
            client.get(('url_shortener', 'links', short_id))
        except aerospike.exception.RecordNotFound:  # type: ignore
            break
    client.put(
        ('url_shortener', 'links', short_id),
        {'original_url': url},
        meta={'ttl': LINK_TTL_SECONDS}
    )
    short_url = f'/{short_id}'
    return {"shortId": short_id, "shortUrl": short_url}

@app.get("/links/{shortId}")
async def get_link(shortId: str):
    try:
        (key, meta, bins) = client.get(('url_shortener', 'links', shortId))
        ttl = meta['ttl'] if meta['ttl'] > 0 else LINK_TTL_SECONDS
        return {
            "shortId": shortId,
            "originalUrl": bins['original_url'],
            "ttl": ttl,
            "prettyTtl": pretty_ttl(ttl, long_format=True)
        }
    except aerospike.exception.RecordNotFound:  # type: ignore
        raise HTTPException(status_code=404, detail="Link not found")