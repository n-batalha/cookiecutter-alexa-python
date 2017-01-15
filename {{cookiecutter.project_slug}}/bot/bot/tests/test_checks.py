import json
import logging
from base64 import b64encode

import mock
from OpenSSL import crypto
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from bot.bot import app
from utils import request_
from utils import test_client, intent_, DateTimeEncoder

logging.basicConfig(level=logging.DEBUG)


# Replicate Google Cloud Load Balancer health checks
def test_health_check():
    c = test_client()
    resp = c.get('/')

    assert resp.status_code == 200


def test_bad_application_id(monkeypatch, caplog):
    monkeypatch.setenv('APPLICATION_ID', '0')

    c = test_client()

    intent_app_0 = intent_('', app_id='0')
    intent_app_1 = intent_('', app_id='1')

    resp_0 = c.post('/', content_type='application/json', data=DateTimeEncoder().encode(intent_app_0))
    resp_1 = c.post('/', content_type='application/json', data=DateTimeEncoder().encode(intent_app_1))

    assert resp_0.status_code == 200
    assert resp_1.status_code == 403

    # test if logs were created
    assert ('bot.bot.utils', logging.ERROR, 'Wrong application id: 0') not in caplog.record_tuples
    assert ('bot.bot.utils', logging.ERROR, 'Wrong application id: 1') in caplog.record_tuples


@mock.patch('alexandra.util.urlopen')
def test_signature(m_urlopen, monkeypatch):
    monkeypatch.setenv('APPLICATION_ID', '')

    # generate private key and certificate, to pretend we're Amazon
    pkey = crypto.PKey()
    pkey.generate_key(type=crypto.TYPE_RSA, bits=2048)

    cert = crypto.X509()
    cert.get_subject().C = "US"
    cert.get_subject().ST = "NY"
    cert.get_subject().L = "NA"
    cert.get_subject().O = "NA"  # noqa
    cert.get_subject().OU = "NA"
    cert.get_subject().CN = "echo-api.amazon.com"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(pkey)
    cert.sign(pkey, 'sha1')

    # generate client from the same app as gunicorn, with validation on
    c = Client(app, BaseResponse)

    data = request_("LaunchRequest", app_id="")
    data_str = DateTimeEncoder().encode(data)

    # sign data with "Amazon's" certificate
    signature = crypto.sign(pkey=pkey, data=data_str, digest='sha1')
    signature_str = b64encode(signature)

    cert_str = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)

    # when code asks Amazon for certificate, we pretend we're Amazon, send our certificate instead
    m_urlopen().read.side_effect = [cert_str]
    m_urlopen().getcode.side_effect = [200]

    resp = c.post('/', content_type='application/json', data=data_str,
                  headers=[('SignatureCertChainUrl', 'https://s3.amazonaws.com/echo.api/echo-api-cert-2.pem'),
                           ('Signature', signature_str)])

    assert m_urlopen.call_args == mock.call('https://s3.amazonaws.com/echo.api/echo-api-cert-2.pem')

    response = {
            "version": "1.0",
            "response": {
                "shouldEndSession": False,
                "outputSpeech": {
                    "text": "",
                    "type": "PlainText"
                },
                "reprompt": {
                    "outputSpeech": {
                        "text": "Which ingredient would you like to replace?",
                        "type": "PlainText"
                    }
                }
            },
            "sessionAttributes": {}
        }

    assert resp.status_code == 200
    assert json.loads(resp.data) == response
