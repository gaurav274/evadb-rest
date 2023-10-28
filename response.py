from flask import Response as Resp
from enum import Enum
import json

class Response:
    def __init__(self, type, data = [], msg=""):
        self.type = type or Type.TABLE.name
        self.data = data
        self.msg = msg

    def json(self):
        if type(self.data) is str:
            self.data = json.loads(self.data)
        return json.dumps({"type": self.type, "data": self.data, "msg": self.msg})

    def generate(self, status = 200, mimetype = "text/json"):
        resp = Resp(
            response=self.json(),
            status=status,
            mimetype=mimetype
        )
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp


class Type(Enum):
    TABLE = 1
    ERROR = 2