import inspect
import logging
from functools import wraps
from logging import Logger

from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.trace import config_integration
from opencensus.trace import execution_context
from opencensus.trace.tracer import Tracer

config_integration.trace_integrations(['logging', 'requests'])

AI_KEY = "xxxxxxxxx-ae15-44c2-8da4-xxxxxxx"
AI_CONNECTION_STRING = f"InstrumentationKey={AI_KEY};IngestionEndpoint=https://westus-0.in.applicationinsights.azure.com/;LiveEndpoint=https://westus.livediagnostics.monitor.azure.com/"
WEBSITE_NAME = "function-demo"


class CustomDimensionsFilter(logging.Filter):
    """Add custom-dimensions in each log by using filters."""

    def __init__(self, custom_dimensions=None):
        """Initialize CustomDimensionsFilter."""
        super().__init__()
        self.custom_dimensions = custom_dimensions or {}

    def filter(self, record):
        """Add the default custom_dimensions into the current log record."""
        dim = {**self.custom_dimensions, **getattr(record, "custom_dimensions", {})}
        record.custom_dimensions = dim
        return True


def callback_add_role_name(envelope):
    """Add role name for logger."""
    envelope.tags['ai.cloud.role'] = WEBSITE_NAME
    envelope.tags["ai.cloud.roleInstance"] = WEBSITE_NAME


def get_logger(name: str, propagate: bool = True, custom_dimensions=None) -> Logger:
    if custom_dimensions is None:
        custom_dimensions = {}

    # Azure Log Handler
    azure_log_handler = AzureLogHandler(connection_string=AI_CONNECTION_STRING)
    azure_log_handler.add_telemetry_processor(callback_add_role_name)
    azure_log_handler.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter('%(asctime)s traceId=%(traceId)s api=%(name)s.%(funcName)s '
                                  '[%(levelname)-7s]: %(message)s')
    azure_log_handler.setFormatter(formatter)
    azure_log_handler.addFilter(CustomDimensionsFilter(custom_dimensions))

    # Logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(azure_log_handler)
    logger.propagate = propagate
    if not logger.handlers:
        logger.addHandler(azure_log_handler)
    return logger


def trace_as_dependency(tracer: Tracer = None, name: str = None, prefix: str = None):
    """trace_as_dependency [method decorator to trace a method invocation as a dependency (in AppInsights)]

    Args:
        tracer (Tracer): [Opencensus tracer object used to create the trace record.]
        name (str): [Name of the created trace record]
        prefix (str): [Prefix to be attached to Name]

    Returns:
        The inner function
    """

    def inner_function(method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            file_name = inspect.getfile(method).split("/")[-1].split(".py")[0]
            f = inspect.currentframe()
            i = inspect.getframeinfo(f.f_back)
            line_number = i.lineno
            trace_name = name if (name is not None) else method.__name__
            trace_name = f"{file_name}.{trace_name}"
            if prefix:
                trace_name = f"{prefix}.{trace_name}"
            oc_tracer = (
                tracer
                if (tracer is not None)
                else execution_context.get_opencensus_tracer()
            )

            if oc_tracer is not None:
                with oc_tracer.span(trace_name):
                    result = method(*args, **kwargs)
            else:
                result = method(*args, **kwargs)

            return result

        return wrapper

    return inner_function


def get_opencensus_tracer() -> Tracer:
    return execution_context.get_opencensus_tracer()