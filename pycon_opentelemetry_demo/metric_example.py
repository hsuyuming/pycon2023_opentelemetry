from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
    ConsoleMetricExporter,
    InMemoryMetricReader

)
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.metrics import set_meter_provider, get_meter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# Create an exporter + reader (ConsoleMetricExporter)
metric_exporter = ConsoleMetricExporter()
reader = PeriodicExportingMetricReader(
    metric_exporter 
)

# Create an exporter + reader (InMemoryMetricReader)
# reader = InMemoryMetricReader()

# Create an exporter + reader (OTLPMetricExporter)
# metric_exporter = OTLPMetricExporter(endpoint="", insecure=True)
# reader = PeriodicExportingMetricReader(
#     metric_exporter
# )


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

# Create Counter
counter = meter.create_counter(
    "counter",
    description="total counts",
)

for i in range(5):
    counter.add(1)

if isinstance(reader, InMemoryMetricReader):
    data = reader.get_metrics_data()
    print(data)


