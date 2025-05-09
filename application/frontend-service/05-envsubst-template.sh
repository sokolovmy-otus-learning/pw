#!/bin/sh

envsubst '$API_SHORTEN_URI' < /index.html.template > /usr/share/nginx/html/index.html
