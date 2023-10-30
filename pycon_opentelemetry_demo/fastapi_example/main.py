import uvicorn
import fastapi
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
import time
import random
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs.export import (
    BatchLogRecordProcessor,
    SimpleLogRecordProcessor,
    ConsoleLogExporter,
    InMemoryLogExporter
)
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry._logs import set_logger_provider
import logging

OTLP_HOST="collector-agent:8890"
SERVICE="opentelemetry-pycon-demo"


### ===============================
### Trace
### ===============================
provider = TracerProvider(
    resource=Resource.create({SERVICE_NAME:SERVICE})
)

processor = BatchSpanProcessor(
    # ConsoleSpanExporter(),
    # InMemorySpanExporter(),
    OTLPSpanExporter(endpoint=OTLP_HOST, insecure=True)
)
provider.add_span_processor(processor)
# Sets the global default tracer provider
trace.set_tracer_provider(provider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer(__name__)

### ===============================
### Trace
### ===============================

logger_exporter = OTLPLogExporter(endpoint=OTLP_HOST, insecure=True)
logger_processor = BatchLogRecordProcessor(logger_exporter)

# Create a LoggerProvider
logger_provider = LoggerProvider(
    resource = Resource.create(
        {SERVICE_NAME: SERVICE}
    ),
    multi_log_record_processor=logger_processor
)

set_logger_provider(logger_provider)

handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)

# Attach OTLP handler to root logger
l = logging.getLogger()
l.setLevel(level=logging.NOTSET)
l.addHandler(handler)

# Create different namespaced loggers
logger = logging.getLogger(__name__)


app = fastapi.FastAPI()


@app.get("/foo")
def foo():
    time.sleep(random.uniform(0,10))
    logger.info("someone call foo.")
    current_span = trace.get_current_span()
    span_context = current_span.context
    trace_id = trace.format_trace_id(span_context.trace_id) 
    return {"message": trace_id}

@app.get("/bar")
async def bar():
    logger.info("someone call bar.")
    return {"message": "bar"}

tp = trace.get_tracer_provider()

Instrumentator().instrument(app).expose(app)
FastAPIInstrumentor.instrument_app(app, excluded_urls="metrics")


if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, host="0.0.0.0",log_level="info", workers=1)