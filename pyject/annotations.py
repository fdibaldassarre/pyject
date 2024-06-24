import functools
from typing import Type, Callable, TypeVar, Tuple, Any, Optional, Dict, Generic

T = TypeVar("T")


class PyjectConstructor:

    def __init__(self, method: Callable, name: Optional[str] = None):
        self.method = method
        self.__instance_name__ = name

    def __getattr__(self, attr):
        return getattr(self.method, attr)

    def set_name(self, name: str) -> None:
        self.__instance_name__ = name

    def __call__(self, *args, **kwargs):
        return self.method(None, *args, **kwargs)


def Named(name: str) -> Callable[[...], Any]:
    def decorator(method):
        if isinstance(method, PyjectConstructor):
            method.set_name(name)
            return method
        else:
            return PyjectConstructor(method, name=name)
    return decorator


class Provider(Generic[T]):

    def get(self, name: Optional[str]) -> T:
        raise NotImplementedError()
