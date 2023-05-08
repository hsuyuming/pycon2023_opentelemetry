from curses.ascii import HT
from opentelemetry.sdk._logs.export import (
    BatchLogRecordProcessor,
)
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
import logging
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,

)
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.metrics import set_meter_provider, get_meter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import set_tracer_provider, get_tracer,get_current_span
from fastapi import FastAPI, HTTPException, Response, status, Request
import httpx
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry._logs import set_logger_provider
import uvicorn


OTLP_ENDPOINT = "192.168.0.6"

# ================================================
# OTLP Trace Setup
# ================================================

# Create an exporter + processor (OTLPSpanExporter)
trace_exporter = OTLPSpanExporter(endpoint=OTLP_ENDPOINT, insecure=True)
trace_processor = BatchSpanProcessor(trace_exporter)

# Create a TracerProvider
tracer_provider = TracerProvider(
    resource = Resource.create(
        {SERVICE_NAME: "server_a"}
    ),
    active_span_processor=trace_processor
)

set_tracer_provider(tracer_provider)
tracer = get_tracer(__name__)


# ================================================
# OTLP Metrics Setup
# ================================================
# Create an exporter + reader (OTLPMetricExporter)
metric_exporter = OTLPMetricExporter(endpoint=OTLP_ENDPOINT, insecure=True)
reader = PeriodicExportingMetricReader(
    metric_exporter
)

# Create a MeterProvider
meter_provider = MeterProvider(
    resource = Resource.create(
        {
            SERVICE_NAME: "pycon_demo"
        }
    ),
    metric_readers = [reader]
)

# Set the global meter provider 
set_meter_provider(meter_provider)

# Get a meter from global provider
meter = get_meter(
    name = "pycon_demo"
)

# ================================================
# OTLP Log Setup
# ================================================

# Create an exporter + processor (OTLPLogExporter)
logger_exporter = OTLPLogExporter(endpoint=OTLP_ENDPOINT, insecure=True)
logger_processor = BatchLogRecordProcessor(logger_exporter)

# Create a LoggerProvider
logger_provider = LoggerProvider(
    resource = Resource.create(
        {SERVICE_NAME: "pycon_demo"}
    ),
    multi_log_record_processor=logger_processor
)
set_logger_provider(logger_provider)

handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)

# Attach OTLP handler to root logger
# l = logging.getLogger()
# l.setLevel(level=logging.NOTSET)
# l.addHandler(handler)


logger = logging.getLogger(__name__)
logger.addHandler(
    LoggingHandler(
        level=logging.NOTSET,
        logger_provider=logger_provider
    )
)

app = FastAPI()


@app.get("/")
async def ping():
    return {"ping":"ping"}

@app.get("/data")
async def data(user:str, requests: Request):
    try:
        if user == "fail":
            raise Exception("A really bad error.")
        with httpx.Client() as client:
            response = client.get("https://google.com")
            data = response.json()
        return data
    except Exception as exc_info:
        current_span = get_current_span()
        logger.error("Critical error")
        current_span.record_exception(exc_info)
        raise HTTPException(status_code=500)

FastAPIInstrumentor.instrument_app(app)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        log_level="info",
    )
