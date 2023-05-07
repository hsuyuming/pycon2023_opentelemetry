from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor
)
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import set_tracer_provider, get_tracer

# Create an exporter + processor (ConsoleSpanExporter)
trace_exporter = ConsoleSpanExporter()
trace_processor = BatchSpanProcessor(trace_exporter)

# Create an exporter + processor (InMemorySpanExporter)
# trace_exporter = InMemorySpanExporter()
# trace_processor = SimpleSpanProcessor(trace_exporter)

# Create an exporter + processor (OTLPSpanExporter)
# trace_exporter = OTLPSpanExporter(endpoint="", insecure=True)
# trace_processor = BatchSpanProcessor(trace_exporter)

# Create a TracerProvider
tracer_provider = TracerProvider(
    resource = Resource.create(
        {SERVICE_NAME: "pycon_demo"}
    ),
    active_span_processor=trace_processor
)

# Set the global tracer provider 
set_tracer_provider(tracer_provider)

# Get a tracer from global provider
tracer = get_tracer("pycon_demo")




if __name__ == "__main__":
    # Instrument!
    with tracer.start_as_current_span("demo") as sp:
        sp.set_attribute("key", "value")

    if isinstance(trace_exporter, InMemorySpanExporter):
        data = trace_exporter.get_finished_spans()
        print(data[0].to_json())