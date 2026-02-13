import json
import pickle
from typing import Any


class Serializer:
    @staticmethod
    def dumps(obj: Any) -> bytes:
        raise NotImplementedError

    @staticmethod
    def loads(data: bytes) -> Any:
        raise NotImplementedError


class PickleSerializer(Serializer):
    @staticmethod
    def dumps(obj: Any):
        return pickle.dumps(obj)

    @staticmethod
    def loads(data: bytes):
        return pickle.loads(data)


class JsonSerializer(Serializer):
    @staticmethod
    def dumps(obj: Any):
        return json.dumps(obj)

    @staticmethod
    def loads(data: bytes):
        return json.loads(data)
