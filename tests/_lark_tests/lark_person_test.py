import logging
import unittest

from _lark.lark_client import LarkClient
from _lark.lark_person import LarkPerson
from _lark.lark_response import LarkResponse
from mock import AsyncMock

log = logging.getLogger(__name__)


class LarkPersonTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lc = AsyncMock(LarkClient)
        self.person = LarkPerson(lc=self.lc, open_id='ou_xxxx')

    def testOpenId(self):
        self.assertEqual(self.person.open_id, 'ou_xxxx')

    def testClient(self):
        self.assertEqual(self.person.client, 'Lark')

    def testFullName(self):
        lc = AsyncMock(LarkClient)
        attrs = {
            "user_batch_get.return_value":
            LarkResponse(code=200,
                         msg='success',
                         data={"user_infos": [{
                             "name": "user_name"
                         }]})
        }
        lc.configure_mock(**attrs)
        person = LarkPerson(lc=lc, open_id='ou_xxxx')
        self.assertEqual(person.fullname, 'user_name')

        attrs = {
            "user_batch_get.return_value":
            LarkResponse(code=200,
                         msg='success',
                         data={"user_infos": []})
        }
        lc.configure_mock(**attrs)
        person = LarkPerson(lc=lc, open_id='ou_xxxx')
        self.assertEqual(person.fullname, '<ou_xxxx>')

    def testUserGet(self):
        user = {"name": "user_name"}
        attrs = {
            "user_batch_get.return_value":
            LarkResponse(code=200, msg='success', data={"user_infos": [user]})
        }
        lc = AsyncMock(LarkClient)
        lc.configure_mock(**attrs)
        person = LarkPerson(lc=lc, open_id='ou_xxxx')
        self.assertDictEqual(person.user_get(['ou_xxxx']), user)

    def testToString(self):
        self.assertEqual('{}'.format(self.person), "ou_xxxx")

    def testComparation(self):
        p1 = LarkPerson(lc=self.lc, open_id='ou_xxxx_1')
        p2 = LarkPerson(lc=self.lc, open_id='ou_xxxx_2')

        t = 'test'

        self.assertFalse(p1 == p2)
        self.assertTrue(p1 == p1)
        self.assertFalse(p1 == t)

        p1 = LarkPerson(lc=self.lc, open_id='ou_xxxx_1')

        s = set()
        s.add(p1)

        self.assertTrue(p1 in s)