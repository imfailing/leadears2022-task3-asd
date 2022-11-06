import configparser, os

class Config:
    def __init__(self, config_name='app.conf'):
        self._config = configparser.ConfigParser()
        self._config.read(config_name)

    def get_db_conf(self):
        if os.getenv('ENV') == 'PROD':
            return self._config['db_prod']
        else:
            return self._config['db_dev']