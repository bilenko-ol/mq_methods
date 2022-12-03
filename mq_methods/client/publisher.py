import asyncio
from abc import abstractmethod
from typing import Optional

import aiormq

from .base import BaseClient


class Publisher(BaseClient):
    def __init__(
            self,
            connection_url: str,
            timeout: int,
            loop: Optional[asyncio.AbstractEventLoop] = None
    ):
        self.connection_url: str = connection_url
        self.timeout: int = timeout
        if loop:
            self.loop: asyncio.AbstractEventLoop = loop
        else:
            self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

        self.futures: dict = {}
        self.channel: Optional[aiormq.abc.AbstractChannel] = None

    @property
    @abstractmethod
    def queue_name(self) -> str:
        raise NotImplementedError

    async def _connect(self):
        self.connection: aiormq.abc.AbstractConnection = await aiormq.connect(self.connection_url)
        self.channel: aiormq.abc.AbstractChannel = await self.connection.channel()
        await self.channel.exchange_declare(
            exchange=self.queue_name, exchange_type='fanout'
        )

    async def _process(self, payload: bytes, routing_key: str) -> None:
        await self._connect()
        await self.channel.basic_publish(
            payload, routing_key=routing_key, exchange=self.queue_name, properties=aiormq.spec.Basic.Properties(
                delivery_mode=1,
            )
        )
        await self.connection.close()
