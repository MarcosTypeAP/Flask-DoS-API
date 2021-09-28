"""Controls the requests remain stable until the end of the given time 
or stop is indicated.
"""

# Python
import os
import sys
import subprocess

# Utils
import time
from datetime import datetime
from utils import (
    get_last_obj, 
    terminate_attack,
    HTTP_CMD,
)

# Signal
import signal


def terminate_attack_and_exit(signal, frame):
    terminate_attack()
    sys.exit(0)


def main(end_time, start_time, n):
    """Main function."""
    if datetime.fromtimestamp(end_time) < datetime.now():
        terminate_attack_and_exit(None, None)

    processes = int(subprocess.getoutput('ps -C http | grep http | wc -l'))
    if processes < n:
        os.system(HTTP_CMD)
        os.system(f"echo '--==--==-- {n}'")


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, terminate_attack_and_exit)

    query = get_last_obj()
    if not query:
        terminate_attack_and_exit(None, None)

    while True:
        main(*query)
        time.sleep(0.5)
