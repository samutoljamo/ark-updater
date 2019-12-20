import configparser
import os

TEMPLATE = {
    "server":{
        "address":"127.0.0.1",
        "queryport":"27015",
        "rconport":"27020",
    }
}
INI_FILE_NAME = 'updater.ini'


class Parser(configparser.ConfigParser):

    def __init__(self, default, ini_file_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default = default
        self.ini_file_name = ini_file_name

    def read(self, *args, **kwargs):
        if not os.path.exists(self.ini_file_name):
            self.restore_defaults()
        res = super().read(*args, **kwargs)
        if not self.validate():
            self.restore_defaults()
        return res

    def restore_defaults(self):
        self.clear()
        self.read_dict(self.default)
        with open(self.ini_file_name, 'w') as fp:
            self.write(fp)

    def validate(self):
        for section in self.sections():
            needed_fields = self.default[section]
            for field, value in needed_fields.items():
                if field not in self[section]:
                    return False
        return True



def get_config():
    config = Parser(TEMPLATE, INI_FILE_NAME)
    config.read(INI_FILE_NAME)
    return config




if __name__ == "__main__":
    print(f"Running tests for {__file__}")
    print(get_config()['server']["queryport"])
