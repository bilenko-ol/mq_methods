# MQ methods

-----

## RPC

### Worker

```python
from mq_methods import worker


class TestRpcWorker(worker.Rpc):
    connection_url: str = 'amqp://root:example@rabbit:5672/'
    queue_name: str = 'test_rpc_queue_name'

    async def process(self, payload: bytes) -> bytes:
        ...

```

### Client

```python
from mq_methods.client import Rpc
import json

TIMEOUT = 5


class TestRpcClient(Rpc):
    queue_name: str = 'test_rpc_queue_name'

    async def process(self, payload: dict) -> dict:
        payload: bytes = json.dumps(payload).encode()
        result: bytes = await self._process(payload)
        result: dict = json.loads(result.decode())
        return result


if __name__ == '__main__':
    client = TestRpcClient('amqp://root:example@rabbit:5672/', TIMEOUT)

    client.process({
        'id': 1,
        'name': 'Test Publisher'
    })
```

-----

## Publisher/Consumer

### Worker

```python
from mq_methods import worker


class TestSubscriberWorker(worker.Subscriber):
    connection_url: str = 'amqp://root:example@rabbit:5672/'
    queue_name: str = 'test_subscriber_queue_name'

    async def process(self, payload: bytes, routing_key: str):
        ...
```

### Client

```python
from mq_methods.client import Publisher
import json

TIMEOUT = 5


class TestPublisherClient(Publisher):
    queue_name: str = 'test_subscriber_queue_name'

    async def process(self, payload: dict, routing_key: str):
        payload: bytes = json.dumps(payload).encode()
        await self._process(payload, routing_key)


if __name__ == '__main__':
    client = TestPublisherClient('amqp://root:example@rabbit:5672/', TIMEOUT)

    client.process({
        'id': 1,
        'name': 'Test Publisher'
    }, 'test_subscriber_routing_key')
```