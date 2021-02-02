import pytest

from simio_di import DependenciesContainer, DependencyInjector


@pytest.fixture
def injector_fabric():
    def _fabric(cfg):
        container = DependenciesContainer()
        return DependencyInjector(cfg, deps_container=container)

    return _fabric
