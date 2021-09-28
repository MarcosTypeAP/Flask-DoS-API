FROM python:3.9-alpine

ENV PYTHONUNBUFFERED 1

RUN apk update \
    # psycopg2 dependencies
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    # CFFI dependencies
    && apk add libffi-dev py-cffi

    # plan malvado dependencies
RUN apk add bash sqlite procps

COPY requirements.txt /
RUN pip install -r requirements.txt

COPY xxx /app/

COPY . /app/

RUN sqlite3 /app/db.sqlite3 < /app/reset-db.sql

WORKDIR /app

CMD gunicorn -b 0.0.0.0:$PORT wsgi:server --chdir /app/dos
