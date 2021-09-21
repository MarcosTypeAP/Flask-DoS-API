"""API Views that will be used by the frontend developers 
to develop the client app without carrying out attacks."""

# Flask
from flask import request, jsonify

# Python
from datetime import datetime
from datetime import timedelta

# Utils
from utils import (
    validate_request, 
    ARG_TZ,
)


def TestStatus():
    """Handle the request and return a simulation
    of the real Status view.
    
    An attack in progress can be simulated with the 
    URL parameter "attack", which can have the value 0 or 1.
    """
    try:
        attack = bool(int(request.args.get('attack', default=0)))
    except ValueError:
        attack = False
    if not attack:
        query = 'There is no attack in progress.'
        http_processes = 0
        handler_processes = 0
    else:
        query = {
            'start_time': '2021-08-13 11:46:02-03:00',
            'end_time': '2021-08-13 11:51:02-03:00',
            'n': 10,
        }
        http_processes = 10
        handler_processes = 1

    return jsonify({
        'http_processes': http_processes,
        'handler_processes': handler_processes,
        'time_info': {
            'server_timezone': 'UTC',
            'server_time': '2021-08-13 14:46:04.665359',
            'argentina_timezone': 'America/Argentina/Buenos_Aires',
            'argentina_time': '2021-08-13 11:46:04.665371-03:00',
        },
        'attack': query,
    }), 200


def TestStop():
    """Handle the request and return a simulation
    of the real Stop view.
    
    An attack in progress can be simulated with the 
    URL parameter "attack", which can have the value 0 or 1."""
    try:
        attack = bool(int(request.args.get('attack', default=0)))
    except ValueError:
        attack = False
    if not attack:
        return jsonify({
            'message': 'There is no attack in progress.',
        }), 409

    return jsonify({
        'message': 'The attack has ended successfully.',
        'duration': '0:01:23',
    }), 200


def TestStart():
    """Handle the request and return a simulation
    of the real Start view
    
    An attack in progress can be simulated with the 
    URL parameter "attack", which can have the value 0 or 1..
    """
    data = validate_request(request)
    if type(data) != dict:
        return data

    try:
        attack = bool(int(request.args.get('attack', default=0)))
    except ValueError:
        attack = False
    if attack:
        return jsonify({
            'message': 'There is already an attack in progress.',
            'remaining': '0:01:23',
        }), 409

    start_time = int(datetime.timestamp(datetime.now()))
    end_time = int(datetime.timestamp(datetime.now() + timedelta(minutes=data['minutes'])))
    n = data['n']

    response_data = {
        'message': 'Attack started successfully.', 
        'data': {
            'start_time': str(ARG_TZ.fromutc(datetime.fromtimestamp(start_time))),
            'end_time': str(ARG_TZ.fromutc(datetime.fromtimestamp(end_time))),
            'n': n,
        },
    }
    return jsonify(response_data), 201