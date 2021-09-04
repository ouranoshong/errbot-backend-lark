from _lark.lark_response import LarkResponse
from _lark.lark_client import LarkClient
import logging
import unittest

from mock.mock import AsyncMock

log = logging.getLogger(__name__)

from _lark.lark_room import LarkRoom
from _lark.lark_bot import LarkBot

class LarkRoomTests(unittest.TestCase):
    def setUp(self) -> None:
        
        b = AsyncMock(LarkBot)
        lc = AsyncMock(LarkClient)
        attrs = {"chat_info.return_value": LarkResponse(code = 200, msg='success', data = {"name": "chat_name_from_api"})}
        lc.configure_mock(**attrs)

        r = LarkRoom(lc=lc, chat_id="oc_xxxx", name="room_name", bot=b)
        self.r = r

    def testGetterSetter(self):
        self.assertEqual(self.r.chat_id, "oc_xxxx")
        self.assertEqual(self.r.name, "chat_name_from_api")
    
    def testToString(self):
        self.assertEqual('{}'.format(self.r), "oc_xxxx")