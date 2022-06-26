FROM python:3.7-slim
WORKDIR /app/worker

COPY worker/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

CMD python3 app.py