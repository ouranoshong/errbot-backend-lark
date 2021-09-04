import pprint
import sys
import logging

from sanic import Sanic
from sanic.request import Request
from sanic.response import json

# from aiohttp import web, web_app, web_request

log = logging.getLogger(__name__)

SERVER_NAME = 'lark-errbot-server'


class LarkServer:
    def __init__(self, config: dict):
        self.verification_token = config.get("verification_token", None)
        self.encrypt_key = config.get("encrypt_key", None)
        self.host = config.get("host", "0.0.0.0")
        self.port = config.get("port", 8000)
        if not self.verification_token:
            log.error("Verification Token must be provided in config")
            sys.exit(1)
        self._register_event_handlers()

    def _register_event_handlers(self):
        self.event_handlers = {
            "url_verification": self._url_verification_handler,
            "im.message.receive_v1": self._message_receive_handler
        }

    def update_event_handlers(self, event_handlers: dict):
        self.event_handlers.update(event_handlers)

    def _url_verification_handler(self, data: dict):
        return {"challenge": data.get("challenge", "")}

    def _message_receive_handler(self, data: dict):
        # override it if you need
        pass

    async def handler(self, request: Request):
        data = request.json
        log.info("received data: %s", data)
        token = data.get("token", "") or data.get('header', {}).get("token", "")
        if token != self.verification_token:
            log.error(f"verification token not match, token={token}")
            return json({"msg": "got invalid verification token"})
        event_type = data.get("type", "") or data.get('header', {}).get("event_type", "")
        event_handler = self.event_handlers.get(event_type, None)
        if not event_handler:
            msg = f"invalid event type:{event_type}"
            log.error(msg)
            return json({"msg": msg})
        return json(event_handler(data))

    def app(self) -> Sanic:
        app = Sanic(SERVER_NAME)
        app.add_route(self.handler, "/", methods=["POST"])
        return app

    def run(self):
        self.app().run(host=self.host, port=self.port)