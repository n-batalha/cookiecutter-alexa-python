import os
import alexandra
import logging
from werkzeug.exceptions import abort

log = logging.getLogger(__name__)


class WsgiAppGC(alexandra.wsgi.WsgiApp, object):
    def wsgi_app(self, request):
        if (request.path, request.method) == ('/', 'GET'):
            return alexandra.wsgi.Response(response='',
                                           status=200,
                                           mimetype='text/plain')
        return super(WsgiAppGC, self).wsgi_app(request)


class App(alexandra.Application, object):
    # extend alexandra to validate the application id
    def dispatch_request(self, body):
        request_app_id = body["session"]["application"]["applicationId"]

        if os.getenv('APPLICATION_ID') != request_app_id:
            log.error("Wrong application id: {}".format(request_app_id))
            abort(403)

        return super(App, self).dispatch_request(body)

    # extend alexandra to handle Google Cloud's Load Balancing health checks
    def create_wsgi_app(self, validate_requests=True):
        return WsgiAppGC(self, validate_requests)
