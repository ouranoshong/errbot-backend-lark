from errbot.backends.base import Message
from errbot.core import ErrBot
import mock
from _lark.lark_response import LarkResponse
from _lark.lark_room import LarkRoom, LarkRoomOccupant
from _lark.lark_person import LarkPerson
from _lark.lark_client import LarkClient
from mock.mock import AsyncMock, Mock
from _lark.lark_bot import LarkBot
import logging
import os
import sys
import unittest
from tempfile import mkdtemp

from mock import MagicMock

from errbot.bootstrap import bot_config_defaults

log = logging.getLogger(__name__)

try:
    from lark import LarkBackend

    class TestLarkBackend(LarkBackend):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.test_msgs = []
            self.lc = AsyncMock(LarkClient)

            attrs = {
                "chat_info.return_value":
                LarkResponse(code=200,
                             msg='success',
                             data={"name": "chat_name_from_api"})
            }
            self.lc.configure_mock(**attrs)

        def callback_message(self, msg):
            self.test_msgs.append(msg)

except SystemExit:
    log.exception("Can't import lark for testing")


class LarkTests(unittest.TestCase):
    def setUp(self):
        tempdir = mkdtemp()

        sys.modules.pop("errbot.config-template", None)
        __import__("errbot.config-template")
        config = sys.modules["errbot.config-template"]
        bot_config_defaults(config)

        config.BOT_DATA_DIR = tempdir
        config.BOT_LOG_FILE = os.path.join(tempdir, "log.txt")
        config.BOT_EXTRA_PLUGIN_DIR = []
        config.BOT_LOG_LEVEL = logging.DEBUG
        config.BOT_IDENTITY = {
            "app_id": "cli_xxxxxxx",
            "app_secret": "xxxxxxxxxxxxxxxxxx",
            "verification_token": "xxxxxxxxxxxx",
            "encrypt_key": None,
            "host": "0.0.0.0",
            "port": 8000
        }

        self.lark = TestLarkBackend(config)

    def testExtractIdentifiers(self):
        extract_from = self.lark._extract_identifiers_from_str

        self.assertEqual(extract_from("ou_1:ou_1:private"),
                         ('ou_1', None, 'private'))
        self.assertEqual(extract_from("ou_1:oc_1:group"),
                         ('ou_1', 'oc_1', 'group'))

        with self.assertRaises(ValueError):
            extract_from("")

        with self.assertRaises(ValueError):
            extract_from("ou_1:oc_1:error")

    def testMessageReceiveEventHandler(self):
        event = {
            "event": {
                "message": {
                    "chat_id":
                    "oc_10223736212f5da6611c201bf8b8f08e",
                    "chat_type":
                    "p2p",
                    "content":
                    "{\"text\":\"@_user_1 !help\"}",
                    "create_time":
                    "1629775246904",
                    "mentions": [{
                        "id": {
                            "open_id": "ou_d07534xxx",
                            "union_id": "on_01bxxxxxxxxxxxxxxxxxxx",
                            "user_id": ""
                        },
                        "key": "@_user_1",
                        "name": "用于测试的应用",
                        "tenant_key": "127ed14fa54e1740"
                    }],
                    "message_id":
                    "om_e6767f0fe272a0a342ee0b9aa88c3f45",
                    "message_type":
                    "text"
                },
                "sender": {
                    "sender_id": {
                        "open_id": "ou_d91f1xxxxxxxxxxx",
                        "union_id": "on_6af3510xxxxxxxxxxxxxxxxxxxx",
                        "user_id": "c3ad911d"
                    },
                    "sender_type": "user",
                    "tenant_key": "127ed14fa54e1740"
                }
            },
            "header": {
                "app_id": "cli_a191d9ded83b9013",
                "create_time": "1629775247204",
                "event_id": "86fc82718ae8aef54ef65e9fb2b6ebe4",
                "event_type": "im.message.receive_v1",
                "tenant_key": "127ed14fa54e1740",
                "token": "UJm7yT0w7sN7BPTwTEGovhll3Lai0gPG"
            },
            "schema": "2.0"
        }

        lc = AsyncMock(LarkClient)
        bot = LarkBot(lc, 'ou_d07534xxx', '用于测试的应用')
        self.lark.bot_identifier = bot

        self.lark._message_receive_handler(event)
        msg = self.lark.test_msgs.pop()

        self.assertEqual(msg.extras["lark_event"], event)
        self.assertEqual(msg.body, '!help')
        self.assertEqual(msg.to, bot)
        self.assertEqual(msg.frm, LarkPerson(lc, 'ou_d91f1xxxxxxxxxxx'))

        group_event = {
            "event": {
                "message": {
                    "chat_id":
                    "oc_ccf285841c47eb3048d0ab0e851fb444",
                    "chat_type":
                    "group",
                    "content":
                    "{\"text\":\"@_user_1 测试\"}",
                    "create_time":
                    "1629776679977",
                    "mentions": [{
                        "id": {
                            "open_id": "ou_d07534xxx",
                            "union_id": "on_01bxxxxxxxxxxxxxxxxxxx",
                            "user_id": ""
                        },
                        "key": "@_user_1",
                        "name": "用于测试的应用",
                        "tenant_key": "127ed14fa54e1740"
                    }],
                    "message_id":
                    "om_e51e62ddc911334e8ce31713ddf79725",
                    "message_type":
                    "text"
                },
                "sender": {
                    "sender_id": {
                        "open_id": "ou_d91f1xxxxxxxxxxx",
                        "union_id": "on_6af3510xxxxxxxxxxxxxxxxxxxx",
                        "user_id": "c3ad911d"
                    },
                    "sender_type": "user",
                    "tenant_key": "127ed14fa54e1740"
                }
            },
            "header": {
                "app_id": "cli_a191d9ded83b9013",
                "create_time": "1629776680491",
                "event_id": "abda9130e27a66c85c777e9ab3ec4259",
                "event_type": "im.message.receive_v1",
                "tenant_key": "127ed14fa54e1740",
                "token": "UJm7yT0w7sN7BPTwTEGovhll3Lai0gPG"
            },
            "schema": "2.0"
        }

        attrs = {
            "chat_info.return_value":
            LarkResponse(code=200,
                         msg='success',
                         data={"name": "chat_name_from_api"})
        }
        lc.configure_mock(**attrs)

        self.lark._message_receive_handler(group_event)
        msg = self.lark.test_msgs.pop()

        self.assertEqual(msg.body, '测试')
        self.assertEqual(
            msg.frm, LarkRoomOccupant(lc, 'ou_d91f1xxxxxxxxxxx', 'oc_ccf285841c47eb3048d0ab0e851fb444', self.lark))
        self.assertEqual(msg.to.name, 'chat_name_from_api')

    def testBuildIdentifier(self):
        self.assertIsInstance(
            self.lark.build_identifier('ou_person:ou_person:private'),
            LarkPerson)
        self.assertIsInstance(
            self.lark.build_identifier('ou_person:oc_chat_id:group'),
            LarkRoomOccupant)
        self.assertIsInstance(
            self.lark.build_identifier('oc_chat_id:oc_chat_id:group'),
            LarkRoom)

    def testSendMessage(self):
        # attrs = {"message_md_send.return_value": LarkResponse(code = 200, msg='success', data = {"name": "chat_name_from_api"})}
        # self.lc.configure_mock(**attrs)

        message_md_send = AsyncMock()
        message_md_send.return_value = LarkResponse(
            code=200, msg='success', data={"name": "chat_name_from_api"})
        self.lark.lc.message_md_send = message_md_send
        with mock.patch.object(ErrBot, "send_message") as mock_send_message:
            msg = Message('!help', extras={"lark_event": {}})
            msg.to = MagicMock(LarkPerson)
            msg.to.person = Mock()
            msg.to.person.return_value = 'ou_person'
            msg.to.fullname = Mock()
            msg.to.fullname.return_value = 'fullname'
            self.lark.send_message(msg)
            message_md_send.assert_called_once_with(md='!help',
                                                    open_id=msg.to.person,
                                                    chat_id=None,
                                                    root_id=None)
            mock_send_message.assert_called_once_with(msg)

        message_md_send = AsyncMock()
        message_md_send.return_value = LarkResponse(
            code=200, msg='success', data={"name": "chat_name_from_api"})
        self.lark.lc.message_md_send = message_md_send
        with mock.patch.object(ErrBot, "send_message") as mock_send_message:
            msg = Message('!help', extras={"lark_event": {}})
            msg.to = MagicMock(LarkRoom)
            msg.to.chat_id = Mock()
            msg.to.chat_id.return_value = 'oc_chat_id'
            msg.to.name = Mock()
            msg.to.name.return_value = 'name'
            self.lark.send_message(msg)
            message_md_send.assert_called_once_with(md='!help',
                                                    open_id=None,
                                                    chat_id=msg.to.chat_id,
                                                    root_id=None)
            mock_send_message.assert_called_once_with(msg)

        message_md_send = AsyncMock()
        message_md_send.return_value = LarkResponse(
            code=200, msg='success', data={"name": "chat_name_from_api"})
        self.lark.lc.message_md_send = message_md_send
        with mock.patch.object(ErrBot, "send_message") as mock_send_message:
            msg = Message(
                '!help',
                extras={"lark_event": {
                    "open_message_id": "om_message_id"
                }})
            msg.parent = Message('!help parent',
                                 extras={
                                     "lark_event": {
                                         "open_message_id":
                                         "om_parent_message_id"
                                     }
                                 })
            msg.to = MagicMock(LarkRoomOccupant)
            msg.to.room = MagicMock(LarkRoom)
            msg.to.room.chat_id = Mock()
            msg.to.room.chat_id.return_value = 'oc_room_chat_id'
            msg.to.room.name = Mock()
            msg.to.room.name.return_value = 'oc_room_name'

            self.lark.send_message(msg)
            message_md_send.assert_called_once_with(
                md='!help',
                open_id=None,
                chat_id=msg.to.room.chat_id,
                root_id='om_parent_message_id')
            mock_send_message.assert_called_once_with(msg)
