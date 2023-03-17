import zmq
import json
import ormsgpack
from zero import ZeroClient
from minicli import cli, run
from zmq_tubes.threads import Tube, TubeNode


@cli
def jwt():
    req_tube = Tube(
        name='REQ',
        addr='tcp://127.0.0.1:5559',
        tube_type=zmq.REQ
    )
    node = TubeNode()
    node.register_tube(req_tube, "jwt/#")
    with node:
        result = node.request(
            'jwt/get', payload=json.dumps({'username': 'test'}))
        token = json.loads(result.payload)
        result = node.request(
            'jwt/verify', payload=json.dumps({'token': token['token']}))
    print(json.loads(result.payload))


@cli
def user():
    client = ZeroClient("localhost", 6000)
    print(client.call('create', {
        'username': 'toto', 'password': 'whatever'
    }))
    print(client.call('get', 'toto'))


if __name__ == '__main__':
    run()
