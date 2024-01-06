from typing import TypeVar, Type

from pyject.common import Scope, AbstractModule
from pyject.mapper import MappingStore, DependencyInfo
from pyject.types import Named
from pyject.utils import get_type_annotations, get_default_args

T = TypeVar('T')
S = TypeVar('S')


class Injector:

    def __init__(self, mapping_store: MappingStore):
        self.mapping_store = mapping_store
        self.services = dict()

    def _create(self, instance_info: DependencyInfo) -> T:
        instance_class = instance_info.instance_class
        instance_constructor = instance_info.constructor
        if instance_constructor is None:
            args = get_type_annotations(instance_class.__init__)
            var_args = get_default_args(instance_class.__init__)
        else:
            args = get_type_annotations(instance_constructor)
            var_args = get_default_args(instance_constructor)
        arguments = dict()
        # Named args
        for key, value in var_args.items():
            if hasattr(value, "__origin__") and value.__origin__ == Named:
                # Named argument
                arguments[key] = self.get_instance(value)
            else:
                # Normal vararg
                arguments[key] = value
        # Other args
        for key, requirement in args.items():
            if key not in arguments:
                arguments[key] = self.get_instance(requirement)
        return instance_class(**arguments) if instance_constructor is None else instance_constructor(**arguments)

    def get_instance(self, instance_class: Type) -> S:
        instance_info = self.mapping_store.get_actual_instance_with_scope(instance_class)
        if instance_info.scope == Scope.NO_SCOPE:
            return self._create(instance_info)
        if instance_info.instance_class not in self.services:
            self.services[instance_class] = self._create(instance_info)
        return self.services[instance_class]


class PyJect:

    @staticmethod
    def create_injector(*modules: AbstractModule) -> Injector:
        store = MappingStore.create(*modules)
        return Injector(store)
