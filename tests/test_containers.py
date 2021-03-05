import pytest

from simio_di import DependenciesContainer, SingletoneDependenciesContainer


@pytest.mark.parametrize(
    "container_type, expected_is_same_instance",
    ((DependenciesContainer, False), (SingletoneDependenciesContainer, True),),
)
def test_dependencies_containers(container_type, expected_is_same_instance):
    container = container_type()

    class TestClient:
        def __init__(self, flag: bool):
            self.flag = flag

    container.set(TestClient, flag=True)

    client_one = container.get(TestClient)()
    assert isinstance(client_one, TestClient)

    client_two = container.get(TestClient)()
    assert isinstance(client_two, TestClient)

    is_same_instance = client_one is client_two
    assert is_same_instance == expected_is_same_instance

    iterated_types = []

    for obj_type, injected in container:
        assert isinstance(injected(), obj_type)
        iterated_types.append(obj_type)

    assert iterated_types == [TestClient]
