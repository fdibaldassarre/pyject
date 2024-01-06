import inspect
from typing import Type, Dict, Callable, Union, Optional


def get_type_annotations(f: Union[Type, Callable]) -> Dict[str, Type]:
    arguments = {}
    if not hasattr(f, "__annotations__"):
        return arguments
    for key, key_type in f.__annotations__.items():
        if key != "return":
            arguments[key] = key_type
    return arguments


def get_return_type(f: Callable) -> Optional[Type]:
    for key, key_type in f.__annotations__.items():
        if key == "return":
            return key_type
    return None


def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }