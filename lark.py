import logging
import pprint
import sys

from errbot.core import ErrBot, Identifier
from errbot.backends.base import Person, Room, Message, RoomOccupant
from _lark.lark_server import LarkServer
from _lark.lark_client import LarkClient
from typing import Dict, Sequence

import json

from _lark.lark_bot import LarkBot
from _lark.lark_person import LarkPerson
from _lark.lark_room import LarkRoom, LarkRoomOccupant

log = logging.getLogger(__name__)


class LarkBackend(ErrBot, LarkServer):
    def __init__(self, bot_config):
        ErrBot.__init__(self, bot_config)
        identity = bot_config.BOT_IDENTITY
        LarkServer.__init__(self, identity)
        self.app_id = identity.get("app_id", None)
        self.app_secret = identity.get("app_secret", None)
        if not (self.app_id and self.app_secret):
            log.error("App Id and App Secert must be provided in the BOT_IDENTITY setting in your configuration")
            sys.exit(1)
        self.lc = None  # will be initialized in serve_once
        self.bot_identifier = None

    def serve_once(self):
        self.lc = LarkClient(app_id=self.app_id, app_secret=self.app_secret)
        self.bot_identifier = LarkBot(self.lc)
        try:
            self.connect_callback()  # notify that the connection occured
            self.run()
        except KeyboardInterrupt:
            log.info("Interrupt received, shutting down..")
            return True
        except Exception:
            log.exception("Error running Lark server!")
        finally:
            log.debug("Triggering disconnect callback")
            self.disconnect_callback()

    def _message_receive_handler(self, data: dict):
        """Callback event handler for the 'message' event"""
        log.debug("Saw an event: %s", pprint.pformat(data))

        event = data.get("event", {})
        message = event.get("message", {})
        msg_type = message.get("message_type", "")
        if msg_type != "text":
            log.warning("only support 'text' msg_type from now on, got:{msg_type}")
            return
        
        text = self._get_text_without_mentions(message)
        chat_type = message.get("chat_type", "").strip()
        sender = event.get("sender", {})
        sender_id = sender.get("sender_id", {})

        msg = Message(text, extras={"lark_event": data})
        if chat_type == 'p2p':
            msg.frm = LarkPerson(self.lc, sender_id.get("open_id"))
            msg.to = self.bot_identifier
        elif chat_type == "group":
            msg.frm = LarkRoomOccupant(self.lc, sender_id.get("open_id"), message.get("chat_id"), self)
            msg.to = LarkRoom(self.lc, message.get("chat_id"), bot=self)
        else:
            log.error(
                f"unknown chat_type:{chat_type} not in ['p2p', 'group']")

        self.callback_message(msg)

    def _get_text_without_mentions(self, message: dict):
        content_str = message.get("content", "")
        content = json.loads(content_str)
        text = content.get("text", "")
        
        for mention in message.get("mentions", []):
            text = text.replace(mention.get("key"), "")

        return text.strip()

    # implements/override methos from base.Backend/core.Errbot
    def send_message(self, msg: Message):
        super().send_message(msg)
        to_humanreadable = "<unknown>"
        receive_id = None
        receive_id_type = None
        memtion_id = None
        mention_name = None
        log.debug("message to: {}".format(msg.to))
        try:
            if isinstance(msg.to, RoomOccupant):
                memtion_id = msg.to.open_id
                memtion_name = msg.to.fullname
                receive_id = msg.to.room.chat_id
                to_humanreadable = msg.to.room.name
                receive_id_type = "chat_id"
            elif msg.is_group:
                receive_id = msg.to.chat_id
                to_humanreadable = msg.to.name
                receive_id_type = "chat_id"
            else:
                receive_id = msg.to.person
                memtion_id = receive_id
                to_humanreadable = msg.to.fullname
                memtion_name = to_humanreadable
                receive_id_type = "open_id"

            msgtype = "direct" if msg.is_direct else "channel"
            # chat_id > open_id
            log.debug('Sending %s message to %s (%s).', msgtype, to_humanreadable, receive_id)
            body = msg.body

            if memtion_id is not None:
                body = f'<at user_id="{memtion_id}">{memtion_name}</at>:\n{body}'

            log.debug('Message size: %d.', len(body))

            response = (self.lc.send_message(json.dumps({"text": body}), receive_id_type, receive_id, "text"))
            log.info('send message response %s', response)
            
        except Exception:
            log.exception(f'An exception occurred while trying to send the following message '
                f'to {to_humanreadable}: {msg.body}.')

    def _msg_id_for_message(self, msg: Message):
        return msg.extras["lark_event"]["event"]["message"]["message_id"]

    def change_presence(self, status: str, message: str) -> None:
        super().change_presence(status=status, message=message)
        pass

    def build_reply(self,
                    msg: Message,
                    text: str = None,
                    private: bool = False,
                    threaded: bool = False):
        response = self.build_message(text)
        response.parent = msg
        response.frm = self.bot_identifier
        response.to = msg.frm
        # if private:
        #     response.to = msg.frm
        # else:
        #     response.to = .room if isinstance(msg.frm, RoomOccupant) else msg.frm
        return response

    def prefix_groupchat_reply(self, message: Message, identifier: Person):
        super().prefix_groupchat_reply(message, identifier)
        message.body = f'<at user_id="{identifier.person}">{identifier.nick}</at>:\n{message.body}'  # nick == fullname

    def build_identifier(self, txt_rep: str) -> Identifier:
        """
        txt_rep: {open_id}:{open_chat_id}:{chat_type}
        """
        log.debug("build idetifier txt: {}".format(txt_rep))

        # only open_id can be used to identify a unique person
        open_id, open_chat_id, chat_type = self._extract_identifiers_from_str(txt_rep)
        if open_id and chat_type == "p2p":
            return LarkPerson(lc=self.lc, open_id=open_id)
        if open_id and open_chat_id and chat_type == "group":
            return LarkRoomOccupant(lc=self.lc, open_id=open_id, chat_id=open_chat_id, bot=self)
        if open_chat_id:
            return LarkRoom(lc=self.lc, chat_id=open_chat_id, bot=self)

        raise Exception(
            "You found a bug. I expected at least one of open_id, open_chat_id, or chat_type "
            "to be resolved but none of them were. This shouldn't happen so, please file a bug."
        )

    @staticmethod
    def _extract_identifiers_from_str(text):
        """
        text: {open_id}:{open_chat_id}:{chat_type}
        """
        exception_message = "invalid identifiers str, except:oc_xxx/oc_xxx/[p2p|group]"
        text = text.strip()
        if not text:
            raise ValueError(exception_message)

        open_id = None
        open_chat_id = None
        chat_type = "p2p"
        chat_types = ["p2p", "group"]
        items = text.split(":")
        for item in items:
            item_ = item.strip()
            if item_.startswith("ou_"):
                open_id = item_
            elif item_.startswith("oc_"):
                open_chat_id = item_
            elif item_ in chat_types:
                chat_type = item_
            else:
                raise ValueError(exception_message)
        return open_id, open_chat_id, chat_type

    def query_room(self, room: str) -> Room:
        pass

    @property
    def mode(self):
        return "lark"

    @property
    def rooms(self) -> Sequence[Room]:
        # just return <=100 rooms
        chat_list_resp = (self.lc.chat_list())
        chat_groups = chat_list_resp.data.get("groups", None)
        return [LarkRoom(lc=self.lc,chat_id=group["chat_id"], bot=self) for group in chat_groups] if chat_groups else []