import os
from abc import abstractmethod
import ipaddress
import urllib3
import configparser


def make_influx_stat(cfg_path):
    if not os.path.exists(cfg_path):
        raise FileNotFoundError()
    config = configparser.ConfigParser()
    config.read(cfg_path)

    host = config['DEFAULT'].get('HOST')
    port = int(config['DEFAULT'].get('PORT'))
    db_name = config['DEFAULT'].get('DB')
    token = config['DEFAULT'].get('TOKEN')

    stat = InfluxStat(host, db_name, port, token)
    return stat


class Stat:
    def __init__(self):
        self.__data = ''

    @abstractmethod
    def send(self, data):
        pass


class InfluxStat(Stat):
    def __init__(self, ip, db_name, port=8086, token=None):
        super().__init__()
        self.__token = token
        self.__ip = ipaddress.ip_address(ip)
        self.__port = port
        self.__db_name = db_name
        self.__url = "http://{}:{}/write?db={}".format(self.__ip, str(self.__port), self.__db_name)
        self.__headers = {'Authorization': self.__token}
        self.__http = urllib3.PoolManager()

    def send(self, data, **params):
        params_str = ''
        for k, v in params.items():
            params_str += '&' + str(k) + '=' + str(v)

        binary_data = data.encode('utf-8')

        r = self.__http.request('POST', self.__url + params_str, headers=self.__headers, body=binary_data)
        if r.status == 200 or r.status == 204:
            return 0
        return -1


    def send_from_file(self, path, **params):
        with open(path) as handler:
            data = handler.read()
        params_str = ''
        for k, v in params.items():
            params_str += '&' + str(k) + '=' + str(v)
        fields = {'filefield': (path, data, 'text/plain')}
        r = self.__http.request('POST', self.__url + params_str, headers=self.__headers, fields=fields)
        pass
