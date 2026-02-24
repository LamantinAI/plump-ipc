from dataclasses import dataclass

from plump_ipc import JsonSerializer, PickleSerializer


@dataclass
class MockData:
    id: int
    name: str


def test_json_serialization_basic():
    serializer = JsonSerializer()
    data = {"id": 1, "meta": [1, 2, 3], "active": True}

    encoded = serializer.dumps(data)
    decoded = serializer.loads(encoded)

    assert decoded == data
    assert isinstance(encoded, bytes)


def test_pickle_serialization_complex_obj():
    serializer = PickleSerializer()
    obj = MockData(id=42, name="Plump")

    encoded = serializer.dumps(obj)
    decoded = serializer.loads(encoded)

    assert decoded.id == 42
    assert decoded.name == "Plump"
    assert isinstance(decoded, MockData)
