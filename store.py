import peewee
import typing as t
from peewee_aio import Manager
from zero import ZeroServer


manager = Manager('aiosqlite:///app.db')


class User(manager.Model):
    username = peewee.CharField(primary_key=True)
    password  = peewee.CharField()


class AccountService:

    def __init__(self, manager: Manager):
        self.manager = manager

    async def create(self, data: dict) -> bool:
        async with self.manager:
            async with self.manager.connection():
                await User.create_table(True)
                test = await User.create(**data)
        return True

    async def get(self, username: str) -> dict:
        async with manager:
            async with manager.connection():
                user = await User.get_by_id(username)
        return {'username': user.username}


if __name__ == "__main__":
    app = ZeroServer(port=6000)
    service = AccountService(manager)
    app.register_rpc(service.create)
    app.register_rpc(service.get)
    app.run()
