from enum import Enum
from typing import Type, Optional, Dict, Tuple


class DependencyIdentifier:

    def __init__(self, dep_type: Type, name: Optional[str] = None):
        self.type = dep_type
        self.name = name

    def __hash__(self):
        return hash((self.type, self.name))

    def __eq__(self, other):
        if not isinstance(other, DependencyIdentifier):
            return False
        if self.type != other.type:
            return False
        if self.name is None and other.name is not None:
            return False
        return self.name == other.name

    def __str__(self):
        return str((self.type, self.name))


class Scope(Enum):
    SINGLETON = "SINGLETON"
    NO_SCOPE = "NO_SCOPE"


class AbstractModule:

    def __init__(self):
        self.mappings: Dict[DependencyIdentifier, Tuple[Type, Scope]] = dict()

    def bind(self, source: Type, to: Type, scope: Scope = Scope.SINGLETON, named: Optional[str] = None) -> None:
        self.mappings[DependencyIdentifier(source, named)] = (to, scope)

    def configure(self) -> None:
        ...
