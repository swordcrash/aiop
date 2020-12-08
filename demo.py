#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from pyzabbix import ZabbixAPI,ZabbixAPIException
import sys
import logging
import json
import csv

# logging.INFO, logging.WARNING, logging.DEBUG
#LOGGING_LEVEL = logging.DEBUG
LOGGING_LEVEL = logging.INFO


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
    print "need help"


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
    for group in groups:
        print("group={0}\tgroupid={1}".format(group['name'],group['groupid']))
        logger.info('hostgroup name: \033[96m {0}\033[00m'.format(group['name']))


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
        print template['host']


def main():
    demo = ZabbixAPI("http://10.112.20.51/demo")
    demo.session.verify = False
    demo.login("zapi", "zapi")
    
    groupName = 'Zabbix servers'
    
    if len(sys.argv) < 2:
        help()
        return
    elif sys.argv[1].startswith('--'):
        option = sys.argv[1][2:]
        if option == 'all':
            print "all"
        elif option == 'version':
            print "version"
        elif option == 'test_host':
            test_host(demo)
        elif option == 'test_group':
            test_group(demo)
        elif option == 'test_inventory':
            res = test_inventory(demo)
        elif option == 'test_template':
            test_template(demo)
    else:
        help()

"""
    hosts = host_info_get(demo)
    for host in hosts:
        print("name={},hostid={},status={},error={}".format(host['name'],host['hostid'],host['status'],host['error']))
"""




if __name__ == "__main__":
    main()
