from dataclasses import dataclass
from unittest.mock import Mock

import pytest

from simio_di import Var, Provide, Depends, InjectionError

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol


def test_fail_inject(injector_fabric):
    @dataclass
    class TestClient:
        my_var: Var["my_var"]
        one_more: str

    def use_client(client: Depends[TestClient]):
        ...

    config = {"my_var": 1}
    with pytest.raises(InjectionError):
        injector_fabric(config).inject(use_client)


def test_fail_var_inject(injector_fabric):
    @dataclass
    class TestClient:
        my_var: Var["my_var"]

    def use_client(client: Depends[TestClient]):
        ...

    config = {}
    with pytest.raises(InjectionError):
        injector_fabric(config).inject(use_client)


def test_fail_provider_inject(injector_fabric):
    @dataclass
    class TestClient:
        provider: Provide[Mock]

    def use_client(client: Depends[TestClient]):
        ...

    config = {}
    with pytest.raises(InjectionError):
        injector_fabric(config).inject(use_client)


def test_success_inject(injector_fabric):
    class ClientProtocol(Protocol):
        some_str: str

    @dataclass
    class Something:
        some_str: str
        my_var: Var["my_var"]

    @dataclass
    class TestClient:
        my_var: Var["my_var"]
        client: Provide[ClientProtocol]

    @dataclass
    class UserOfClient:
        client: Depends[TestClient]

    config = {
        # clients init
        Something: {"some_str": "123"},
        # provider bindings
        ClientProtocol: Something,
        # vars
        "my_var": "some text",
    }

    injected_client: UserOfClient = injector_fabric(config).inject(UserOfClient)()
    assert isinstance(injected_client.client, TestClient)

    assert injected_client.client.my_var == "some text"
    assert isinstance(injected_client.client.client, Something)
    assert injected_client.client.client.my_var == "some text"
    assert injected_client.client.client.some_str == "123"
