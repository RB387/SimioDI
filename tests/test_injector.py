from dataclasses import dataclass
from unittest.mock import Mock
from typing import Type, Optional

import pytest

from simio_di import Var, Provide, InjectionError

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol


def test_fail_inject(injector_fabric):
    class ClientProtocol(Protocol):
        ...

    @dataclass
    class TestClient:
        my_var: Var["my_var"]
        one_more: str

    def use_client(client: Provide[ClientProtocol]):
        ...

    config = {"my_var": 1, ClientProtocol: TestClient}
    with pytest.raises(InjectionError):
        injector_fabric(config).inject(use_client)


def test_fail_var_inject(injector_fabric):
    class ClientProtocol(Protocol):
        ...

    @dataclass
    class TestClient:
        my_var: Var["my_var"]

    def use_client(client: Provide[ClientProtocol]):
        ...

    config = {ClientProtocol: TestClient}
    with pytest.raises(InjectionError):
        injector_fabric(config).inject(use_client)


def test_fail_provider_inject(injector_fabric):
    class ClientProtocol(Protocol):
        ...

    def use_client(client: Provide[ClientProtocol]):
        ...

    config = {}
    with pytest.raises(InjectionError):
        injector_fabric(config).inject(use_client)


def test_success_inject(injector_fabric):
    class ClientOneProtocol(Protocol):
        some_str: str

    class SomeEntityProtocol(Protocol):
        ...

    class Empty:
        ...

    @dataclass
    class Something:
        some_str: str
        my_var: Var["my_var"]

    class ClientTwoProtocol(Protocol):
        ...

    @dataclass
    class TestClient(ClientTwoProtocol):
        my_var: Var["my_var"]
        some_cls: Provide[Type[SomeEntityProtocol]]
        client_one: Provide[ClientOneProtocol]

    @dataclass
    class UserOfClient:
        client_two: Provide[ClientTwoProtocol]

    config = {
        # clients init
        Something: {"some_str": "123"},
        # provider bindings
        ClientOneProtocol: Something,
        ClientTwoProtocol: TestClient,
        SomeEntityProtocol: Empty,
        # vars
        "my_var": "some text",
    }

    injected_client: UserOfClient = injector_fabric(config).inject(UserOfClient)()
    assert isinstance(injected_client.client_two, TestClient)

    assert injected_client.client_two.my_var == "some text"
    assert injected_client.client_two.some_cls is Empty
    assert isinstance(injected_client.client_two.client_one, Something)
    assert injected_client.client_two.client_one.my_var == "some text"
    assert injected_client.client_two.client_one.some_str == "123"


def test_lazy_inject(injector_fabric):
    class ClientOneProtocol(Protocol):
        ...

    class ClientOne:
        ...

    default_value = 1

    def use_client(client: Provide[ClientOneProtocol] = default_value):
        return client

    injector = injector_fabric({ClientOneProtocol: ClientOne})
    injected = injector.lazy_inject(use_client)

    assert injected() is default_value

    injector.do_lazy_injections()
    assert type(injected()) is ClientOne


def test_add_config(injector_fabric):
    config = {
        "key_one": {"embedded": "3", "one_more": "5",},
        "key_two": "4",
        "key_three": "5",
    }

    injector = injector_fabric(config)
    injector.add_config(
        {"key_two": "10", "key_one": {"embedded": "10", "new_key": "123",},}
    )

    assert injector.deps_cfg == {
        "key_one": {"embedded": "10", "new_key": "123", "one_more": "5",},
        "key_two": "10",
        "key_three": "5",
    }
