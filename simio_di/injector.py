from dataclasses import dataclass
from functools import wraps
from typing import (
    TypeVar,
    Type,
    cast,
    get_type_hints,
    Dict,
    Any,
    Hashable,
    Callable,
    List,
)

from more_itertools import one

from simio_di.utils import deep_merge_dicts

try:
    from typing import get_origin, get_args
except ImportError:
    from simio_di.utils import get_origin, get_args

from simio_di.containers import DependenciesContainerProtocol

T = TypeVar("T")


@dataclass
class Provider:
    provider: Type[T]


@dataclass
class Variable:
    var: Hashable


class _Provide:
    def __getitem__(self, item: Type[T]) -> Type[T]:
        # So actually it's not Type[T], we still return Dependency instance
        # But for type hints it is, because we will inject it later
        provider = Provider(item)
        return cast(Type[T], provider)


class _Var:
    def __getitem__(self, item: str) -> Any:
        return Variable(item)


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
        self.deps: DependenciesContainerProtocol = deps_container
        self.deps_cfg: Dict[Any, Any] = deps_cfg
        self.postponed: List[Callable[[], Any]] = []

    def inject(self, obj: Type[T]) -> Callable[[], T]:
        """ Idempotent operation """
        obj = get_origin(obj) or obj
        injected = self.deps.get(obj)

        if injected is not None:
            return injected

        try:
            return self._inject(obj)
        except TypeError as e:
            raise InjectionError(f"Failed to inject {obj}: {e}")

    def lazy_inject(self, obj: Type[T]) -> Type[T]:
        injected = obj

        @wraps(obj)
        def wrapper(*args, **kwargs):
            return injected(*args, **kwargs)

        def _inject():
            nonlocal injected
            injected = self.inject(obj)

        self.postponed.append(_inject)
        return wrapper

    def do_lazy_injections(self):
        while self.postponed:
            self.postponed.pop()()

    def add_config(self, deps_cfg: Dict[Any, Any]):
        deep_merge_dicts(self.deps_cfg, deps_cfg)

    def _inject(self, obj: Type[T]) -> Callable[[], T]:
        type_hints = get_type_hints(obj)
        kwargs = self.deps_cfg.get(obj, {})

        for name, cls in type_hints.items():
            if isinstance(cls, Provider):
                if get_origin(cls.provider) is type:
                    type_hint = one(get_args(cls.provider))
                    provided_obj = self.deps_cfg.get(type_hint)

                    if provided_obj is None:
                        raise InjectionError(
                            f"Provided value for {cls.provider} is not configured"
                        )

                    kwargs[name] = provided_obj
                else:
                    provider = get_origin(cls.provider) or cls.provider
                    provided_obj = self.deps_cfg.get(provider)

                    if provided_obj is None:
                        raise InjectionError(
                            f"Provided value for {provider} is not configured"
                        )

                    # If all deps are injected then it will be okay
                    # Other wise will raise exception (You should add more deps to config)
                    kwargs[name] = self.inject(provided_obj)()
            elif isinstance(cls, Variable):
                try:
                    # Exception instead of get, because None value in vars is legit
                    var_value = self.deps_cfg[cls.var]
                except KeyError:
                    raise InjectionError(f"Value for variable {cls.var} is not defined")

                kwargs[name] = var_value

        self.deps.set(obj, **kwargs)
        return self.deps.get(obj)
