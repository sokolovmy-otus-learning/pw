import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import aerospike
app = FastAPI()

# Подключение к Aerospike
config = {
    'hosts': [(os.getenv('AEROSPIKE_HOST', 'aerospike'), 3000)],
    'policies': {'timeout': 1000}
}
client = aerospike.client(config).connect()
LINK_TTL_SECONDS = int(os.getenv('LINK_TTL_SECONDS', 86400))

@app.get("/{shortId}")
async def redirect_url(shortId: str):
    try:
        (key, meta, bins) = client.get(('url_shortener', 'links', shortId))
        # Обновление TTL
        client.put(
            ('url_shortener', 'links', shortId),
            {'original_url': bins['original_url']},
            meta={'ttl': LINK_TTL_SECONDS}
        )
        return RedirectResponse(bins['original_url'])
    except aerospike.exception.RecordNotFoundError:  # type: ignore
        raise HTTPException(status_code=404, detail="Link not found")