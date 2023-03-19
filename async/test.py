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

    loop = asyncio.get_event_loop()
    client = await aiozmq.rpc.connect_rpc(connect='tcp://127.0.0.1:5556')
    await asyncio.gather(*[
        client.call.create({
            "email": f"test{idx}@test.com",
            "password": "toto"
        }) for idx in range(10)
    ])
    #userid = await client.call.create()
    #ret = await client.call.get(userid)
    #print(ret)
    client.close()


asyncio.run(go()
)
