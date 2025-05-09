FROM python:3.12-slim


ENV PORT=8001
ENV UVICORN_WORKERS=2

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "gunicorn -w ${UVICORN_WORKERS} -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:${PORT}"]
