from valve.source.a2s import ServerQuerier
from valve.rcon import RCON
import subprocess


def get_num_players(address):
    with ServerQuerier(address) as s:
        info = s.info()
        return info["player_count"]


def broadcast(message, address, password):
    with RCON(address, password, timeout=5) as rcon:
        print(rcon.authenticated, rcon.connected)
        print(rcon(f"broadcast {message}"))


def get_version(steamcmd_path):
    subprocess.run([steamcmd_path])

if __name__ == '__main__':
    print(f"Running tests for {__file__}")
    print(get_num_players(("192.168.1.107", 27015)))
    #broadcast("test", ("192.168.1.107", 27020), "dodo123")
