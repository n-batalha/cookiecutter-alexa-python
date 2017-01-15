from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
from bot.bot.app import app
import datetime
import json


wsgi_app = app.create_wsgi_app(validate_requests=False)


def request_(req_type, app_id=None, session=None):  # pragma: no cover
    if (not session) and app_id is not None:
        session = {
            "application": {
                "applicationId": app_id
            }
        }

    return {
        'request': {
            'type': req_type,
            'timestamp': datetime.datetime.utcnow()
        },
        'session': session
    }


def intent_(name, slots=None, app_id=None, session=None):
    req = request_('IntentRequest', app_id, session)

    req['request']['intent'] = {
        'name': name,
        'slots': {
            k: {'name': k, 'value': v}
            for k, v in (slots or {}).items()
        }
    }

    return req


def test_client():
    return Client(wsgi_app, BaseResponse)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%dT%H:%M:%SZ")
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()
        else:
            return super(DateTimeEncoder, self).default(obj)
