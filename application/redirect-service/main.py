import os
import re
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from aerospike import Client
import aerospike
import uvicorn

app = FastAPI()

# Константы
LINK_TTL_SECONDS = int(os.getenv("LINK_TTL_SECONDS", 86400))
NAMESPACE = os.getenv("AEROSPIKE_NAMESPACE", "url_shortener")
PORT = int(os.getenv("PORT", 8001))
UVICORN_WORKERS = int(os.getenv("UVICORN_WORKERS", 4))
AEROSPIKE_PORT = int(os.getenv("AEROSPIKE_PORT", 3000))
HOSTS_STR = os.getenv("AEROSPIKE_HOSTS", "aerospike")

# Парсим AEROSPIKE_HOSTS
hosts = [(host.strip(), AEROSPIKE_PORT) for host in re.split(r'\s*,\s*', HOSTS_STR.strip()) if host.strip()]

# Подключаемся к Aerospike
client = Client({
    "hosts": hosts,
    "policies": {
        "read": {
            "total_timeout": 1000,
            "max_retries": 2,
            "retry": aerospike.POLICY_RETRY_ONCE,
            "read_touch_ttl_percent": 100
        }
    }
})
client.connect()

@app.get("/health-status")
async def health_check():
    try:
        client.is_connected()
        return {"status": "healthy"}
    except aerospike.exception.AerospikeError:  # type: ignore
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Aerospike connection failed")

@app.get("/{short_id}")
async def redirect(short_id: str):
    key = (NAMESPACE, "links", short_id)
    try:
        (key, meta, bins) = client.get(key)
        original_url = bins["originalUrl"]
        return RedirectResponse(url=original_url)
    except aerospike.exception.RecordNotFound:  # type: ignore
        raise HTTPException(status_code=404, detail="Link not found")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        workers=UVICORN_WORKERS
    )