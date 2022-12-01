import asyncio
from abc import abstractmethod
from typing import Optional

import aiormq
import nest_asyncio

from mq_methods.logger import worker_logger
from .base import BaseWorker


class Rpc(BaseWorker):
    @property
    @abstractmethod
    def queue_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def process(self, payload: bytes) -> bytes:
        raise NotImplementedError

    def __init__(self):
        self.response: Optional[bytes] = None

    async def consuming(self):
        worker_logger.debug('Consuming worker: Rpc')
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        loop.create_task(self.connect())
        loop.run_forever()

    async def connect(self):
        connection = await aiormq.connect(self.connection_url)
        channel = await connection.channel()
        worker_logger.debug(f'Queue declare: {self.queue_name}')
        declare_ok = await channel.queue_declare(self.queue_name)
        await channel.basic_consume(declare_ok.queue, self.on_message)

    async def on_message(self, message: aiormq.abc.DeliveredMessage):
        worker_logger.debug(f'Received message: {message.body}')
        try:
            self.response = await self.process(message.body)
        except Exception as e:
            worker_logger.error(e)
            raise e
        worker_logger.debug(f'Send response: {self.response}')
        await message.channel.basic_publish(
            self.response, routing_key=message.header.properties.reply_to,
            properties=aiormq.spec.Basic.Properties(
                correlation_id=message.header.properties.correlation_id
            ),
        )
        await message.channel.basic_ack(message.delivery.delivery_tag)
