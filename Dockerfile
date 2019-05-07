FROM python:3.6.8

ADD . /app/
WORKDIR /app/

EXPOSE 5000

RUN pip install -r requirements.txt

CMD ["python", "/app/app.py"]