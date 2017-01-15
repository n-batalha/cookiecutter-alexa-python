import logging

from app import wsgi_app as app

# For now, send all errors of the root logger to gunicorn's log (ours, werkzeug, alexandra, etc)
# logger = logging.getLogger(__name__)
logger = logging.getLogger()

# only send INFO logs and above
logger.setLevel(logging.INFO)

gunicorn_error_handlers = logging.getLogger('gunicorn.error').handlers
logger.handlers.extend(gunicorn_error_handlers)
