from re import I
from symbol import import_as_name
import time

import requests
from flask import Flask, jsonify, request, Response
from flask import g
from flask_cors import CORS, cross_origin
from src.authz.verify import protected
from src.authz.verify import AppError
from src.appinsight.logger import get_logger
from src.appinsight.logger import trace_as_dependency, get_opencensus_tracer

app = Flask(__name__)
cors = CORS(origins='*', allow_headers=['Content-Type', 'Authorization'])

logger = get_logger(__name__)

@app.errorhandler(AppError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


@app.before_request
def before_request():
    g.start = time.time()


@app.after_request
def response_logger(response: Response):
    response_time = round(time.time() - g.start, 3) * 1000
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    remote_addr = "-" if ip is None else ip
    remote_user = "-" if request.remote_user is None else request.remote_user
    method = request.method
    scheme = request.scheme
    query_string = "-" if request.query_string is None else request.query_string
    url = request.url
    status = response.status
    referrer = request.referrer
    user_agent = request.user_agent
    logger.info(f"addr={remote_addr} user={remote_user} method={method} scheme={scheme} url={url} "
                f"query_string={query_string} referrer={referrer} user_agent={user_agent} "
                f"response_time_ms={response_time}, status={status}")
    return response


@app.errorhandler(404)
def handle_not_found(ex):
    return jsonify(message=f"Path {request.path} not found"), 404


@app.errorhandler(405)
def handle_not_found(ex):
    return jsonify(message=f"Method {request.method} not allowed on {request.path}"), 405


@app.route("/health", methods=['GET', 'HEAD'])
@trace_as_dependency(name="health")
def health():
    tracer = get_opencensus_tracer()
    logger.info("Checking health of the function.")
    with tracer.span('get_linkedin.com'):
        try:
            res = requests.get("https://www.linkedin.com", timeout=10)
            if res.status_code == 200:
                response = "Health Check Ok"
                status_code = res.status_code
            else:
                response = "Health Check Failed"
                status_code = res.status_code
            return jsonify(message=response), status_code
        except Exception as error:
            return jsonify(message=str(error)), 500


@app.route("/vault", methods=['GET', 'HEAD'])
@protected
@cross_origin(cors)
@trace_as_dependency(name="get_secret")
def get_secret():
    args = request.args
    secret = args.get("secret", None)
    if not secret:
        return jsonify(message="Secret name is missing. Please use QP secret=<secret_name>"), 400
    return jsonify(message=f"Vault Integration is currently not implemented to get value for {secret}"), 200


if __name__ == '__main__':
    app.run()
