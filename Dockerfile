FROM python:3.10

WORKDIR /usr/src/pycon_demo
COPY . /usr/src/pycon_demo

RUN apt-get update && apt-get install -y vim

RUN pip install -U pip
RUN pip install "poetry==1.6.1" && poetry install --no-interaction --no-ansi

CMD /usr/local/bin/python /usr/src/pycon_demo/pycon_opentelemetry_demo/fastapi_example/main.py