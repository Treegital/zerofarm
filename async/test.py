import aiozmq.rpc
import sys, asyncio


if sys.version_info >= (3, 8) and sys.platform.lower().startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def go():
    client = await aiozmq.rpc.connect_rpc(connect='tcp://127.0.0.1:5555')
    token = await client.call.get_token("test")
    ret = await client.call.verify_token(token)
    print(ret)

    client.close()


asyncio.run(go())