import logging

from _lark.lark_client import LarkClient

from _lark.lark_person import LarkPerson

log = logging.getLogger(__name__)


class LarkBot(LarkPerson):
    def __init__(self,
                 lc: LarkClient,
                 open_id: str = None,
                 app_name: str = None):
        self._lc = lc
        if not (open_id and app_name):
            bot = self.bot_get()
            if not bot:
                raise RuntimeError(
                    "can't get bot info, please check your app_id && app_secret, and ensure your robot ability"
                )
            open_id = bot["open_id"]
            app_name = bot["app_name"]
        super().__init__(lc=lc, open_id=open_id)
        self._app_name = app_name

    @property
    def fullname(self):
        return self._app_name

    def bot_get(self):
        bot_resp = (self._lc.bot_info())
        return bot_resp.data.get("bot", None)