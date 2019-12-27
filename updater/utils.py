import valve
from valve.source.a2s import ServerQuerier
from .rcon import RCON, RCON
import subprocess
import os, re
import time, threading
import logging

logger = logging.getLogger(__name__)

ARK_APPID = "376030"
REGEX = r'"public"\n\t\t\t{\n\t\t\t\t"buildid"\t\t"(\d+)"'


def get_num_players(address):
    try:
        with ServerQuerier(address) as s:
            info = s.info()
            return info["player_count"]
    except valve.source.NoResponseError:
        logger.error("Cannot connect, make sure updater.ini has the right values")
        exit(-1)


def stop_server(address, password, save=True):
    try:
        with RCON(address, password, timeout=5) as rcon:
            if save:
                rcon("saveworld")
                time.sleep(10)
            rcon("doexit")
    except TimeoutError:
        logger.error("Failed to connect to RCON. Make sure you have RCON enabled and correct values in updater.ini file")
        exit(-1)


def broadcast(message, address, password):
    try:
        with RCON(address, password, timeout=5) as rcon:
            rcon(f"broadcast {message}")
    except TimeoutError:
        logger.error("Failed to connect to RCON. Make sure you have RCON enabled and correct values in updater.ini file")
        exit(-1)


def get_version(path):
    res = subprocess.run([path, "+login anonymous", "+app_info_update 1", "+app_info_print", ARK_APPID, "+quit"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         universal_newlines=True)
    m = re.search(REGEX, res.stdout)
    return int(m.group(1))


def start_server(path, args):
    return subprocess.Popen([path + "ShooterGame/Binaries/Win64/ShooterGameServer.exe", args])


def update_server(path, ark_dir):
    subprocess.run([path, "+login anonymous", "+force_install_dir", ark_dir, "+app_update", ARK_APPID,
                    "validate", "+quit"])


def loop(func, seconds=None, minutes=None, hours=None, *args, **kwargs):
    interval = 0
    if seconds:
        interval = seconds
    if minutes:
        interval += minutes * 60
    if hours:
        interval += hours * 3600
    if interval <= 0:
        interval = 1

    event = threading.Event()

    def f():
        def next_time(t, n):
            while t <= n:
                t += interval
            return t
        t0 = time.monotonic()
        func(*args, **kwargs)

        now = time.monotonic()
        t0 = next_time(t0, now)
        while not event.wait(t0-now):
            func(*args, **kwargs)
            now = time.monotonic()
            t0 = next_time(t0, now)
    threading.Thread(target=f).start()
    return event.set

