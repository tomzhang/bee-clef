# -*- coding:utf-8 -*-

"""
Author: Fang
Date:   2021.06.01
WeChat: chizi777
Twitter: https://twitter.com/phper100
This is a swarm debug api manage script, include almost swarm apis.
這是一個swarm api的管理脚本，集成大多數的管理功能。
Usage:
python beetools.py
python beetools.py [index, [1,2,3,4,5,6,7.....]]
Features:
1. Include almost of bee debug apis
2. Formated command result while run command, logs  in ./logs folder.
功能：
1. 包括大部分的 Swarm BEE 的API
2. 当你执行命令时会格式化记录你命令执行的结果，以方便查看，日志在相对目录logs文件夹下面
Require:
Python3+
"""

import requests
import sys
import os
import time
import json

MIN_AMOUNT = 0
DEBUG_API = ''
LOG_FILE = "./logs/default.log"
API_ADDRESSES = '{}/addresses'
API_CHEQUEBOOK_CHEQUE = '{}/chequebook/cheque'
API_CHEQUEBOOK_ADDRESS = '{}/chequebook/address'
API_CHEQUEBOOK_CASHOUT = '{}/chequebook/cashout/{}'
API_SETTLEMENTS = '{}/settlements'
API_BALANCES = '{}/balances'
API_PEERS = '{}/peers'
API_CHEQUEBOOK_WITHDRAW = '{}/chequebook/withdraw'
API_CHEQUEBOOK_DEPOSIT = '{}/chequebook/deposit'

DEFAULT_API_PORT = '1633'
DEFAULT_P2P_PORT = '1634'
DEFAULT_DEBUG_PORT = '1635'


def getAllActions():
    return [
        {
            "index": "1",
            "alias": "docker-list-cheques",
            "tips": "On Docker, List all cheques at this server.",
        },
        {
            "index": "2",
            "alias": "docker-cashout-cheques",
            "tips": "On Docker, Cashout all uncashed cheques at this server.",
        },
        {
            "index": "3",
            "alias": "list-all-cheques",
            "tips": "List all cheques.",
        },
        {
            "index": "4",
            "alias": "cash-out-allA",
            "tips": "Cash out all.",
        },
        {
            "index": "5",
            "alias": "query-eth-addresses",
            "tips": "Query eth addresses.",
        },
        {
            "index": "6",
            "alias": "query-chequebook-address",
            "tips": "Query chequebook address.",
        },
        {
            "index": "7",
            "alias": "query-peers",
            "tips": "Query peers.",
        },
        {
            "index": "8",
            "alias": "query-settlements",
            "tips": "Query settlements.",
        },
        {
            "index": "9",
            "alias": "query-balances",
            "tips": "Query balances.",
        },
        {
            "index": "10",
            "alias": "chequebook-deposit",
            "tips": "Chequebook deposit.",
        },
        {
            "index": "11",
            "alias": "chequebook-withdraw",
            "tips": "Chequebook withdraw.",
        },
        {
            "index": "12",
            "alias": "view-bee-logs",
            "tips": "View bee logs.",
        },
        {
            "index": "13",
            "alias": "install-prometheus-client",
            "tips": "Install prometheus monitor client(TODO...)",
        }
    ]


def log(msg, level="info"):
    global LOG_FILE
    msg = "{} [{}] {}\n".format(time.strftime('%Y-%m-%d %H:%M:%S'), level, msg)
    print(msg)
    fileObject = open(LOG_FILE, 'a')
    fileObject.write(msg)
    fileObject.close()


def getDebugApi(port):
    return 'http://localhost:{}'.format(port)


def getPeers():
    global DEBUG_API
    response = requests.get('{}/chequebook/cheque'.format(DEBUG_API))
    data = response.json()
    if type(data) is dict and data.get('lastcheques'):
        return list(map(lambda x: x['peer'], data['lastcheques']))
    return []


def cashout(peer):
    global DEBUG_API
    response = requests.post('{}/chequebook/cashout/{}'.format(DEBUG_API, peer))
    if type(response.json()) is not dict or not response.json().get('transactionHash'):
        log("could not cashout cheque for peer: {}, error reason: {}".format(peer, response.json()))
        return
    txHash = response.json()['transactionHash']
    log("cashing out cheque for peer: {} in transactionHash {}".format(peer, txHash))


def getCumulativePayout(peer):
    global DEBUG_API
    response = requests.get('{}/chequebook/cheque/{}'.format(DEBUG_API, peer))
    if response.json().get('lastreceived') and response.json().get('lastreceived') is not None:
        return response.json()['lastreceived'].get('payout')
    return 0


def getLastCashedPayout(peer):
    global DEBUG_API
    response = requests.get('{}/chequebook/cashout/{}'.format(DEBUG_API, peer))

    if response.json().get('cumulativePayout'):
        return response.json().get('cumulativePayout')
    return 0


def getUncashedAmount(peer):
    cashedPayout = getLastCashedPayout(peer)
    cumulativePayout = getCumulativePayout(peer)
    if cumulativePayout == 0:
        log("cheque with 0 uncashedAmount peer: {}".format(peer))
        return 0
    return cumulativePayout - cashedPayout


def getInfo():
    global DEBUG_API
    response = requests.get('{}/addresses'.format(DEBUG_API))
    address = response.json().get('ethereum') if response.json().get('ethereum') else ''
    response = requests.get('{}/chequebook/address'.format(DEBUG_API))
    chequebook = response.json().get('chequebookAddress') if response.json().get('chequebookAddress') else ''
    chequebook = response.json().get('chequebookaddress') if not chequebook else chequebook
    msg = "Current node: port: {}, eth address: {}, chequebook address: {}".format(DEBUG_API, address, chequebook)
    log(msg)


def cashoutAll(min_amount=MIN_AMOUNT):
    peers = getPeers()
    for peer in peers:
        uncashedAmount = getUncashedAmount(peer)
        if uncashedAmount > min_amount:
            msg = "Uncashed: {} (gbzz: {}), uncashed peer: {}".format(uncashedAmount, toEth(uncashedAmount), peer)
            log(msg)
            cashout(peer)


def listAllUncashed():
    global DEBUG_API
    peers = getPeers()
    if len(peers) == 0:
        msg = "{} has no cash.".format(DEBUG_API)
        log(msg)
        return
    for peer in peers:
        uncashedAmount = getUncashedAmount(peer)
        if uncashedAmount > 0:
            msg = "Uncashed: {} (gbzz: {}), uncashed peer: {}".format(uncashedAmount, toEth(uncashedAmount), peer)
            log(msg)


def setLogFile(action):
    global LOG_FILE
    os.popen("mkdir -p ./logs")
    LOG_FILE = "./logs/{}-{}.log".format(action, time.strftime('%Y%m%d-%H%M%S'))


def toEth(num):
    return num / 1000000000000000


def toGwei(num):
    return int(num * 1000000000000000)


def queryAddress(port):
    global DEBUG_API, API_ADDRESSES
    DEBUG_API = getDebugApi(port)
    response = requests.get(API_ADDRESSES.format(DEBUG_API))
    print(json.dumps(response.json(), indent=4))


def queryChequebookAddress(port):
    global DEBUG_API, API_CHEQUEBOOK_ADDRESS
    DEBUG_API = getDebugApi(port)
    response = requests.get(API_CHEQUEBOOK_ADDRESS.format(DEBUG_API))
    chequebookAddress = response.json()['chequebookAddress']
    if not chequebookAddress:
        chequebookAddress = response.json()['chequebookaddress']
    print("Chequebook address: {}".format(chequebookAddress))


def queryPeers(port):
    global DEBUG_API, API_PEERS
    DEBUG_API = getDebugApi(port)
    response = requests.get(API_PEERS.format(DEBUG_API))
    peers = response.json()['peers']
    print(json.dumps(peers, indent=4))
    print("Peer length: {}".format(len(peers)))


def querySettlements(port):
    global DEBUG_API, API_SETTLEMENTS
    DEBUG_API = getDebugApi(port)
    response = requests.get(API_SETTLEMENTS.format(DEBUG_API))
    print(json.dumps(response.json(), indent=4))


def queryBalances(port):
    global DEBUG_API, API_BALANCES
    DEBUG_API = getDebugApi(port)
    response = requests.get(API_BALANCES.format(DEBUG_API))
    print(json.dumps(response.json(), indent=4))


def chequebookWithdraw(port, amount):
    global DEBUG_API, API_CHEQUEBOOK_WITHDRAW
    DEBUG_API = getDebugApi(port)
    response = requests.post(API_CHEQUEBOOK_WITHDRAW.format(DEBUG_API) + "?amount=" + str(toGwei(amount)))
    print(json.dumps(response.json(), indent=4))


def viewBeeLogs():
    os.system('journalctl --lines=100 --follow --unit bee')


def chequebookDeposit(port, amount):
    global DEBUG_API, API_CHEQUEBOOK_DEPOSIT
    DEBUG_API = getDebugApi(port)
    response = requests.post(API_CHEQUEBOOK_DEPOSIT.format(DEBUG_API) + "?amount=" + str(toGwei(amount)))
    print(json.dumps(response.json(), indent=4))


def getAction(actionIndex):
    actionArray = getAllActions()
    i = 0
    for elm in actionArray:
        if elm['index'] == actionIndex:
            return actionArray[i]
        i = i + 1
    return {}


if __name__ == '__main__':
    actionInfo = {}
    if len(sys.argv) > 1:
        actionInfo = getAction(sys.argv[1])
    else:
        print("Here we go, select below number to start: (Author's Wechat: chizi777)\n")
        actionArray = getAllActions()
        i = 1
        for elm in actionArray:
            print("{}. {}".format(i, elm['tips']))
            i = i + 1
        actionInfo = getAction(str(input("Please select option:")))
        if len(actionInfo) < 1:
            print('Please select number.')
    setLogFile(actionInfo['alias'])
    action = actionInfo['index']
    if action and action in ['1', '2']:
        debugPorts = os.popen("docker ps | grep bee | awk -F'->' '{print $3}' | awk -F':' '{print $2}' | sort")
        if debugPorts:
            for port in debugPorts:
                try:
                    port = port.strip()
                    if not port:
                        continue
                    DEBUG_API = getDebugApi(port)
                    getInfo()
                    if action == '1':
                        listAllUncashed()
                    elif action == '2':
                        cashoutAll(MIN_AMOUNT)
                    print("\n")
                except Exception as e:
                    log("Port {} error, error details: {}".format(port, str(e)), 'error')
        else:
            log("Get bee debug ports of docker is error, run exited.", 'error')
    elif action and action in ['3', '4', '5', '6', '7', '8', '9', '10', '11']:
        port = input("Please input port number (default port: 1635): ")
        if not port:
            port = DEFAULT_DEBUG_PORT
        DEBUG_API = getDebugApi(port.strip())
        if action == '3':
            getInfo()
            listAllUncashed()
        elif action == '4':
            getInfo()
            cashoutAll(MIN_AMOUNT)
        elif action == '5':
            queryAddress(port)
        elif action == '6':
            queryChequebookAddress(port)
        elif action == '7':
            queryPeers(port)
        elif action == '8':
            querySettlements(port)
        elif action == '9':
            queryBalances(port)
        elif action == '10':
            amount = input("Please input deposit amount, 1 mean 1 bzz: ")
            chequebookDeposit(port, float(amount))
        elif action == '11':
            amount = input("Please input withdraw amount, 1 mean 1 bzz: ")
            chequebookWithdraw(port, float(amount))
        else:
            print("Error option")
    elif action and action in ['12', '13']:
        if action == '12':
            viewBeeLogs()
    else:
        print("Error option")