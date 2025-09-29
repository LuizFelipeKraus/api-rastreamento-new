import os
import psycopg2
from flask import g


def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            database=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            port=os.getenv('POSTGRES_PORT'))
    return g.db


def get_db_alt():
    if 'db_alt' not in g:
        g.db_alt = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            database=os.getenv('POSTGRES_ALT_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            port=os.getenv('POSTGRES_PORT'))
    return g.db_alt


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

    db_alt = g.pop('db_alt', None)
    if db_alt is not None:
        db_alt.close()