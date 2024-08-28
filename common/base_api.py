import json as json_

import requests

from common.config import TRACK_17_DOMAIN, DEFAULT_HEADERS
from common.exts import logger


class HttpRequest:
    _session = requests.Session()
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, method, path, params=None, data=None, headers=None, cookies=None, files=None, auth=None,
                 json=None, domain=None):
        self.files = [] if files is None else files
        self.headers = DEFAULT_HEADERS if headers is None else headers
        self.params = {} if params is None else params
        self.json = {} if json is None else json
        self.data = [] if data is None else data

        # 默认返回17track的domain，其他域名需要主动传参指定
        if not domain:
            self.domain = TRACK_17_DOMAIN
        else:
            self.domain = domain
        self.method = method
        self.path = path
        self.auth = auth
        self.cookies = cookies
        self.url = self.domain + self.path

    def execute(self):
        response = self._session.request(self.method,
                                         self.url,
                                         headers=self.headers,
                                         files=self.files,
                                         data=self.data,
                                         json=self.json,
                                         params=self.params,
                                         auth=self.auth,
                                         cookies=self.cookies)
        log_data = {
            "request headers": self.headers,
            "request url": self.url,
            "request params": self.params,
            "request data": self.data,
            "request json": self.json
        }
        logger.info(f"request data:\n{json_.dumps(log_data, indent=2, ensure_ascii=False)}")
        if response.json():
            resp_data = json_.dumps(response.json(), indent=2, ensure_ascii=False)
            logger.info(f"response statusCode: {response.status_code}, response data:\n{resp_data}")
        return response
