from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import redis.asyncio as redis
import string
import random
import os
import re

app = FastAPI()

# Получение TTL из переменной окружения (по умолчанию 86400 секунд = 1 день)
LINK_TTL_SECONDS = int(os.getenv('LINK_TTL_SECONDS', 86400))

# Подключение к Redis
REDIS_SERVER = os.getenv('REDIS_SERVER', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
redis_client = redis.Redis(host=REDIS_SERVER, port=REDIS_PORT, decode_responses=True)

# Модель для входных данных
class UrlRequest(BaseModel):
    url: HttpUrl

# Генерация shortId (base62)
def generate_short_id():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(6))

# Создание короткой ссылки
@app.post("/api/shorten")
async def shorten_url(request: UrlRequest):
    url = str(request.url)

    # Проверка валидности URL
    if not re.match(r'^https?://.+', url):
        raise HTTPException(status_code=400, detail="Invalid URL")

    # Генерация уникального shortId
    while True:
        short_id = generate_short_id()
        if not await redis_client.exists(short_id):
            break

    # Сохранение URL и установка TTL
    await redis_client.set(short_id, url)
    await redis_client.expire(short_id, LINK_TTL_SECONDS)

    short_url = f'/{short_id}'
    return {"shortId": short_id, "shortUrl": short_url}

# Получение информации о ссылке
@app.get("/api/links/{shortId}")
async def get_link(shortId: str):
    url = await redis_client.get(shortId)
    if not url:
        raise HTTPException(status_code=404, detail="Link not found")
    return {"shortId": shortId, "originalUrl": url}