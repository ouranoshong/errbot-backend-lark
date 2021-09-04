from _lark.lark_client import LarkClient
import logging
import unittest

from mock.mock import AsyncMock
from _lark.lark_bot import LarkBot
from _lark.lark_response import LarkResponse

log = logging.getLogger(__name__)

class LartBotTests(unittest.TestCase):

    def setUp(self) -> None:
        self.lc = AsyncMock(LarkClient)
        self.bot = LarkBot(lc=self.lc, open_id='ou_xxxxx', app_name='app_name_xxxx')

    def testFullName(self):
        self.assertEqual(self.bot.fullname, 'app_name_xxxx')

    def testInitWithNoOpenId(self):
        lc = AsyncMock(LarkClient)
        bot = {"open_id": "ou_bot_id", "app_name": "bot_app_name"}
        attrs = {"bot_info.return_value": LarkResponse(code = 200, msg='success', data = {"bot": bot})}
        lc.configure_mock(**attrs)
        bot = LarkBot(lc=lc)
        self.assertEqual(bot.fullname, "bot_app_name")

        bot = {"open_id": "ou_bot_id", "app_name": "bot_app_name"}
        attrs = {"bot_info.return_value": LarkResponse(code = 200, msg='success', data = {})}
        lc.configure_mock(**attrs)

        with self.assertRaises(RuntimeError):
            LarkBot(lc=lc)
