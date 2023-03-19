import jwt
import asyncio
import aiozmq.rpc
from datetime import datetime, timedelta, timezone
import sys


if sys.version_info >= (3, 8) and sys.platform.lower().startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class JWTService(aiozmq.rpc.AttrHandler):

    def __init__(self, secret: str, algorithm: str = "HS256"):
        self.secret = secret
        self.algorithm = algorithm

    @aiozmq.rpc.method
    def get_token(self, username: str) -> str:
        data = {
            "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
            "username": username
        }
        return jwt.encode(data, self.secret, algorithm=self.algorithm)

    @aiozmq.rpc.method
    def verify_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                    token, self.secret, algorithms=[self.algorithm])
        except jwt.exceptions.InvalidSignatureError:
            return {"error": "Invalid token"}
        except jwt.ExpiredSignatureError:
            return {"error": "Token expired"}


async def serve():
    service = JWTService('swordfish')
    server = await aiozmq.rpc.serve_rpc(
        service, bind='tcp://127.0.0.1:5555')
    await server.wait_closed()


asyncio.run(serve())