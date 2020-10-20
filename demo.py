#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from pyzabbix import ZabbixAPI,ZabbixAPIException
import sys
import logging

# logging.INFO, logging.WARNING, logging.DEBUG
#LOGGING_LEVEL = logging.DEBUG
LOGGING_LEVEL = logging.INFO


# host status
MONITORED       = 0
NOT_MONITORED   = 1
NOT_FOUND       = 2


def help():
    print "need help"

def group_info_get(zapi):
    group = zapi.hostgroup.get(
        output='extend',
        selectHosts='extend',
        real_host=True,
        monitored_hosts=True
    )

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
        return host[0]['status']


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
        selectTags='extend'
    )
    
    return host


def logging_load():
    stream = logging.StreamHandler(sys.stdout)
    stream.setLevel(LOGGING_LEVEL)
    log = logging.getLogger('pyzabbix')
    log.addHandler(stream)
    log.setLevel(LOGGING_LEVEL)


def test_host(zapi):
    hosts = host_info_get(zapi)
    for host in hosts:
        print(host)
        print("name={:15}\t\thostid={:15}\tstatus={:15}\terror={:15}".format(host['name'],host['hostid'],host['status'],host['error']))
    

def test_group(zapi):
    groups = group_info_get(zapi)
    for group in groups:
        print("group={0}\tgroupid={1}".format(group['name'],group['groupid']))

def test_inventory(zapi):
    groups = group_info_get(zapi)

    inventory = []
    num = 0
    for group in groups:
        
        for host in group['hosts']:
            hostStatus = host_status_get(zapi, host['host'])
            print id(hostStatus),id(MONITORED)
            if hostStatus is MONITORED:
                hostInfo = host_info_get_by_hostname(zapi, host['host'])
                inventory = {}
                print hostInfo + "#"
            else:
                print "no output"

def main():
    logging_load()
    #stream = logging.StreamHandler(sys.stdout)
    #stream.setLevel(LOGGING_LEVEL)
    #log = logging.getLogger('pyzabbix')
    #log.addHandler(stream)
    #log.setLevel(LOGGING_LEVEL)

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
            test_inventory(demo)
    else:
        help()

    #get group
    #groups = group_info_get(demo)

    #filter by group name
    #group = group_status_get(demo, 'demo-network/上海-交换机')

    #get group id by group name
    #group = group_id_get(demo, groupName)
    #for group in groups:
    #   print group
"""
    hosts = host_info_get(demo)
    for host in hosts:
        print("name={},hostid={},status={},error={}".format(host['name'],host['hostid'],host['status'],host['error']))
"""




if __name__ == "__main__":
    main()
