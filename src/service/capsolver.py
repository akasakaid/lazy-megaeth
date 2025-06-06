import time
import json
import httpx
import asyncio
from src.utils.http import http
from src.utils.log import log


async def capsolver(apikey):
    data = {
        "clientKey": apikey,
        "task": {
            "type": "AntiTurnstileTaskProxyLess",
            "websiteURL": "https://testnet.megaeth.com",
            "websiteKey": "0x4AAAAAABA4JXCaw9E2Py-9",
        },
    }
    req_url = "https://api.capsolver.com/createTask"
    res_url = "https://api.capsolver.com/getTaskResult"
    headers = {"content-type": "application/json"}
    async with httpx.AsyncClient(headers=headers,timeout=1000) as ses:
        res = await http(ses=ses, url=req_url, data=json.dumps(data))
        task_id = res.json().get("taskId")
        error_id = res.json().get("errorId")
        error_code = res.json().get("errorCode")
        error_desc = res.json().get("errorDescription")
        if error_id != 0:
            log(f"error code : {error_code}")
            log(f"error desc : {error_desc}")
            return 0, False
        st = int(time.time())
        while True:
            data = {"clientKey": apikey, "taskId": task_id}
            res = await http(ses=ses, url=res_url, data=json.dumps(data))
            error_id = res.json().get("errorId")
            status = res.json().get("status")
            if error_id != 0:
                error_code = res.json().get("errorCode")
                error_desc = res.json().get("errorDescription")
                log(f"error code : {error_code}")
                log(f"error desc : {error_desc}")
                return 0, False
            if status == "processing":
                await asyncio.sleep(3)
                continue
            if status == "ready":
                solution = res.json().get("solution", {})
                token = solution.get("token")
                nt = int(time.time())
                ft = nt - st
                return ft, token
