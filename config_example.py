from collections import namedtuple

Check = namedtuple('Check', ['slug', 'name', 'url', 'dnsname'])


ZABBIX_SERVER = 'http://zabbix.example.com'
ZABBIX_LOGIN = 'Admin'
ZABBIX_PASSWORD = 'zabbix'

HOST_GROUP_NAME = 'HealthCheck'
SCRIPT_NAME = 'healthchecker.py'
UPDATE_INTERVAL = 60

HEALTHCHECKS = (
    Check(
        slug='test',
        name='Test It',
        url='http://example.com/healthcheck',
        dnsname='example.com',
    ),
)
