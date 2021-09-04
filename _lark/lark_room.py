from _lark.lark_client import LarkClient
import logging

from errbot.backends.base import Room
from errbot.backends.base import RoomOccupant
from _lark.lark_client import LarkClient
from _lark.lark_person import LarkPerson

log = logging.getLogger(__name__)

class LarkRoom(Room):
    def __init__(self, lc: LarkClient, chat_id: str = None, name: str = None, bot=None):
        self._chat_id = chat_id
        self._name = name
        self._bot = bot
        self._lc = lc

        if self._chat_id:
            self._name = self._chat_info["name"]

    @property
    def chat_id(self):
        return self._chat_id

    @property
    def name(self):
        return self._name

    @property
    def _chat_info(self):
        chat_info_resp = (self._lc.chat_info(self.chat_id))
        return chat_info_resp.data

    def __str__(self):
        return self._chat_id

    def join(self, username=None, password=None):
        pass

    def leave(self, reason=None):
        pass

    def create(self):
        pass

    def destroy(self):
        (self._lc.chat_disband(self.chat_id))
        

    def invite(self, *args):
        open_ids = [open_id for open_id in args]
        (self.lc.chat_chatter_add(self.chat_id, open_ids))
        

    @property
    def exists(self):
        pass

    @property
    def joined(self):
        pass

    @property
    def topic(self):
        return self.name

    @topic.setter
    def topic(self, topic):
        (self._lc.chat_update(self.chat_id, topic))

    @property
    def occupants(self):
        members = self._chat_info["members"]
        return [
            LarkRoomOccupant(self._lc, m["open_id"], self.chat_id, self._bot)
            for m in members
        ]


class LarkRoomOccupant(RoomOccupant, LarkPerson):
    def __init__(self, lc: LarkClient, open_id: str, chat_id: str, bot):
        super().__init__(lc, open_id)
        self._room = LarkRoom(lc=lc, chat_id=chat_id, bot=bot)

    @property
    def room(self):
        return self._room

    def __unicode__(self):
        return f'{self._open_id}:{self._room.chat_id}:group'

    def __str__(self):
        return self.__unicode__()

    def __eq__(self, other):
        if not isinstance(other, RoomOccupant):
            log.warning(
                "tried to compare a LarkRoomOccupant with a LarkPerson %s vs %s",
                self,
                other,
            )
            return False
        return other.room.chat_id == self.room.chat_id and other.open_id == self.open_id