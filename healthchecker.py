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
    founded = -1
    for check in config.HEALTHCHECKS:
        if check.slug != host:
            continue
        g.go(check.url)
        data = loads(g.doc.body.decode('utf-8'))
        for result in data['results']:
            if result['checker'] != item:
                continue
            founded = 1
            if not result['passed']:
                return 0
    return founded


if __name__ == '__main__':
    host = argv[1]
    item = argv[2]
    result = get_check(host, item)
    print(int(result))
