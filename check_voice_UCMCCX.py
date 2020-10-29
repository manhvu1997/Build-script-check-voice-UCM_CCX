#!/usr/bin/python
import time
import sys
import os
from optparse import OptionParser
import time
from elasticsearch import Elasticsearch
from pprint import pprint

query_time = 900  # thoi gian query log kibana tinh bang giay

# Status code
OK = 0
CRITICAL = 2
UNKNOWN = 3

# Result
msg1 = ""
msg2 = ""
msg = ""
type1 = " production"
msg_compare = []
hit_compare = []
result = dict()
now = time.time()
past = now - query_time
now = int(now * 1000)   # chuyen sang milisecond
past = int(past * 1000)  # chuyen sang milisecond
list_service = ['Cisco License Manager',
                'Cisco DRF Master',
                'Cisco Bulk Provisioning Service',
                'Cisco CAR DB',
                'Cisco CAR Scheduler',
                'Cisco CAR Web Service',
                'Cisco CDR Repository Manager',
                'Cisco Certificate Authority Proxy Function',
                'Cisco DRF Master',
                'Cisco DirSync',
                'Cisco Directory Number Alias Sync',
                'Cisco Intercluster Lookup Service',
                'Cisco SOAP - CDRonDemand Service',
                'Cisco SOAP - CallRecord Service',
                'Cisco TAPS Service',
                'Cisco Unified Mobile Voice Access Service',
                'Cisco Wireless Controller Synchronization Service',
                'Self Provisioning IVR']

# Parsing argurments
parser = OptionParser()
parser.add_option(
    "-H",
    dest="host",
    type="string",
    help="Hostname/IP Address of device",
    metavar=' ')
parser.add_option(
    "-S",
    dest="service",
    type="string",
    help="Service of device",
    metavar=' ')
parser.add_option(
    "-N",
    dest="node",
    type="string",
    help="Node of device",
    metavar=' ')
parser.add_option(
    "-P",
    dest="primary",
    type="string",
    help="Primary node of device",
    metavar=' ')
parser.add_option(
    "-T",
    dest="status",
    type="string",
    help="Status of device",
    metavar=' ')
# parser.add_option(
#     "-D",
#     dest="type",
#     type="string",
#     help="Status of device",
#     metavar=' ')

(options, args) = parser.parse_args()
server = str(options.host)
list_ip = ["172.27.228.202", "172.27.228.105"]
if server in list_ip:
    type_device = 'development'
else:
    type_device = 'production'
node = str(options.node)
service = str(options.service)
service_re = service.replace('_', ' ')

if service_re not in list_service:
    primary_node = str(options.primary)
    list_primary_node = list(primary_node.split("_"))
    index = "cucm-cucx-logs-*"  # index lay log
    body = {
        "size": 1000,
        "query": {
            "bool": {
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": past,
                            "lte": now
                        }
                    }
                },
                "must": [
                    {"match": {"server.keyword": {
                        "query": str(options.host), "operator": "and"}}},
                    {"match": {"service.keyword": {
                        "query": service_re, "operator": "and"}}},
                    {"match": {"node.keyword": {"query": str(
                        options.node), "operator": "and"}}},
                    # {"match": {"primary_node.keyword": {"query": str(options.primary), "operator": "and"}}},
                    {"match": {"status.keyword": {
                        "query": str(options.status)}}}
                ]
            }
        }
    }
    #### KIBANA CONNECTION ####
    try:
        es = Elasticsearch(
            '118.70.194.14:9200',
            http_auth=(
                'sccftel',
                'scC@ft3l'),
            timeout=3)
        kibanaLog = es.search(index=index, body=body)
        stt_query = kibanaLog["_shards"]["failed"]
        if (stt_query == 0) and (kibanaLog['hits']['hits'] == []):
            msg = 'CRITICAL' + ' ' + '-' + ' ' + node + ' ' + \
                service_re + ' ' + 'fail on ' + server + ' ' + type_device
            print msg
            sys.exit(2)

        #### KIBANA QUERY ####
        elif (stt_query == 0) and (kibanaLog['hits']['hits'] != []):
            for hit in kibanaLog['hits']['hits']:
                if hit["_source"]["primary_node"] in list_primary_node:
                    msg1 = 'OK'

                else:
                    msg2 = 'CRITICAL'
                msg_compare.append(msg1)
                msg_compare.append(msg2)
            if 'CRITICAL' not in msg_compare:
                msg = 'OK - All services check OK'
                print msg
                sys.exit(0)
            else:
                msg += 'CRITICAL' + ' ' + '-' + ' ' + node + ' ' + \
                    service_re + ' ' + 'fail on ' + server + ' ' + type_device
                print msg
                sys.exit(2)
        elif (stt_query != 0):
            print 'UNKNOWN - Server Kibana query fail'
            sys.exit(3)
    except Exception as e:
        print 'UNKNOWN - Server Kibana connection timed out!'
        sys.exit(3)
else:
    index = "cucm-cucx-logs-*"  # index lay log
    primary_node = str(options.primary)
    status = str(options.status)
    list_primary_node = list(primary_node.split("_"))
    try:
        list_primary_node.remove("")
    except Exception as e:
        pass
    list_status = list(status.split("_"))
    try:
        list_status.remove("")
    except Exception as e:
        pass
    body1 = {
        "size": 1000,
        "query": {
            "bool": {
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": past,
                            "lte": now
                        }
                    }
                },
                "must": [
                    # {"match": {"server.keyword": {
                    #     "query": str(options.host), "operator": "and"}}},
                    {"match": {"service.keyword": {
                        "query": service_re, "operator": "and"}}},
                    {"match": {"node.keyword": {"query": str(
                        options.node), "operator": "and"}}},
                    # {"match": {"primary_node.keyword": {"query":primary_node, "operator": "and"}}},
                    # {"match": {"status.keyword": {"query":status_start}}}
                ]
            }
        }
    }
    try:
        es_1 = Elasticsearch(
            '118.70.194.14:9200', http_auth=(
                'sccftel', 'scC@ft3l'), timeout=3)
        kibanaLog_1 = es_1.search(index=index, body=body1)
        # kibanaLog_2 = es_1.search(index = index, body = body2)
        stt_query_1 = kibanaLog_1["_shards"]["failed"]
        # stt_query_2 = kibanaLog_2["_shards"]["failed"]
        # pprint (kibanaLog_1['hits']['hits'])
        if (stt_query_1 == 0) and (kibanaLog_1['hits']['hits'] != []):
            for hit in kibanaLog_1['hits']['hits']:
                hit_status = []
                if hit["_source"]["status"] in list_status and hit["_source"]["primary_node"] in list_primary_node:
                    hit_status.append(hit["_source"]["status"])
                    hit_status.append(hit["_source"]["primary_node"])
                    hit_compare.append(hit_status)
                else:
                    msg = 'CRITICAL' + ' ' + '-' + ' ' + node + ' ' + \
                        service_re + ' ' + 'fail on ' + server + ' ' + type_device
                    print msg
                    sys.exit(2)
            for lst, pri in zip(list_status, list_primary_node):
                lst_compare = []
                lst_compare.append(lst)
                lst_compare.append(pri)
                if lst_compare in hit_compare:
                    msg1 = "OK"
                else:
                    msg2 = "CRITICAL"
                msg_compare.append(msg1)
                msg_compare.append(msg2)
            if "CRITICAL" not in msg_compare:
                print "OK - All services check OK"
                sys.exit(0)
            else:
                msg = 'CRITICAL' + ' ' + '-' + ' ' + node + ' ' + \
                    service_re + ' ' + 'fail on ' + server + ' ' + type_device
                print msg
                sys.exit(2)
        else:
            print 'UNKNOWN - Server Kibana query fail'
            sys.exit(3)
        # print (kibanaLog_1)
        # print (kibanaLog_2)
    except Exception as e:
        print 'UNKNOWN - Server Kibana connection timed out!'
        sys.exit(3)
