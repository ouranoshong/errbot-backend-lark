from _lark.lark_server import LarkServer
from sanic import Sanic
from sanic_testing import TestManager
import unittest


class LarkServerTests(unittest.TestCase):

    _app: Sanic

    def setUp(self):
        self._config = {"verification_token": "verification_token"}
        self._server = LarkServer(self._config)
        self._app = self._server.app()
        TestManager(self._app)

    def testNoToken(self):
        _, response = self._app.test_client.post("/", json={})
        self.assertEqual(response.json,
                         {'msg': 'got invalid verification token'})

    def testUrlVerify(self):
        request, response = self._app.test_client.post(
            "/",
            json={
                "challenge": "ajls384kdjx98XX",
                "token": self._config.get("verification_token"),
                "type": "url_verification"
            })

        self.assertEqual(response.json, {"challenge": "ajls384kdjx98XX"})

    def testMessageReceiveV1Handler(self):
        def handler(data: dict):
            return data.get("schema", "")

        self._server.update_event_handlers({"im.message.receive_v1": handler})
        _, response = self._app.test_client.post(
            "/",
            json={
                "schema": "2.0",
                "header": {
                    "event_id": "5e3702a84e847582be8db7fb73283c02",
                    "event_type": "im.message.receive_v1",
                    "create_time": "1608725989000",
                    "token": self._config.get("verification_token"),
                    "app_id": "cli_9f5343c580712544",
                    "tenant_key": "2ca1d211f64f6438"
                },
                "event": {
                    "sender": {
                        "sender_id": {
                            "union_id": "on_8ed6aa67826108097d9ee143816345",
                            "user_id": "e33ggbyz",
                            "open_id": "ou_84aad35d084aa403a838cf73ee18467"
                        },
                        "sender_type": "user",
                        "tenant_key": "736588c9260f175e"
                    },
                    "message": {
                        "message_id":
                        "om_5ce6d572455d361153b7cb51da133945",
                        "root_id":
                        "om_5ce6d572455d361153b7cb5xxfsdfsdfdsf",
                        "parent_id":
                        "om_5ce6d572455d361153b7cb5xxfsdfsdfdsf",
                        "create_time":
                        "1609073151345",
                        "chat_id":
                        "oc_5ce6d572455d361153b7xx51da133945",
                        "chat_type":
                        "group",
                        "message_type":
                        "text",
                        "content":
                        "{\"text\":\"@_user_1 hello\"}",
                        "mentions": [{
                            "key": "@_user_1",
                            "id": {
                                "union_id":
                                "on_8ed6aa67826108097d9ee143816345",
                                "user_id": "e33ggbyz",
                                "open_id": "ou_84aad35d084aa403a838cf73ee18467"
                            },
                            "name": "Tom",
                            "tenant_key": "736588c9260f175e"
                        }]
                    }
                }
            })

        self.assertEqual(response.json, "2.0")
