"""巩义燃气 API 封装。

加密协议：
  请求: JSON → AES-128-ECB + PKCS7 → Base64
        包装为 {"aoteEncrypt": "AES", "data": "<base64>"}
  响应: 原始 Base64 → AES 解密 → JSON
"""
from __future__ import annotations

import base64
import json
import logging
from typing import Any

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

_LOGGER = logging.getLogger(__name__)

HOST = "http://weixin.uxinxin.com/weixin2"
KEY = b"OXuYieBb4eoIne^K"
USER_AGENT = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 26_0_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "CriOS/140.0.7339.122 Mobile/15E148 Safari/604.1"
)


class GasApi:
    """巩义燃气 API 客户端。"""

    def __init__(self, openid: str, user_name: str) -> None:
        self._openid = openid
        self._user_name = user_name
        self._session = requests.Session()
        self._session.trust_env = False
        self._session.headers.update({
            "User-Agent": USER_AGENT,
            "Referer": f"http://weixin.uxinxin.com/weixin2/index32.html?openid={openid}&filiale=gongyi",
        })

    @staticmethod
    def _encrypt(text: str) -> str:
        padded = pad(text.encode("utf-8"), AES.block_size, style="pkcs7")
        return base64.b64encode(AES.new(KEY, AES.MODE_ECB).encrypt(padded)).decode()

    @staticmethod
    def _decrypt(b64_text: str) -> str:
        raw = base64.b64decode(b64_text)
        return unpad(
            AES.new(KEY, AES.MODE_ECB).decrypt(raw),
            AES.block_size, style="pkcs7"
        ).decode("utf-8")

    def _post(self, url: str, post_data: dict) -> Any:
        body = json.dumps({
            "aoteEncrypt": "AES",
            "data": self._encrypt(json.dumps(post_data)),
        })
        resp = self._session.post(url, data=body)
        if resp.status_code != 200:
            raise ConnectionError(f"HTTP {resp.status_code} for {url}: {resp.text[:300]}")
        return json.loads(self._decrypt(resp.text))

    def fetch_all(self) -> dict[str, Any]:
        """依次调用 searchBandList → searchUserMeter → searchUserHandPlanDetailToNew"""

        # 1. 查找用户信息
        users = self._post(
            f"{HOST}/rs/logic/searchBandList",
            {"condition": f"f_open_id = '{self._openid}'", "f_open_id": self._openid},
        )
        user_info = None
        for u in users:
            if u.get("f_user_name") == self._user_name:
                user_info = u
                break
        if not user_info:
            raise Exception(f"未找到燃气用户: {self._user_name}")

        address = user_info.get("f_address", "")
        userinfo_id = user_info["f_userinfo_id"]

        # 2. 查询燃气表信息
        meters = self._post(
            f"{HOST}/rs/logic/searchUserMeter",
            {"condition": f"f_userinfo_id = {userinfo_id}"},
        )
        meter = meters[0]
        balance = float(meter.get("f_balance_amount", 0))
        user_id = meter["f_user_id"]
        meter_number = meter.get("f_meternumber", "")

        # 3. 查询昨日用量
        records = self._post(
            f"{HOST}/rs/sql/searchUserHandPlanDetailToNew?pageNo=1&pageSize=5",
            {"data": {"f_user_id": str(user_id)}},
        )
        yesterday = records[0] if records else {}
        yesterday_usage = float(yesterday.get("f_oughtamount", 0))
        yesterday_fee = float(yesterday.get("f_oughtfee", 0))
        update_time = yesterday.get("f_input_date", "")

        return {
            "balance": balance,
            "yesterday_usage": yesterday_usage,
            "yesterday_fee": yesterday_fee,
            "update_time": update_time,
            "meter_number": meter_number,
            "address": address,
        }
