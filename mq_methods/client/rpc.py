import asyncio
import uuid
from abc import abstractmethod
from typing import Optional

import aiormq

from mq_methods.mq_methods.logger import client_logger
from .base import BaseClient


class Rpc(BaseClient):
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
        declare_ok = await self.channel.queue_declare(exclusive=True, auto_delete=True)
        await self.channel.basic_consume(declare_ok.queue, self.on_response)
        self.callback_queue: str = declare_ok.queue

    async def on_response(self, message: aiormq.abc.DeliveredMessage):
        future = self.futures.pop(message.header.properties.correlation_id)
        future.set_result(message.body)

    async def _process(self, payload: bytes) -> bytes:
        await self._connect()
        correlation_id = str(uuid.uuid4())

        client_logger.debug(f'Correlation ID: {correlation_id}')
        client_logger.debug(f'Queue name: {self.queue_name}')

        future = self.loop.create_future()
        self.futures[correlation_id] = future
        await self.channel.basic_publish(
            payload,
            routing_key=self.queue_name,
            timeout=self.timeout,
            properties=aiormq.spec.Basic.Properties(
                correlation_id=correlation_id,
                reply_to=self.callback_queue,
            )
        )
        response = await future
        client_logger.debug(f'Received response: {response}')
        return response
