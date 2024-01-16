import functools
from typing import Type, Callable, TypeVar, Tuple, Any, Optional, Dict


class PyjectConstructor:

    def __init__(self, method: Callable, name: Optional[str] = None, named_args: Optional[Dict[str, str]] = None):
        self.method = method
        self.__instance_name__ = name
        self.__named_args__ = named_args

    def __getattr__(self, attr):
        return getattr(self.method, attr)

    def set_name(self, name: str) -> None:
        self.__instance_name__ = name

    def set_instance_names(self, named_args: Dict[str, str]):
        self.__named_args__ = named_args

    def __call__(self, *args, **kwargs):
        return self.method(None, *args, **kwargs)


def NamedParams(**kwargs) -> Callable[[...], Any]:
    def decorator(method):
        if isinstance(method, PyjectConstructor):
            method.set_instance_names(kwargs)
            return method
        else:
            return PyjectConstructor(method, name=None, named_args=kwargs)
    return decorator


def Named(name: str) -> Callable[[...], Any]:
    def decorator(method):
        if isinstance(method, PyjectConstructor):
            method.set_name(name)
            return method
        else:
            return PyjectConstructor(method, name=name)
    return decorator
