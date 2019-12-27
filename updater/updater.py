import time
import logging

from.config import get_config
from .utils import get_version, get_num_players, update_server, start_server, stop_server, broadcast, loop, server_online
from .rcon import RCON

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
format = logging.Formatter('%(asctime)s: %(message)s')
handler.setFormatter(format)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class Updater:

    def __init__(self, sleep=30):
        self.config = get_config()
        self.sleep = sleep
        self.exit = None

    def check_for_updates(self):
        logger.info("Checking for updates")
        self.config = get_config()
        new_version = get_version(self.steamcmd)
        if new_version > self.buildid:
            self.exit()
            logger.info("Update found")
            self._broadcast("Update found. The server will be updated as soon as all players have left the server")
            self.update_server()
            self.buildid = new_version
            self.run(first=False)
        else:
            logger.info("No update found")

    def run(self, first=True):
        if not first:
            while not server_online((self.address, self.queryport)):
                time.sleep(self.sleep)
        self.exit = loop(self.check_for_updates, minutes=1)

    @property
    def address(self):
        return self.config.get('server', 'address')

    @property
    def queryport(self):
        return self.config.getint("server", "queryport")

    @property
    def rconport(self):
        return self.config.getint("server", "rconport")

    @property
    def steamcmd(self):
        return self.config.get('paths', 'steamcmdpath')

    @property
    def arkfolder(self):
        return self.config.get('paths', 'arkfolder')

    @property
    def password(self):
        return self.config.get("server", "password")

    @property
    def buildid(self):
        return self.config.getint("updater", "buildid")

    @buildid.setter
    def buildid(self, value):
        if type(value) != int:
            raise ValueError()
        self.config.set("updater", "buildid", str(value))
        self.config.save_to_file()

    def _broadcast(self, message):
        broadcast(message, (self.address, self.rconport), self.password)

    def update_server(self):
        while get_num_players((self.address, self.queryport)) >= 1:
            time.sleep(self.sleep)
        stop_server((self.address, self.rconport), self.password)
        # give some time for the server to stop
        time.sleep(10)
        update_server(self.steamcmd, self.arkfolder)
        start_server(self.arkfolder, self.config.get("server", "startcommand"))





