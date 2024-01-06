from typing import Type, Tuple, Callable, Generator, Optional, Any

from pyject.common import Scope, AbstractModule
from pyject.utils import get_return_type


class DependencyInfo:
    def __init__(self, instance_class: Type, scope: Scope, constructor: Optional[Callable[..., Any]] = None):
        self.instance_class = instance_class
        self.scope = scope
        self.constructor = constructor


class MappingStore:

    def __init__(self):
        self.mappings = dict()

    def _get_provider_methods(self, module: AbstractModule) -> Generator[Tuple[Type, Callable[..., Any]], None, None]:
        method_list = [func for func in dir(module) if callable(getattr(module, func))]
        for method in method_list:
            if method.startswith("get_"):
                provider = getattr(module, method)
                yield get_return_type(provider), provider
                #yield getattr(module, method)()

    def _load_modules(self, *modules: AbstractModule) -> None:
        for module in modules:
            module.configure()
            for mapping, (target_type, scope) in module.mappings.items():
                self.mappings[mapping] = DependencyInfo(target_type, scope)
            for mapped_type, constructor in self._get_provider_methods(module):
                self.mappings[mapped_type] = DependencyInfo(mapped_type, Scope.SINGLETON, constructor)

    def get_actual_instance_with_scope(self, instance_class: Type) -> DependencyInfo:
        return self.mappings.get(instance_class,
                                 DependencyInfo(instance_class, Scope.SINGLETON))

    @classmethod
    def create(cls, *modules: AbstractModule) -> 'MappingStore':
        store = cls()
        store._load_modules(*modules)
        return store
