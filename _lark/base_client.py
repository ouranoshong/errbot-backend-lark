#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import requests

from _lark import lark_response

log = logging.getLogger(__name__)


class BaseClient:
    BASE_URL = "https://open.feishu.cn/open-apis"

    def __init__(self,
                 base_url: str = BASE_URL,
                 app_id: str = None,
                 app_secret: str = None):
        self.base_url = base_url
        self.app_id = app_id
        self.app_secret = app_secret

    def auth_headers(self):
        access_token = self.tenant_access_token_internal()
        return {
            "Authorization": f"Bearer {access_token}"
        } if access_token else None

    def tenant_access_token_internal(self) -> str:
        """
        return tenant_access_token
        """
        tat_key = "tenant_access_token"
        params = {"app_id": self.app_id, "app_secret": self.app_secret}
        resp = self.api_call("/auth/v3/tenant_access_token/internal/",
                                   params=params)
        return resp.data[tat_key] if tat_key in resp.data else None

    def api_call(self,
                       api: str,
                       params: dict = None,
                       json: dict = None,
                       headers: dict = {}) -> lark_response.LarkResponse:
        try:
            url = self.__build_url(api)

            if params is not None:
                r = requests.get(url, params=params, headers=headers)

            if json is not None:
                r = requests.post(url, json=json, headers=headers)

            log.debug('fetch url: %s, headers: %s, params %s, json: %s', url, headers, params, json)
            
            return lark_response.of(r.json())
        except Exception as e:
            log.exception("fetch lark resp error")
            return lark_response.error(e)

    def __build_url(self, api: str):
        return self.base_url.rstrip('/') + '/' + api.lstrip('/')
