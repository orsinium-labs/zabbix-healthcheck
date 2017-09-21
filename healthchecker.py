#!/usr/bin/python3

# built-in
from json import loads
from sys import argv
# external
from grab import Grab
from pyzabbix import ZabbixAPI
# project
import config


g = Grab()

zapi = ZabbixAPI(config.ZABBIX_SERVER)
zapi.login(config.ZABBIX_LOGIN, config.ZABBIX_PASSWORD)


def get_check(host, item):
    error_code = 2          # NOT FOUND
    for check in config.HEALTHCHECKS:
        if check.slug != host:
            continue
        try:
            g.go(check.url)
        except Exception as e:
            return 3        # NETWORK ERROR
        data = loads(g.doc.body.decode('utf-8'))
        for result in data['results']:
            if result['checker'] != item:
                continue
            error_code = 0  # OK
            # проверка вернула ошибку
            if not result['passed']:
                return 1    # NOT PASSED
    return error_code


if __name__ == '__main__':
    host = argv[1]
    item = argv[2]
    result = get_check(host, item)
    print(int(result))
