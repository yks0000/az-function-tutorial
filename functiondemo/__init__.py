import json

import azure.functions as func
from src.appinsight.logger import get_logger
from src.api import app as application
from opencensus.extension.azure.functions import OpenCensusExtension
from src.appinsight.logger import AI_CONNECTION_STRING, callback_add_role_name
from src.appinsight.logger import trace_as_dependency

# configure opencensus ext for azure function.
# this ensures that an opencensus tracer is created and associated with the func context
OpenCensusExtension.configure(connection_string=AI_CONNECTION_STRING)

# ensure that dependency records have the correct role name
OpenCensusExtension._exporter.add_telemetry_processor(callback_add_role_name)

__version__ = "0.0.1"
logger = get_logger(__name__)

@trace_as_dependency(name="entrypoint")
def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    logger.info("Receiving request for main handler.")
    try:
        http_response = func.WsgiMiddleware(application.wsgi_app).handle(req, context)
        http_response.headers["x-function-invocationId"] = context.invocation_id
        http_response.headers["x-function-version"] = __version__
        return http_response
    except Exception as error:
        logger.exception(str(error))
        return func.HttpResponse(
            json.dumps({"message": str(error)}),
            mimetype="application/json",
            status_code=504
        )
