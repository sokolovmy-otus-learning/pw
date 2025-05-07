from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import redis.asyncio as redis
import os

app = FastAPI()

# Подключение к Redis
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

# Получение TTL из переменной окружения (по умолчанию 86400 секунд = 1 день)
LINK_TTL_SECONDS = int(os.getenv('LINK_TTL_SECONDS', 86400))

# Редирект по shortId
@app.get("/{shortId}")
async def redirect_url(shortId: str):
    url = await redis_client.get(shortId)
    if not url:
        raise HTTPException(status_code=404, detail="Link not found")

    # Обновление TTL при обращении
    await redis_client.expire(shortId, LINK_TTL_SECONDS)

    return RedirectResponse(url)