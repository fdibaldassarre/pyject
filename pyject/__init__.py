import typing
from logging import getLogger
from typing import TypeVar, Type, Any, Optional

from pyject.annotations import Provider
from pyject.common import Scope, AbstractModule, DependencyIdentifier
from pyject.mapper import MappingStore, DependencyInfo
from pyject.utils import get_type_annotations, get_default_args

T = TypeVar('T')
S = TypeVar('S')


class AbstractInjector:

    def get_instance(self, instance_class: Type[S], instance_name: Optional[str] = None) -> S:
        raise NotImplementedError()


class ProviderImpl(Provider):

    def __init__(self, injector: AbstractInjector, dep_type: Type[S]):
        self.injector = injector
        self.dep_type = dep_type

    def get(self, name: Optional[str]) -> S:
        return self.injector.get_instance(self.dep_type, name)


class Injector(AbstractInjector):

    def __init__(self, mapping_store: MappingStore):
        self.mapping_store = mapping_store
        self.services = dict()
        self.logging = getLogger(Injector.__name__)

    def _create(self, instance_info: DependencyInfo) -> T:
        instance_class = instance_info.instance_class
        if typing.get_origin(instance_class) == Provider:
            # Class Provider
            source = typing.get_args(instance_class)[0]
            return ProviderImpl(self, source)
        instance_constructor = instance_info.constructor
        args = instance_info.get_requirements()
        arguments = dict()
        for key, requirement in args.items():
            if key not in arguments:
                arguments[key] = self._get_instance(requirement)
        self.logging.debug(f"Creating {instance_info.instance_class} [{instance_info.instance_name}]")
        return instance_class(**arguments) if instance_constructor is None else instance_constructor(**arguments)

    def _get_instance(self, ide: DependencyIdentifier) -> Any:
        instance_info = self.mapping_store.get_actual_instance_with_scope(ide)
        if instance_info.scope == Scope.NO_SCOPE:
            return self._create(instance_info)
        if ide not in self.services:
            self.services[ide] = self._create(instance_info)
        return self.services[ide]

    def get_instance(self, instance_class: Type[S], instance_name: Optional[str] = None) -> S:
        return self._get_instance(DependencyIdentifier(instance_class, instance_name))


class PyJect:

    @staticmethod
    def create_injector(*modules: AbstractModule) -> Injector:
        store = MappingStore.create(*modules)
        return Injector(store)
