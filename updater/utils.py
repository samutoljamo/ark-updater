import valve
from valve.source.a2s import ServerQuerier
from valve.source.messages import InfoRequest, LongField, ByteField, Message, StringField, InfoResponse
from .rcon import RCON, RCONTimeoutError
import subprocess
import os, re
import time, threading
import logging

logger = logging.getLogger(__name__)

ARK_APPID = "376030"
REGEX = r'"public"\n\t\t\t{\n\t\t\t\t"buildid"\t\t"(\d+)"'


class InfoRequestChallenge(Message):
    fields = (
        ByteField("request_type", True, 0x54),
        StringField("payload", True, "Source Engine Query"),
        LongField("challenge", True)
    )

class InfoChallenge(Message):
    fields = (
        ByteField("response_type", validators=[lambda x: x==0x41]),
        LongField("challenge")
    )
def info(s):
    s.request(InfoRequest())
    response = InfoChallenge.decode(s.get_response())
    req = InfoRequestChallenge(challenge=response['challenge'])
    s.request(req)
    return InfoResponse.decode(s.get_response())

def get_num_players(address):
    try:
        with ServerQuerier(address) as s:
            return info(s)["player_count"]
    except valve.source.NoResponseError:
        logger.error("Cannot connect, make sure updater.ini has the right values")
        exit(-1)


def server_online(address):
    try:
        with ServerQuerier(address) as s:
            info(s)
            return True
    except valve.source.NoResponseError:
        return False

def stop_server(address, password, save=True):
    try:
        with RCON(address, password, timeout=5) as rcon:
            if save:
                logger.info(rcon("saveworld"))
                time.sleep(10)
            logger.info(rcon("doexit"))
    except (RCONTimeoutError, TimeoutError):
        logger.error("Failed to connect using RCON. Make sure you have RCON enabled and correct values in updater.ini file")
        exit(-1)


def broadcast(message, address, password):
    try:
        with RCON(address, password, timeout=5) as rcon:
            logger.info(rcon(f"broadcast {message}"))
    except (RCONTimeoutError, TimeoutError):
        logger.error("Failed to connect using RCON. Make sure you have RCON enabled and correct values in updater.ini file")
        exit(-1)


def get_version(path):
    res = subprocess.run([path, "+login anonymous", "+app_info_update 1", "+app_info_print", ARK_APPID, "+quit"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         universal_newlines=True)
    m = re.search(REGEX, res.stdout)
    return int(m.group(1))


def start_server(path, args):
    return subprocess.Popen([path + "/ShooterGame/Binaries/Win64/ShooterGameServer.exe", args])


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


