#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyzabbix import ZabbixAPI,ZabbixAPIException
import sys
import logging
import json
import csv
import time

# logging.INFO, logging.WARNING, logging.DEBUG
LOGGING_LEVEL = logging.DEBUG
#LOGGING_LEVEL = logging.INFO


# host status
MONITORED       = 0
NOT_MONITORED   = 1
NOT_FOUND       = 2


#stream = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler('zbxtool.log')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

#stream.setLevel(LOGGING_LEVEL)
logger = logging.getLogger('pyzabbix')

#logger.addHandler(stream)
logger.addHandler(file_handler)

logger.setLevel(LOGGING_LEVEL)


def help():
    print("need help")


def group_info_get(zapi):
    group = zapi.hostgroup.get(
        output='extend',
        selectHosts='extend',
        real_host=True,
        monitored_hosts=True
    )
    #logger.debug('hostgroup name: \033[96m {0}\033[00m'.format(group['name']))
    return group


def group_status_get(zapi, groupName):
    group = zapi.hostgroup.get(
        output='extend',
        filter={'name': groupName}
    )

    return group


def group_id_get(zapi, groupName):
    group = zapi.hostgroup.get(
        output=['groupid'],
        filter={'name': groupName}
    )

    return group


def group_create(zapi, groupName):
    group = zapi.hostgroup.create(
        name=groupName  
    )

    return group


def group_check(zapi, groupName):
    group = zapi.hostgroup.get(
        output=['groupid'],
        filter={'name': groupName}
    )

    return group


def host_status_get(zapi, host):
    host = zapi.host.get(
        filter={'host': host},
        output=['status'],
    )
    
    if not host:
        return NOT_FOUND
    else:
        #return int(host[0]['status'])
        return int(host[0]['status'])


def host_id_get(zapi, host):
    host = zapi.host.get(
        filter={'host': host},
        output=['hostid'],
    )
    
    if not host:
        return NOT_FOUND
    else:
        #return int(host[0]['status'])
        return int(host[0]['hostid'])


def host_create_for_sender(zapi, host, groupid):
    host = zapi.host.create(
        host=host,
        interfaces=[{
            "type":1,
            "ip":"127.0.0.1",
            "useip": 1,
            "port": "10050",
            "main": 1,
            "dns": ""
        }],
        groups=groupid
    )

    return host

def item_create_for_sender(zapi, hostid, key, value_type):
    item = zapi.item.create(
        name=key,
        key_=key,
        hostid=hostid,
        type=2,  # type of item
        value_type=value_type # 0-float 1-char 3-unsigned
    )

    return item


def item_search_for_sender(zapi, hostid, key):
    item = zapi.item.get(
        output="extend",
        hostids=hostid,
        search={"key_": key}
    )

    return item

#def history_get(zapi, itemid, value_type, time_from='1451606400', time_to='2398377600', limit=8760):
def history_get(zapi, itemid, value_type, limit=10):
    history = zapi.history.get(
        output='extend',
        history=value_type,
        itemids=itemid,
        sortorder='DESC',
        time_from=(int(time.time())-24*60*60*3), #1451606400,
        time_till=(int(time.time())), #2398377600,
        limit=limit
    )
    
    return history


def host_info_get(zapi):
    host = zapi.host.get(
        output='extend',
        selectInventory='extend',
        selectInterfaces='extend',
        selectTags='extend'
    )
    
    return host

def host_info_get_by_hostname(zapi, hostname):
    host = zapi.host.get(
        filter={'host':hostname},
        output='extend',
        selectInventory='extend',
        selectInterfaces='extend',
        selectTags='extend',
        selectParentTemplates='extend'
    )
    
    return host


def template_get(zapi):
    template = zapi.template.get(
        output='extend'
    )
        
    return template


def trigger_get(zapi):
    trigger = zapi.trigger.get(
        output='extend',
        expandDescription=1,
        only_true=1,
        skipDependent=1,
        active=1,
        withLastEventUnacknowledge=1,
        monitored=1,
        selectGroups=['groupid','name'],
        selectHosts=['host','name'],
        min_severity=4,
        selectItems=['key_','prevvalue','units','value_type'],
        sortorder='DESC',
        filter={'value':1}
    )
    
    return trigger


def logging_load():
    #stream = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler('zbxtool.log')

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    #stream.setLevel(LOGGING_LEVEL)
    logger = logging.getLogger('pyzabbix')

    #logger.addHandler(stream)
    logger.addHandler(file_handler)

    logger.setLevel(LOGGING_LEVEL)
    return logger


def test_host(zapi):
    hosts = host_info_get(zapi)
    for host in hosts:
        #print(host)
        print("name={:15}\t\thostid={:15}\tstatus={:15}\terror={:15}".format(host['name'],host['hostid'],host['status'],host['error']))
    

def test_group(zapi):
    groups = group_info_get(zapi)
    res = []
    for group in groups:
        print("group={0}\tgroupid={1}".format(group['name'],group['groupid']))
        res.append(group['name'])
        logger.info('hostgroup name: \033[96m {0}\033[00m'.format(group['name']))
    
    return res


def test_inventory(zapi):
    groups = group_info_get(zapi)

    inventorys = []
    num = 0
    for group in groups:
        
        for host in group['hosts']:
            hostStatus = host_status_get(zapi, host['host'])
            if hostStatus is MONITORED:
                hostInfo = host_info_get_by_hostname(zapi, host['host'])
                
                inventory = {}
                inventory['groupID'] = group['groupid']
                inventory['groupName'] = group['name']
                inventory['hostID'] =  hostInfo[0]['hostid']
                inventory['host'] =  hostInfo[0]['host']
                inventory['visiableName'] =  hostInfo[0]['name']

                # Tag
                tagList = []
                for tag in hostInfo[0]['tags']:
                    tagList.append(tag)
                inventory['tags'] = tagList 

                # Template
                templateList = []
                for template in hostInfo[0]['parentTemplates']:
                    templateList.append(template['host'])
                inventory['templates'] = templateList

                logger.info('inventory:{0}'.format(inventory))
                inventorys.append(inventory)
            else:
                logger.info('{} is null'.format(group))
           
        INVENTORY = 'inventory.json'
        with open(INVENTORY, 'w+') as f:
            f.write(json.dumps(inventorys, sort_keys=True, indent=4, separators=(',',':')))

        return json.dumps(inventorys, sort_keys=True, indent=4, separators=(',',':'))


def test_template(zapi):
    templates = template_get(zapi)
    for template in templates:
        print(template['host'])


def test_trigger(zapi):
    triggers = trigger_get(zapi)
    for trigger in triggers:
        print("{}#{}".format(trigger['description'],trigger['hosts'][0]['host']))


#def test_history(zapi, host, item, value_type, time_from, time_to, limit=8760):
def test_history(zapi, item, value_type=3):
    results = history_get(zapi, item, value_type)
    for result in results:
        print(result)

    return results
    

def main():
    demo = ZabbixAPI("http://10.112.20.51/demo")
    #demo = ZabbixAPI("http://10.112.20.209/zabbix")
    demo.session.verify = False
    demo.login("zapi", "zapi")
    
    groupName = 'Zabbix servers'
    
    if len(sys.argv) < 2:
        help()
        return
    elif sys.argv[1].startswith('--'):
        option = sys.argv[1][2:]
        if option == 'all':
            print("all")
        elif option == 'version':
            print("version")
        elif option == 'test_host':
            test_host(demo)
        elif option == 'test_group':
            test_group(demo)
        elif option == 'test_inventory':
            res = test_inventory(demo)
        elif option == 'test_template':
            test_template(demo)
        elif option == 'test_trigger':
            test_trigger(demo)
        elif option == 'test_history':
            key = 'test'
            host_id = host_id_get(demo, 'test01')
            print(host_id)
            item = item_search_for_sender(demo, host_id, key)
            item_id = item[0]['itemid']
            print(item_id)
            test_history(demo, item_id, 3)
    else:
        help()

"""
    hosts = host_info_get(demo)
    for host in hosts:
        print("name={},hostid={},status={},error={}".format(host['name'],host['hostid'],host['status'],host['error']))
"""




if __name__ == "__main__":
    main()
