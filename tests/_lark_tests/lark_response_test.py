import logging
import unittest

from _lark.lark_response import CODE, LarkResponse

log = logging.getLogger(__name__)

import _lark.lark_response as lr


class LarkResponseTests(unittest.TestCase):
    def setUp(self):
        self._lr = lr.LarkResponse(
            code=lr.SUCCESS_CODE,
            msg="lark resonse message",
            data={"data": "data"}
        )

    def testCodeGetterSetter(self):
        self._lr.code = 'code'
        self.assertEqual(self._lr.code, 'code')

    def testMsgGetterSetter(self):
        self._lr.msg = 'msg1'
        self.assertEqual(self._lr.msg, 'msg1')
    
    def testDataGetterSetter(self):
        self._lr.data = {'data': 'data1'}
        self.assertDictEqual(self._lr.data, {'data': 'data1'})

    def testLarkResponseFormat(self):
        r = lr.LarkResponse(
            code=lr.SUCCESS_CODE,
            msg="lark resonse message",
            data={"data": "data"}
        )

        self.assertEqual('{}'.format(r), "LarkResponse[code=0 msg=lark resonse message data={'data': 'data'}]")


    def testErrorResponse(self):
        r = lr.error(Exception)
        self.assertEqual('{}'.format(r), "LarkResponse[code=-1 msg=<class 'Exception'> data={}]")


    def testOfResponse(self):
        resp = {}
        resp[lr.CODE] = lr.SUCCESS_CODE
        resp[lr.MSG] = "success"
        resp[lr.DATA] = {"data": "data"}

        # resp.get
        r = lr.of(resp)
        self.assertEqual('{}'.format(r), "LarkResponse[code=0 msg=success data={'data': 'data'}]")

        r = lr.of({})
        self.assertEqual('{}'.format(r), "LarkResponse[code=-1 msg=error data={}]")

        resp = {}
        resp[lr.CODE] = lr.SUCCESS_CODE
        resp[lr.MSG] = "success"
        resp['test'] = "data"
        r = lr.of(resp)
        self.assertEqual('{}'.format(r), "LarkResponse[code=0 msg=success data={'test': 'data'}]")
