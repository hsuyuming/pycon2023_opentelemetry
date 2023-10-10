from opentelemetry.sdk._logs.export import (
    BatchLogRecordProcessor,
    SimpleLogRecordProcessor,
    ConsoleLogExporter,
    InMemoryLogExporter
)
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry._logs import set_logger_provider,get_logger
import logging
from trace_example import tracer



# Create an exporter + processor (ConsoleLogExporter)
logger_exporter = ConsoleLogExporter()
logger_processor = BatchLogRecordProcessor(logger_exporter)

# Create an exporter + processor (InMemoryLogExporter)
# logger_exporter = InMemoryLogExporter()
# logger_processor = SimpleLogRecordProcessor(logger_exporter)

# Create an exporter + processor (OTLPLogExporter)
# logger_exporter = OTLPLogExporter(endpoint="", insecure=True)
# logger_processor = BatchLogRecordProcessor(logger_exporter)


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
l = logging.getLogger()
l.setLevel(level=logging.NOTSET)
l.addHandler(handler)

# Create different namespaced loggers
logger = logging.getLogger("pycon_demo")




if __name__ == "__main__":
    with tracer.start_as_current_span("demo") as sp:
        sp.set_attribute("key", "value")
        logger.info("pycon OTEL logging demo")
    
    # When you use InMemoryLogExporter, you can use get_finished_logs to get all logs. It's good for unittest.
    data = logger_exporter.get_finished_logs()
    print(data[0].log_record.to_json())



