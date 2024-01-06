#!/usr/bin/env python3
from enum import Enum
from typing import TypeVar, Type, Dict, Tuple

T = TypeVar('T')
S = TypeVar('S')


class Scope(Enum):
    SINGLETON = "SINGLETON"
    NO_SCOPE = "NO_SCOPE"


class AbstractModule:

    def __init__(self):
        self.mappings = dict()

    def bind(self, source: Type, to: Type, scope: Scope = Scope.SINGLETON) -> None:
        self.mappings[source] = (to, scope)

    def configure(self) -> None:
        pass

    def get_mappings(self) -> Dict[Type, Tuple[Type, Scope]]:
        return self.mappings


class MappingStore:

    def __init__(self):
        self.mappings = dict()

    def _load_modules(self, *modules: AbstractModule) -> None:
        for module in modules:
            module.configure()
            self.mappings.update(module.get_mappings())

    def get_actual_instance_with_scope(self, instance_class: Type[T]) -> Tuple[Type[S], Scope]:
        return self.mappings.get(instance_class, (instance_class, Scope.SINGLETON))

    @classmethod
    def create(cls, *modules: AbstractModule) -> 'MappingStore':
        store = cls()
        store._load_modules(*modules)
        return store


class Injector:

    def __init__(self, mapping_store: MappingStore):
        self.mapping_store = mapping_store
        self.services = dict()

    def _create(self, instance_class: Type[T]) -> T:
        arguments = dict()
        for key, requirement in instance_class.__init__.__annotations__.items():
            arguments[key] = self.get_instance(requirement)
        return instance_class(**arguments)

    def get_instance(self, instance_class: Type[T]) -> S:
        instance_class, instance_scope = self.mapping_store.get_actual_instance_with_scope(instance_class)
        if instance_scope == Scope.NO_SCOPE:
            return self._create(instance_class)
        if instance_class not in self.services:
            self.services[instance_class] = self._create(instance_class)
        return self.services[instance_class]


class PyJect:

    @staticmethod
    def create_injector(*modules: AbstractModule) -> Injector:
        store = MappingStore.create(*modules)
        return Injector(store)
