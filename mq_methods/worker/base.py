from abc import ABC, abstractmethod


class BaseWorker(ABC):
    @property
    @abstractmethod
    def connection_url(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def consuming(self):
        raise NotImplementedError

    @abstractmethod
    async def connect(self):
        raise NotImplementedError
