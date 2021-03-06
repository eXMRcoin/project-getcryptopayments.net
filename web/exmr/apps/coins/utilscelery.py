import json
import os
import web3
import requests
import datetime
import binascii
import subprocess
import collections


from decimal import Decimal
from itertools import chain
from solc import compile_source
from web3.contract import ConciseContract
from web3 import Web3, HTTPProvider, TestRPCProvider
from stellar_base.asset import Asset
from stellar_base.memo import TextMemo
from stellar_base.address import Address
from stellar_base.keypair import Keypair
from stellar_base.operation import CreateAccount, Payment
from stellar_base.horizon import horizon_livenet, horizon_testnet
from stellar_base.transaction_envelope import TransactionEnvelope as Te
from stellar_base.builder import Builder

from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT

from bitcoinrpc.authproxy import AuthServiceProxy
from apps.coins.models import Wallet, WalletAddress, Coin, EthereumToken, EthereumTokenWallet,\
    Transaction, MoneroPaymentid, PaybyName, TradeCommision
from apps.apiapp import views as apiview

from apps.merchant_tools.models import MerchantPaymentWallet

w3 = Web3(HTTPProvider('http://35.185.10.253:8545'))


def create_BTC_connection():
    """
    create connetion to bitcoin fullnode
    """
    access = AuthServiceProxy(
        "http://exmr:MKDNdksjfDNsjkN@35.185.10.253:8332")
    return access


def create_LTC_connection():
    """
    create connetion to litecoin fullnode
    """
    access = AuthServiceProxy("http://litecoinrpc:12345678@47.88.59.35:2300")
    return access


def create_XVG_connection():
    """
    create connetion to litecoin fullnode
    """
    access = AuthServiceProxy("http://verge:12345678@47.88.59.130:2300")
    return access


def create_BCH_connection():
    """
    create connetion to bitcoin cash fullnode
    """
    access = AuthServiceProxy(
        "http://bitcoincashrpc:12345678@39.104.231.49:2300")
    return access


def create_DASH_connection():
    return apiview.create_DASH_connection()


def get_balance(user, currency, addr=None):
    """
    Retrive specified user wallet balance.
    """
    if "Unable to generate address" in addr:
        return 0
    erc = EthereumToken.objects.filter(contract_symbol=currency)
    if erc:
        balance = EthereumTokens(user=user, code=currency, addr=addr).balance()
        # balance = 1
    elif currency == "XRPTest":
        balance = XRPTest(user, addr=addr).balance()
        # balance = 1
    elif currency in ["BTC", "LTC", "XVG", "BCH"]:
        balance = BTC(user, currency, addr=addr).balance()
        # balance = 1
    elif currency == "ETH":
        balance = ETH(user, currency, addr=addr).rcvd_bal()
        # balance = 1
    elif currency == "XRP":
        balance = XRP(user, addr=addr).balance()
        # balance = 1
    elif currency == "XLM":
        balance = XLM(user, "XLM", addr=addr).balance()
        # balance = 1
    elif currency == "XMR":
        balance = XLM(user, "XMR", addr=addr).balance()
        # balance = 1
    else:
        balance = 0

    return balance


class XRPTest():
    def __init__(self, user, addr=None):
        self.user = user
        self.address = addr

    def balance(self):
        if self.address:
            params = {
                "method": "account_info",
                "params": [
                    {
                        "account": self.address,
                        "strict": True,
                        "ledger_index": "validated"
                    }
                ]
            }
            result = json.loads(requests.post(
                "https://s.altnet.rippletest.net:51234", json=params).text)
            try:
                return float(Decimal(result['result']['account_data']['Balance'])/Decimal(1000000))
            except:
                return 0.0
        else:
            wallet = Wallet.objects.get(user=self.user, name__code="XRPTest")
            secret = wallet.private
            address = wallet.addresses.all().first().address
            params = {
                "method": "account_info",
                "params": [
                    {
                        "account": address,
                        "strict": True,
                        "ledger_index": "validated"
                    }
                ]
            }
        result = json.loads(requests.post(
            "https://s.altnet.rippletest.net:51234", json=params).text)
        try:
            return (float(Decimal(result['result']['account_data']['Balance'])/Decimal(1000000))-0)
        except:
            return 0.0

class ETH():
    def __init__(self, user=None, currency="ETH", addr=None):
        self.user = user
        self.address = addr
        self.currency = currency

    def get_results(self, method, params):
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        serialized_data = json.dumps(message)
        headers = {'Content-type': 'application/json'}
        response = requests.post(
            "http://35.185.10.253:8545", headers=headers, data=serialized_data)
        return response.json()

    def balance(self):
        current_balance = 0
        try:
            user_addr_list = Wallet.objects.get(user=self.user, name__code='ETH').addresses.all()
            current_balance = 0
            for temp_addr in user_addr_list:
                balance = float(w3.fromWei(w3.eth.getBalance(Web3.toChecksumAddress(temp_addr.address)), "ether"))
                current_balance = current_balance + balance
            return current_balance
        except:
            return current_balance

    def rcvd_bal(self):
        try:
            balance = float(w3.fromWei(w3.eth.getBalance(Web3.toChecksumAddress(self.address)), "ether"))
        except:
            balance = 0
        return float(balance)


def create_DASH_wallet(user, currency):
    coin = Coin.objects.get(code=currency)
    wallet_username = user.username + "_exmr"
    try:
        addr = apiview.createaddr(wallet_username, coin)
        # addr = False
        # raise Exception
    except:
        return ''
    try:
        wallet, created = Wallet.objects.get_or_create(user=user, name=coin)
        if created:
            wallet.addresses.add(WalletAddress.objects.create(address=addr))
            wallet.save()
        else:
            pub_address = wallet.addresses.all()[0].address
    except:
        addr = "Unable to generate address"
    return addr


class EthereumTokens():
    def __init__(self, user, code, addr=None):
        self.user = user
        self.code = code
        obj = EthereumToken.objects.get(contract_symbol=code)
        self.contract = w3.eth.contract(address=Web3.toChecksumAddress(obj.contract_address),
                                        abi=obj.contract_abi)
        self.address = addr

    def get_results(self, method, params):
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        serialized_data = json.dumps(message)
        headers = {'Content-type': 'application/json'}
        response = requests.post(
            "http://35.185.10.253:8545", headers=headers, data=serialized_data)
        return response.json()

    def balance(self, address=None):
        user_addr = self.address
        balance = float(self.contract.call().balanceOf(Web3.toChecksumAddress(user_addr))/pow(10, self.contract.call().decimals()))
        return balance


class BTC:
    def __init__(self, user=None, currency='BTC', addr=None):
        self.user = user
        self.currency = currency
        self.coin = Coin.objects.get(code=currency)
        self.access = globals()['create_' + currency+'_connection']()
        self.address = addr

    def balance(self):
        if not self.address:
            wallet_username = self.user.username + "_exmr"
            balance = self.access.getreceivedbyaccount(wallet_username)
            transaction = Transaction.objects.filter(
                user__username=self.user, currency=self.currency)
            if transaction:
                balance = balance - sum([Decimal(obj.amount)
                                         for obj in transaction])
        else:
            balance = self.access.getreceivedbyaddress(self.address)

        return float(balance)

    def rcvd_bal(self):
        try:
            balance = self.access.getreceivedbyaddress(self.address)
        except:
            balance = 0
        return float(balance)


class LTC():
    def __init__(self, user, currency, addr=None):
        self.temp = BTC(user, currency)
        self.address = addr

    def balance(self):
        self.temp.balance(self.address)



class XMR():
    def __init__(self, user, currency, addr=None):
        self.user = user
        self.address = addr

    def create_XMR_connection(self, method, params):
        url = "http://47.254.34.85:18083/json_rpc"
        headers = {'content-type': 'application/json'}
        data = {"jsonrpc": "2.0", "id": "0",
                "method": method, "params": params}
        response = requests.post(url, json=data, headers={
            'content-type': 'application/json'})
        return response.json()

    def balance(self):
        coin = Coin.objects.get(code='XMR')
        wallet = Wallet.objects.get(user=self.user, name=coin)
        if wallet:
            temp_list = MoneroPaymentid.objects.filter(user=self.user)
            balance = 0
            for pids in temp_list:
                param = {
                    "payment_id": pids.paymentid
                }
                try:
                    temp_balance = self.create_xmr_connection("get_payments", param)[
                        "result"]['payments'][0]['amount']
                except:
                    temp_balance = 0
                balance = balance + temp_balance
        else:
            balance = 0
        return balance

class XRP():
    def __init__(self, user, addr=None):
        self.user = user
        self.address = addr

    def balance(self):
        if self.address:
            params = {
                "method": "account_info",
                "params": [
                    {
                        "account": self.address,
                        "strict": True,
                        "ledger_index": "validated"
                    }
                ]
            }
            result = json.loads(requests.post(
                "http://s1.ripple.com:51234/", json=params).text)
            try:
                return float(Decimal(result['result']['account_data']['Balance'])/Decimal(1000000))
            except:
                return 0.0
        else:
            wallet = Wallet.objects.get(user=self.user, name__code="XRP")
            secret = wallet.private
            address = wallet.addresses.all().first().address
            params = {
                "method": "account_info",
                "params": [
                    {
                        "account": address,
                        "strict": True,
                        "ledger_index": "validated"
                    }
                ]
            }
            result = json.loads(requests.post(
                "http://s1.ripple.com:51234/", json=params).text)
            try:
                return float(Decimal(result['result']['account_data']['Balance'])/Decimal(1000000))
            except:
                return 0.0


def create_transaction(user, currency, amount, address):
    if currency in ['BTC', 'LTC']:
        currency = Coin.objects.get(code=currency)
        try:
            wallet_username = user.username + "_exmr"
        except:
            wallet_username = user + "_exmr"
        access = globals()['create_'+currency+'_connection']()
        valid = access.sendtoaddress(address, amount)
    elif currency == "eth":
        valid = ETH.send(self.request.user, amount, address)


def get_primary_address(user, currency):
    erc = EthereumToken.objects.filter(contract_symbol=currency)
    if erc:
        return EthereumTokens(user=user, code=currency).create_erc_wallet()
    if currency in ['XRPTest']:
        return XRP(user).create_xrp_wallet()
    if currency in ['ETH']:
        return ETH(user, currency).generate()
    elif currency in ['DASH']:
        return globals()['create_'+currency+'_wallet'](user, currency)
    elif currency in ['BTC', 'LTC']:
        coin = Coin.objects.get(code=currency)
        try:
            wallet = Wallet.objects.get(user=user, name=coin)
            addr = wallet.addresses.all()[0].address
        except:
            return create_wallet(user, currency)
        return addr

    else:
        return str(currency)+' server is under maintenance'

    return addr


class XLM():
    def __init__(self, user=None, currency="XLM", addr=None):
        self.user = user
        self.currency = currency
        self.coin = Coin.objects.get(code=currency)
        self.address = addr

    def generate(self, unique_id, random=None):
        kp = Keypair.random()
        address = kp.address().decode()
        if random:
            MerchantPaymentWallet.objects.create(merchant=self.user, address=address, private=kp.seed(
            ).decode(), unique_id=unique_id, code=self.currency)
            return address

        wallet, created = Wallet.objects.get_or_create(
            user=self.user, name=self.coin)
        if created:
            # requests.get('https://friendbot.stellar.org/?addr=' + address)
            wallet.addresses.add(WalletAddress.objects.create(address=address))
            wallet.private = kp.seed().decode()
            wallet.save()
        else:
            address = wallet.addresses.all()[0].address
            # requests.get('https://friendbot.stellar.org/?addr=' + address)
        return address

    def balance(self, address=None):
        if address:
            addr = Address(address=address)
            try:
                addr.get()
                return float(Decimal(addr.balances[0]['balance']))
            except:
                return 0.0
        else:
            user_addr = Wallet.objects.get(
                user=self.user, name=self.coin).addresses.all()[0].address
            address = Address(address=user_addr)
            try:
                address.get()
                return float(Decimal(address.balances[0]['balance']))
            except:
                return 0.0

    def send(self, destination, amount):
        destination = check_pay_by_name(destination, "XLM")
        wallet = Wallet.objects.get(user=self.user, name=self.coin)
        try:
            builder = Builder(secret=wallet.private)
            builder.add_text_memo("EXMR, Stellar!").append_payment_op(
                destination=destination.strip(), amount=str(amount), asset_code='XLM')
            builder.sign()
            response = builder.submit()
            return response["hash"]
        except:
            return {"error": "insufficient funds"}


class DepositTransaction():

    def __init__(self, user):
        self.user = user

    def get_deposit_transactions(self):
        data = []
        wallets = Wallet.objects.filter(user=self.user)
        available_coins = Coin.objects.filter(active=True, display=True)
        for wallet in wallets:
            if wallet.name in available_coins:
                data = data + self.get_currency_txn(wallet.name.code)
        return data

    def get_currency_txn(self, currency):
        erc = EthereumToken.objects.filter(contract_symbol=currency)
        if erc:
            return EthereumTokens(user=self.user, code=currency).get_transactions()
        if currency in ['BTC', 'LTC', 'XVG', 'BCH']:
            return BTC(self.user, currency).get_transactions()
        elif currency == 'ETH':
            return ETH(self.user, currency).get_transactions()
        else:
            return []


def check_pay_by_name(name, currency):
    if '$' in name:
        try:
            user = PaybyName.objects.get(label=name.strip('$')).user
            wallet = Wallet.objects.get(user=user, name__code=currency)
            return wallet.addresses.all().first().address
        except:
            pass
    return name
