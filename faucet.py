import os
import sys
import httpx
import asyncio
import json
from config import apikey, provider
from web3 import Web3, Account
from src.utils import ipinfo, log, http
from src.service import anticaptcha, capsolver, twocaptcha


async def faucet(address, proxy):
    ses = httpx.AsyncClient(proxy=proxy,timeout=1000)
    ip = await ipinfo(ses=ses)
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,id;q=0.8",
        "cache-control": "no-cache",
        "content-type": "text/plain;charset=UTF-8",
        "origin": "https://testnet.megaeth.com",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://testnet.megaeth.com/",
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
    }
    ses.headers.update(headers)
    if provider == "anticaptcha":
        timet, token = await anticaptcha(apikey=apikey)
    elif provider == "twocaptcha":
        timet, token = await twocaptcha(apikey=apikey)
    elif provider == "capsolver":
        timet, token = await capsolver(apikey=apikey)
    if token is None:
        return None
    log(f"time to solve : {timet}")
    data = {
        "addr": address,
        "token": token,
    }
    claim_url = "https://carrot.megaeth.com/claim"
    res = await http(ses=ses, url=claim_url, data=json.dumps(data))
    if res.status_code != 200:
        if 'invalid CAPTCHA' in res.text:
            log('error : invalid captcha !')
        return None
    success = res.json().get('success')
    if success:
        log("success claim testnet token !")
        return True
    message = res.json().get('message')
    log(f"failed claim testnet token, {message}")
    return False


async def main():
    proxies = open("proxies.txt").read().splitlines()
    addresses = open("addresses.txt").read().splitlines()
    banner = ">\n> Auto Claim Faucet MegaETH\n> Join : @sdsproject\n> "
    menu = "1.) generate new walet\n2.) from addresses.txt\n"
    print(banner)
    print()
    print(f"total proxy : {len(proxies)}")
    print(f"total address : {len(addresses)}")
    print()
    print(menu)
    opt = input("input number : ")
    if opt == "1":
        p = 0
        while True:
            wallet = Account.create()
            privatekey = Web3.to_hex(wallet.key)
            open('privatekeys.txt','a').write(f'{privatekey}\n')
            address = wallet.address
            open('addresses.txt','a').write(f'{address}\n')
            log(f"addr : {address}")
            while  True:
                proxy = None if len(proxies) <= 0 else proxies[p % len(proxies)]
                result = await faucet(address=address,proxy=proxy)
                if result is None:
                    continue
                p += 1
                break

    elif opt == "2":
        
        for p,address in enumerate(addresses):
            log(f"addr : {address}")
            proxy = None if len(proxies) <= 0 else proxies[p % len(proxies)]
            while True:
                result = await faucet(address=address,proxy=proxy)
                if result is None:
                    continue
                break
    else:
        print("no number selected, exit !")
        sys.exit()



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, EOFError):
        sys.exit()
