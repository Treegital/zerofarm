import peewee
import asyncio
import time
from aiozmq import rpc
from models import manager, Account, Certificate, AccountStatus


class AccountService(rpc.AttrHandler):

    def __init__(self, manager):
        self.manager = manager

    @rpc.method
    async def create_account(self, data: dict) -> bool:
        await asyncio.sleep(3)
        async with self.manager:
            async with self.manager.connection():
                item = await Account.create(**data)
        return item.id

    @rpc.method
    async def request_account_token(self, id: str) -> dict:
        async with self.manager:
            async with self.manager.connection():
                item = await Account.get_by_id(id)
        return {'email': item.email}

    @rpc.method
    async def verify_account(self, email: str, token: str) -> dict:
        async with self.manager:
            async with self.manager.connection():
                account = await models.Account.get(
                    email=item['email'],
                    status=models.AccountStatus.pending
                )
        if account is None:
            return {'err': 'Invalid token'}

        if not account.totp.verify(token):
            return {'err': 'Invalid token'}

        account.status = models.AccountStatus.active
        await account.save()
        return True

    @rpc.method
    async def verify_credentials(self, username: str, password: str) -> dict:
        async with self.manager:
            async with self.manager.connection():
                item = await Account.get_by_id(id)
        return {'email': item.email}

    @rpc.method
    async def get_account(self, id: str) -> dict:
        async with self.manager:
            async with self.manager.connection():
                item = await Account.get_by_id(id)
        return {'email': item.email}


async def serve():
    async with manager:
        async with manager.connection():
            await Account.create_table()
            await Certificate.create_table()

    service = AccountService(manager)
    server = await rpc.serve_rpc(
        service, bind='tcp://127.0.0.1:5556')
    await server.wait_closed()


asyncio.run(serve())
