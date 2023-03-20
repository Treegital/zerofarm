import jwt
import asyncio
import aiozmq.rpc
from minicli import run, cli
from datetime import datetime, timedelta, timezone


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


@cli
async def serve(host: str = "127.0.0.1", port: int = 5555):
    service = JWTService('swordfish')
    server = await rpc.serve_rpc(service, bind=f'tcp://{host}:{port}')
    await server.wait_closed()


if __name__ == '__main__':
    run()
