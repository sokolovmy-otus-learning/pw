import os
import re
import string
import random
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, HttpUrl
from aerospike import Client
import aerospike
import uvicorn

# Константы
LINK_TTL_SECONDS = int(os.getenv("LINK_TTL_SECONDS", 86400))
NAMESPACE = os.getenv("AEROSPIKE_NAMESPACE", "links")
PORT = int(os.getenv("PORT", 8000))
UVICORN_WORKERS = int(os.getenv("UVICORN_WORKERS", 4))
AEROSPIKE_PORT = int(os.getenv("AEROSPIKE_PORT", 3000))
HOSTS_STR = os.getenv("AEROSPIKE_HOSTS", "aerospike")
ROOT_PATH = os.getenv("ROOT_PATH", "/api")


app = FastAPI(root_path=ROOT_PATH)

# Парсим AEROSPIKE_HOSTS
hosts = [(host.strip(), AEROSPIKE_PORT) for host in re.split(r'\s*,\s*', HOSTS_STR.strip()) if host.strip()]

# Подключаемся к Aerospike
client = Client({
    "hosts": hosts,
    "policies": {
        "write": {
            "total_timeout": 1000,
            "max_retries": 2,
            "retry": aerospike.POLICY_RETRY_ONCE,
            "ttl": LINK_TTL_SECONDS
        },
        "read": {
            "total_timeout": 1000,
            "max_retries": 2,
            "retry": aerospike.POLICY_RETRY_ONCE,
            "read_touch_ttl_percent": -1
        }
    }
})

client.connect()

class ShortenRequest(BaseModel):
    url: HttpUrl

class LinkResponse(BaseModel):
    shortId: str
    shortUrl: str

class LinkInfoResponse(BaseModel):
    shortId: str
    originalUrl: str
    ttl: int
    prettyTtl: str

def generate_short_id(length: int = 6) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@app.post("/shorten", response_model=LinkResponse)
async def shorten_url(request: ShortenRequest):
    short_id = generate_short_id()
    key = (NAMESPACE, "links", short_id)
    bins = {"originalUrl": str(request.url)}
    client.put(key, bins)
    short_url = f"/{short_id}"
    return {"shortId": short_id, "shortUrl": short_url}

@app.get("/links/{short_id}", response_model=LinkInfoResponse)
async def get_link_info(short_id: str):
    key = (NAMESPACE, "links", short_id)
    try:
        (key, meta, bins) = client.get(key)
        ttl = meta["ttl"]
        pretty_ttl = f"{ttl // 3600} hours, {(ttl % 3600) // 60} minutes, {ttl % 60} seconds"
        return {
            "shortId": short_id,
            "originalUrl": bins["originalUrl"],
            "ttl": ttl,
            "prettyTtl": pretty_ttl
        }
    except aerospike.exception.RecordNotFound:  # type: ignore
        raise HTTPException(status_code=404, detail="Link not found")

@app.get("/health-status")
async def health_check():
    try:
        client.is_connected()
        return {"status": "healthy"}
    except aerospike.exception.AerospikeError:  # type: ignore
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Aerospike connection failed")

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        workers=UVICORN_WORKERS
    )