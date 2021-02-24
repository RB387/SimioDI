from dataclasses import dataclass
from typing import TypeVar, Type, cast, get_type_hints, Dict, Any, Callable

from simio_di.containers import DependenciesContainerProtocol

T = TypeVar("T")


@dataclass
class Dependency:
    dependency: Type[T]


@dataclass
class Provider:
    provider: Type[T]


@dataclass
class Variable:
    var: str


class _Depends:
    # Need to create instance, because
    # with __class_getitem__ type hinting
    # in PyCharm doesn't work for some reason
    def __getitem__(self, item: Type[T]) -> Type[T]:
        dependency = Dependency(item)
        # So actually it's not Type[T], we still return Dependency instance
        # But for type hints it is, because we will inject it later
        return cast(Type[T], dependency)


class _Provide:
    def __getitem__(self, item: Type[T]) -> Type[T]:
        provider = Provider(item)
        return cast(Type[T], provider)


class _Var:
    def __getitem__(self, item: str) -> Any:
        return Variable(item)


Depends = _Depends()
Provide = _Provide()
Var = _Var()


class InjectionError(Exception):
    ...


class DependencyInjector:
    """
        Injects dependencies. Uses deps_cfg for deps initialization(which is basically is container)
        Dependencies can be marked in type hint as `deps: Depends[A]`
        If you use interfaces, you can use Providers: `provided: Provide[B]` a then bind it in cfg
        Also, you can use variables that can be anything: `my_var: Var['some_var']`
    """

    def __init__(
        self, deps_cfg: Dict[Any, Any], deps_container: DependenciesContainerProtocol
    ):
        self._deps_cfg: Dict[Any, Any] = deps_cfg
        self._deps_container: DependenciesContainerProtocol = deps_container

    def inject(self, obj: Type[T]) -> Callable[[], T]:
        """ Idempotent operation """
        injected = self._deps_container.get(obj)

        if injected is not None:
            return injected

        try:
            return self._inject(obj)
        except TypeError as e:
            raise InjectionError(f"Failed to inject {obj}: {e}")

    def _inject(self, obj: Type[T]) -> Callable[[], T]:
        type_hints = get_type_hints(obj)
        kwargs = self._deps_cfg.get(obj, {})

        for name, cls in type_hints.items():
            if isinstance(cls, Dependency):
                # If all deps are injected then it will be okay
                # Other wise will raise exception (You should add more deps to config)
                kwargs[name] = self.inject(cls.dependency)()
            elif isinstance(cls, Provider):
                provided_obj = self._deps_cfg.get(cls.provider)

                if provided_obj is None:
                    raise InjectionError(
                        f"Provided value for {cls.provider} is not configured"
                    )

                kwargs[name] = self.inject(provided_obj)()
            elif isinstance(cls, Variable):
                try:
                    # Exception instead of get, because None value in vars is legit
                    var_value = self._deps_cfg[cls.var]
                except KeyError:
                    raise InjectionError(f"Value for variable {cls.var} is not defined")

                kwargs[name] = var_value

        self._deps_container.set(obj, **kwargs)
        return self._deps_container.get(obj)
