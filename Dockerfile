FROM python:3-alpine

RUN pip install --upgrade pip

RUN mkdir /src

ADD . .

WORKDIR /src

RUN pip install -r requirements.txt

CMD gunicorn --bind 0.0.0.0:$PORT wsgi
