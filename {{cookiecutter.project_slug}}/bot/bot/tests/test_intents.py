import json
import logging
from utils import request_, test_client, DateTimeEncoder
import pytest

logging.basicConfig(level=logging.DEBUG)


fixtures = [
    (
        request_("LaunchRequest", app_id=""),
        200,
        {
            "version": "1.0",
            "sessionAttributes": {},
            "response": {
                "outputSpeech": {
                    "text": "",
                    "type": "PlainText"
                },
                "reprompt": {
                    "outputSpeech": {
                        "text": "Which ingredient would you like to replace?",
                        "type": "PlainText"
                    }
                },
                "shouldEndSession": False,
            },
        }
     )
]


@pytest.mark.parametrize("data,code,response", fixtures)
def test_good_app(data, code, response, monkeypatch):
    monkeypatch.setenv('APPLICATION_ID', '')

    c = test_client()
    resp = c.post('/', content_type='application/json', data=DateTimeEncoder().encode(data))

    assert resp.status_code == code
    assert json.loads(resp.data) == response
