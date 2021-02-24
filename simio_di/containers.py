from functools import partial, wraps
from inspect import isfunction
from typing import Type, Any, Optional, Callable, TypeVar

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol

T = TypeVar("T")


class DependenciesContainerProtocol(Protocol):
    def set(self, obj: Type[T], **obj_kwargs: Any):
        ...

    def get(self, obj: Type[T]) -> Optional[Callable[[], T]]:
        ...


class DependenciesContainer:
    def __init__(self):
        self._deps = {}

    def set(self, obj: Type[T], **obj_kwargs: Any):
        self._deps[obj] = wraps(obj)(partial(obj, **obj_kwargs))

    def get(self, obj: Type[T]) -> Optional[Callable[[], T]]:
        dependency = self._deps.get(obj)

        if dependency is not None:
            return dependency

        return None


class SingletoneDependenciesContainer:
    def __init__(self):
        self._deps = {}

    def set(self, obj: Type[T], **obj_kwargs):
        if isfunction(obj):
            self._deps[obj] = wraps(obj)(partial(obj, **obj_kwargs))
        else:
            self._deps[obj] = obj(**obj_kwargs)

    def get(self, obj: Type[T]) -> Optional[Callable[[], T]]:
        dependency = self._deps.get(obj)

        if dependency is not None:
            if isfunction(obj):
                return dependency

            return lambda: dependency

        return None
