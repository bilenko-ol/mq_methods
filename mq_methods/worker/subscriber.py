import asyncio
from abc import abstractmethod

import aiormq
import nest_asyncio

from mq_methods.logger import worker_logger
from .base import BaseWorker


class Subscriber(BaseWorker):
    @property
    @abstractmethod
    def queue_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def process(self, payload: bytes, routing_key: str):
        raise NotImplementedError

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
        await channel.exchange_declare(
            exchange=self.queue_name, exchange_type='fanout'
        )
        declare_ok = await channel.queue_declare(exclusive=True)
        await channel.queue_bind(declare_ok.queue, self.queue_name)
        await channel.basic_consume(declare_ok.queue, self.on_message)

    async def on_message(self, message: aiormq.abc.DeliveredMessage):
        worker_logger.debug(f'Received message: {message.body}')
        worker_logger.debug(f'Received routing_key: {message.routing_key}')
        try:
            await self.process(message.body, message.routing_key)
        except Exception as e:
            worker_logger.error(e)
            raise e
        await message.channel.basic_ack(message.delivery.delivery_tag)
