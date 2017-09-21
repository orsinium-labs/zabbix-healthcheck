
# built-in
from json import loads
# external
from grab import Grab
from pyzabbix import ZabbixAPI
# project
import config


g = Grab()

zapi = ZabbixAPI(config.ZABBIX_SERVER)
zapi.login(config.ZABBIX_LOGIN, config.ZABBIX_PASSWORD)


# Host group
groups = zapi.hostgroup.get()
for group in groups:
    if group['name'] == config.HOST_GROUP_NAME:
        print('Host group {} already added'.format(group['name']))
        group_id = group['groupid']
        break
else:
    group = zapi.hostgroup.create(name=config.HOST_GROUP_NAME)
    print('Created host group {}'.format(config.HOST_GROUP_NAME))
    group_id = group['groupids'][0]
print()

# Hosts
hosts = zapi.host.get(groupids=[group_id])
hostnames = [host['host'] for host in hosts]
for check in config.HEALTHCHECKS:
    if check.name in hostnames:
        print('Host {} already added'.format(check.name))
    else:
        zapi.host.create(
            host=check.name,
            groups=[{'groupid': group_id}],
            interfaces=[{
                'dns': check.dnsname,
                'ip': '',
                'main': 1,
                'port': '10050',
                'type': 1,
                'useip': 0,
            }],
        )
        print('Created host {}'.format(check.name))
print()

# Items
hosts = zapi.host.get(groupids=[group_id])
for host in hosts:
    items = zapi.item.get(hostids=[host['hostid']])
    items_names = [item['name'] for item in items]
    for check in config.HEALTHCHECKS:
        if check.name != host['host']:
            continue
        g.go(check.url)
        data = loads(g.doc.body.decode('utf-8'))
        for result in data['results']:
            # пропускаем уже созданные items
            if result['checker'] in items_names:
                print('Item {} already added'.format(result['checker']))
                continue
            # получаем интерфейс
            interface = zapi.hostinterface.get(hostids=[host['hostid']])[0]
            # создаем новый item
            zapi.item.create(
                name=result['checker'],
                delay=config.UPDATE_INTERVAL,
                hostid=host['hostid'],
                interfaceid=interface['interfaceid'],
                key_='{}[{},{}]'.format(
                    config.SCRIPT_NAME,
                    check.slug,
                    result['checker'],
                ),
                type=10,        # external check
                value_type=3,   # numeric unsigned
                history=1,      # [days]
            )
            items_names.append(result['checker'])
            print('Created item {} for host'.format(
                result['checker'],
                host['host'],
            ))
print()

# triggers
hosts = zapi.host.get(groupids=[group_id])
for host in hosts:
    triggers = zapi.trigger.get(hostids=[host['hostid']])
    triggers_names = [trigger['description'] for trigger in triggers]
    for check in config.HEALTHCHECKS:
        if check.name != host['host']:
            continue
        g.go(check.url)
        data = loads(g.doc.body.decode('utf-8'))
        for result in data['results']:
            key_name = '{}[{},{}]'.format(
                config.SCRIPT_NAME,
                check.slug,
                result['checker'],
            )
            # создаем триггеры
            for name, expr in config.TEMPLATES:
                name = name.format(result['checker'])
                # пропускаем уже созданные триггеры
                if name in triggers_names:
                    print('Trigger "{}" already added'.format(name))
                    continue
                expr = expr.replace('HOST', host['host'])
                expr = expr.replace('KEY', key_name)
                zapi.trigger.create(
                    description=name,
                    expression=expr,
                    priority=4,     # high
                )
                triggers_names.append(name)
                print('Created trigger "{}"'.format(name))
