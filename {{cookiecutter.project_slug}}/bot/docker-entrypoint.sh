#!/bin/bash

touch /srv/logs/gunicorn.log
touch /srv/logs/access.log
tail -n 0 -f /srv/logs/*.log &

echo Starting Gunicorn
exec gunicorn bot:app \
    --bind 0.0.0.0:${API_PORT} \
    --log-level=info \
    --workers=1 \
    --log-file=/srv/logs/gunicorn.log \
    --access-logfile=/srv/logs/access.log \
    "$@"
