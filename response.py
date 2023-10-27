from enum import Enum
import json

class Response:
    def __init__(self, type, data = list(), msg=""):
        self.type = type or Type.TABLE.name
        self.data = data
        self.msg = msg

    def json(self):
        return json.dumps({"type": self.type, "data": self.data, "msg": self.msg})


class Type(Enum):
    TABLE = 1
    ERROR = 2