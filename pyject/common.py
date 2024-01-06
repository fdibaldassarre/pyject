from enum import Enum
from typing import Type


class Scope(Enum):
    SINGLETON = "SINGLETON"
    NO_SCOPE = "NO_SCOPE"


class AbstractModule:

    def __init__(self):
        self.mappings = dict()

    def bind(self, source: Type, to: Type, scope: Scope = Scope.SINGLETON) -> None:
        self.mappings[source] = (to, scope)

    def configure(self) -> None:
        ...
