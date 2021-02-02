# Simio
[![Build Status](https://travis-ci.com/RB387/simio-di.svg?branch=main)](https://travis-ci.com/RB387/simio-di)  

Small and simple dependency injector. Made for framework [Simio](https://github.com/RB387/Simio).

* Supports `Providers`, `Variables`, `Dependencies`
* Works with async functions
* Friendly with mypy
* Does not steal constructor and doesn't change injected object
* Supports Singletone injections or new instances on every injection
* Easy to use


## Examples

So for example let's look at this code

```python
import asyncio
from dataclasses import dataclass
from simio_di import Depends, Var, DependencyInjector, DependenciesContainer


@dataclass
class MongoClient:
    mongo_dsn: str


@dataclass
class Worker:
    mongo: Depends[MongoClient]
    env_type: Var['env']


async def start_worker(worker: Worker, env: Var['env']):
    # do some work
    ...

# To make it work all you need to do is:
config = {
    MongoClient: {'mongo_dsn': 'localhost:27017'},
    'env': 'dev',
}
di = DependencyInjector(config, deps_container=DependenciesContainer())
asyncio.run(di.inject(start_worker))
```
But what if we wanna use interfaces instead of realization? Use providers!

```python
import asyncio
from dataclasses import dataclass
from typing import Protocol
from simio_di import Provide, Depends, Var, DependencyInjector, DependenciesContainer


@dataclass
class UserDaoProtocol(Protocol):
    async def get_user_info(self): ...
    async def update_user_info(self): ...


async def user_page_handler(user_dao: Provide[UserDaoProtocol]):
    # do some work
    ...

# Now lets make realization of protocol
@dataclass
class MongoClient:
    mongo_dsn: Var['mongo_dsn']


@dataclass
class MongoUserDao:
    mongo: Depends[MongoClient]

    async def get_user_info(self): ...
    async def update_user_info(self): ...


# Now lets make it work
config = {
    # Provider bindings
    UserDaoProtocol: MongoUserDao,
    # Variables
    'mongo_dsn': 'localhost:27017',
}
di = DependencyInjector(config, deps_container=DependenciesContainer())
injected_handler = di.inject(user_page_handler)
asyncio.run(injected_handler)
```

If you need your clients as singletone, use `SingletoneDependenciesContainer`
```python
from simio_di import DependencyInjector, SingletoneDependenciesContainer

config = {
    # some config
}
di = DependencyInjector(config, deps_container=SingletoneDependenciesContainer())
di.inject(something)
```


## Testing
DI does not change object that's being injected, so you can use deps in test like this:
```python
async def user_page_handler(user_dao: Provide[UserDaoProtocol]):
    ...

async def test_user_page_handler():
    result = await user_page_handler(user_dao=Mock())
```