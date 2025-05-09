FROM nginx:1.28.0-alpine-slim

ENV API_SHORTEN_URI=/api/shorten

COPY index.html /index.html.template

COPY 05-envsubst-template.sh /docker-entrypoint.d/
