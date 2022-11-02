FROM python:3.9

RUN pip install prometheus_client

ADD exporter.py /

EXPOSE 9299/tcp

CMD [ "python", "-u", "./exporter.py" ]