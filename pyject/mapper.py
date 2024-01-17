from logging import getLogger
from typing import Type, Tuple, Callable, Generator, Optional, Any, Dict, List

from pyject.annotations import PyjectConstructor
from pyject.common import Scope, AbstractModule, DependencyIdentifier
from pyject.utils import get_return_type, get_type_annotations


class DependencyInfo:
    def __init__(self,
                 instance_class: Type,
                 scope: Scope,
                 constructor: Optional[Callable[..., Any]] = None,
                 instance_name: Optional[str] = None,
                 requirements_names: Optional[Dict[str, str]] = None
                 ):
        self.instance_class = instance_class
        self.scope = scope
        self.instance_name = instance_name
        self.constructor = constructor
        self.requirements_names = requirements_names

    def get_requirements(self) -> Dict[str, DependencyIdentifier]:
        if self.constructor is None:
            args = get_type_annotations(self.instance_class.__init__)
            #var_args = get_default_args(instance_class.__init__)
        else:
            args = get_type_annotations(self.constructor)
            #var_args = get_default_args(instance_constructor)
        result = dict()
        for name, dep_type in args.items():
            dep_name = self.requirements_names.get(name) if self.requirements_names is not None else None
            result[name] = DependencyIdentifier(dep_type, dep_name)
        return result

    @staticmethod
    def build(instance_class: Type,
              scope: Scope,
              constructor: Optional[Callable[..., Any]] = None,
              ) -> 'DependencyInfo':
        if isinstance(constructor, PyjectConstructor):
            instance_name = constructor.__instance_name__
            requirements_names = constructor.__named_args__
        else:
            instance_name = None
            requirements_names = None
        return DependencyInfo(instance_class, scope, constructor,
                              instance_name=instance_name, requirements_names=requirements_names)


class MappingStore:

    def __init__(self):
        self.mappings: Dict[DependencyIdentifier, DependencyInfo] = dict()
        self.logger = getLogger(MappingStore.__name__)

    def _get_provider_methods(self, module: AbstractModule) -> Generator[Tuple[Type, Callable[..., Any]], None, None]:
        method_list = [func for func in dir(module) if callable(getattr(module, func))]
        for method in method_list:
            if method.startswith("get_"):
                provider = getattr(module, method)
                yield get_return_type(provider), provider

    def _load_modules(self, *modules: AbstractModule) -> None:
        for module in modules:
            module.configure()
            for mapping, (target_type, scope) in module.mappings.items():
                self.logger.debug(f"Bind {mapping.type} [{mapping.name}] to {target_type}")
                self.mappings[mapping] = DependencyInfo.build(target_type, scope)
            for mapped_type, constructor in self._get_provider_methods(module):
                dep_info = DependencyInfo.build(mapped_type, Scope.SINGLETON, constructor)
                self.logger.debug(f"Bind {dep_info.instance_class} [{dep_info.instance_name}] to provider")
                self.mappings[DependencyIdentifier(dep_info.instance_class, dep_info.instance_name)] = dep_info

    def get_actual_instance_with_scope(self, ide: DependencyIdentifier) -> DependencyInfo:
        if ide.name is not None:
            return self.mappings[ide]
        else:
            return self.mappings.get(ide,
                                     DependencyInfo.build(ide.type, Scope.SINGLETON))

    @classmethod
    def create(cls, *modules: AbstractModule) -> 'MappingStore':
        store = cls()
        store._load_modules(*modules)
        return store
