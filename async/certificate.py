import asyncio
import uuid
import logging
from typing import MutableMapping
from aio_pika import Message, connect
from aio_pika.abc import (
    AbstractChannel, AbstractConnection, AbstractIncomingMessage, AbstractQueue,
)


async def main() -> None:

    # Perform connection
    connection = await connect("amqp://guest:guest@localhost/")

    # Creating a channel
    channel = await connection.channel()
    exchange = channel.default_exchange

    # Declaring queue
    queue = await channel.declare_queue("rpc_queue")

    print(" [x] Awaiting RPC requests")

    # Start listening the queue with name 'hello'
    async with queue.iterator() as qiterator:
        message: AbstractIncomingMessage
        async for message in qiterator:
            try:
                async with message.process(requeue=False):
                    assert message.reply_to is not None
                    n = int(message.body.decode())
                    response = str(fib(n)).encode()
                    await exchange.publish(
                        Message(
                            body=response,
                            correlation_id=message.correlation_id,
                        ),
                        routing_key=message.reply_to,
                    )
                    print("Request complete")

            except Exception:
                logging.exception("Processing error for message %r", message)


class PKI:
    connection: AbstractConnection
    channel: AbstractChannel
    callback_queue: AbstractQueue
    loop: asyncio.AbstractEventLoop

    def __init__(self) -> None:
        self.futures: MutableMapping[str, asyncio.Future] = {}
        self.loop = asyncio.get_running_loop()

    async def connect(self) -> "PKI":
        self.connection = await connect(
            "amqp://guest:guest@localhost/", loop=self.loop,
        )
        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(exclusive=True)
        await self.callback_queue.consume(self.on_response, no_ack=True)
        return self

    def on_response(self, message: AbstractIncomingMessage) -> None:
        if message.correlation_id is None:
            print(f"Bad message {message!r}")
            return

        future: asyncio.Future = self.futures.pop(message.correlation_id)
        future.set_result(message.body)

    async def call(self, n: int) -> int:
        correlation_id = str(uuid.uuid4())
        future = self.loop.create_future()
        self.futures[correlation_id] = future

        await self.channel.default_exchange.publish(
            Message(
                str(n).encode(),
                content_type="text/plain",
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key="rpc_queue",
        )

        return int(await future)


async def main() -> None:
    fibonacci_rpc = await FibonacciRpcClient().connect()
    print(" [x] Requesting fib(30)")
    response = await fibonacci_rpc.call(30)
    print(f" [.] Got {response!r}")



if __name__ == "__main__":

    asyncio.run(main())