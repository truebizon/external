from enum import Enum

class _EnumWithValue(Enum):
    @classmethod
    def Value(cls, name: str):
        return cls[name].value

class UasState(_EnumWithValue):
    LANDING = 0
    INFLIGHT_OPERATING = 1
    INFLIGHT_MISSION_INTERRUPT = 2
    INFLIGHT = 3
    INFLIGHT_MISSION = 4
    INFLIGHT_MISSION_HOVER = 5
