# Pyject
Pyject is a dependency injection framework for Python 3 inspired by Guice.

# Sample usage

```python
from pyject import PyJect


class Logger:

    def __init__(self):
        self.name = "MyLogger"

    def info(self, msg: str) -> None:
        print(f"{self.name} :: " + msg)


class Dao:

    def __init__(self, logger: Logger):
        self.logger = logger
        self.users = list()

    def add_user(self, user: str) -> None:
        self.users.append(user)
        self.logger.info(f"Added user {user}")


class StartupService:

    def __init__(self, dao: Dao):
        self.dao = dao

    def run(self):
        self.dao.add_user("John")
        self.dao.add_user("Anne")


if __name__ == "__main__":
    injector = PyJect.create_injector()
    startup = injector.get_instance(StartupService)
    startup.run()
```

# Advanced usage

In this example we bind an abstract class to a different implementation
depending on an environment variable.

This is done in the `AbstractModule` implementation.

```python
import os
from abc import abstractmethod

from pyject import PyJect, AbstractModule


class Logger:

    @abstractmethod
    def info(self, msg: str) -> None:
        ...


class LoggerSimple(Logger):

    def __init__(self):
        self.name = "MyLoggerSimple"

    def info(self, msg: str) -> None:
        print(f"{self.name} :: " + msg)


class LoggerVerbose(Logger):

    def __init__(self):
        self.name = "MyLoggerVerbose"

    def info(self, msg: str) -> None:
        print(f"{self.name} :: " + msg)


class Dao:

    def __init__(self, logger: Logger):
        self.logger = logger
        self.users = list()

    def add_user(self, user: str) -> None:
        self.users.append(user)
        self.logger.info(f"Added user {user}")


class StartupService:

    def __init__(self, dao: Dao):
        self.dao = dao

    def run(self):
        self.dao.add_user("John")
        self.dao.add_user("Anne")


class MyModule(AbstractModule):

    def configure(self) -> None:
        if os.environ.get("MY_LOGGER") == "Verbose":
            self.bind(Logger, to=LoggerVerbose)
        else:
            self.bind(Logger, to=LoggerSimple)


if __name__ == "__main__":
    injector = PyJect.create_injector(
        MyModule()
    )
    startup = injector.get_instance(StartupService)
    startup.run()
```

