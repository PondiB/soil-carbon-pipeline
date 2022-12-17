FROM python:3.9-slim-buster

RUN pip install sqlalchemy psycopg2-binary

WORKDIR /app

COPY . .