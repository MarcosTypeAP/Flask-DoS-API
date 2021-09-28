"""Flask app that start/stop ddos attack to XD"""

# Flask
from flask import Flask, request, jsonify

# Python
import os
from datetime import datetime
from datetime import timedelta
import subprocess

# Utils
from utils import (
    open_db, 
    validate_request, 
    get_last_obj,
    terminate_attack,
    HTTP_CMD,
    ARG_TZ,
)
import time

# Test URLs
from test_views import (
    TestStart,
    TestStop,
    TestStatus,
)


app = Flask(__name__)
app.config['APPLICATION_ROOT'] = '/app'

app.add_url_rule("/test/start", methods=['POST'], view_func=TestStart)
app.add_url_rule("/test/stop", methods=['DELETE'], view_func=TestStop)
app.add_url_rule("/test/status", methods=['GET'], view_func=TestStatus)


@app.route('/status', methods=['GET'])
def Status():
    """Handles the request and responds with status data."""
    http_processes = int(subprocess.getoutput('ps -C http | grep http | wc -l'))
    handler_processes = int(subprocess.getoutput('ps -C python | grep python | wc -l'))
    query = get_last_obj()
    if not query:
        query = 'There is no attack in progress.'
    else:
        start_time = str(ARG_TZ.fromutc(datetime.fromtimestamp(query[1])))
        end_time = str(ARG_TZ.fromutc(datetime.fromtimestamp(query[0])))
        n = query[2]
        query = {
            'start_time': start_time,
            'end_time': end_time,
            'n': n,
        }

    return jsonify({
        'http_processes': http_processes,
        'handler_processes': handler_processes,
        'time_info': {
            'server_timezone': time.tzname[0],
            'server_time': str(datetime.now()),
            'argentina_timezone': str(ARG_TZ),
            'argentina_time': str(ARG_TZ.fromutc(datetime.utcnow())),
        },
        'attack': query,
    }), 200


@app.route('/stop', methods=['DELETE'])
def Stop():
    """Handle the request and stop the attack."""
    processes = int(subprocess.getoutput('ps -C http | grep http | wc -l'))
    query = get_last_obj()
    if not query and not processes:
        return jsonify({
            'message': 'There is no attack in progress.',
        }), 409

    os.system('pkill -f handle_requests.py')
    terminate_attack()
    start_time = datetime.fromtimestamp(query[1])
    seconds_diff = (datetime.now() - start_time).seconds
    return jsonify({
        'message': 'The attack has ended successfully.',
        'duration': str(timedelta(seconds=seconds_diff)),
    }), 200


@app.route('/start', methods=['POST'])
def Start():
    """Handle the request and start an attack
    if it is not existing yet.
    """
    data = validate_request(request)
    if type(data) != dict:
        return data

    query = get_last_obj()
    if query:
        current_end_time = datetime.fromtimestamp(query[0])

        if current_end_time > datetime.now():
            seconds_remaining = (current_end_time - datetime.now()).seconds
            return jsonify({
                'message': 'There is already an attack in progress.',
                'remaining': str(timedelta(seconds=seconds_remaining)),
            }), 409

    start_time = int(datetime.timestamp(datetime.now()))
    end_time = int(datetime.timestamp(datetime.now() + timedelta(minutes=data['minutes'])))
    n = data['n']

    db = open_db()
    db.execute("""
        INSERT INTO ddos (start_time, end_time, n)
        VALUES ({:d}, {:d}, {:d})
        """.format(start_time, end_time, n)
    )
    db.commit()
    db.close()

    for i in range(n):
        os.system(HTTP_CMD)
        os.system(f"echo '--==--==-- {i}'")
    
    os.system('python /app/ddos/handle_requests.py &')

    response_data = {
        'message': 'Attack started successfully.', 
        'data': {
            'start_time': str(ARG_TZ.fromutc(datetime.fromtimestamp(start_time))),
            'end_time': str(ARG_TZ.fromutc(datetime.fromtimestamp(end_time))),
            'n': n,
        },
    }
    return jsonify(response_data), 201