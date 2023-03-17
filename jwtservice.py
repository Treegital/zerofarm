import zmq
import jwt
import json
import ormsgpack
from datetime import datetime, timedelta, timezone
from zmq_tubes.threads import Tube, TubeNode, TubeMessage


class JWTService:

    def __init__(self, secret: str, algorithm: str = "HS256"):
        self.secret = secret
        self.algorithm = algorithm

    def get_token(self, request: TubeMessage) -> str:
        try:
            payload = json.loads(request.payload)
            data = {
                "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
                "username": payload['username']
            }
            token = jwt.encode(data, self.secret, algorithm=self.algorithm)
            return request.create_response(json.dumps({'token': token}))
        except Exception as err:
            import pdb
            pdb.set_trace()
            pass

    def verify_token(self, request: TubeMessage) -> dict:
        payload = json.loads(request.payload)
        token = payload['token']
        try:
            data = jwt.decode(
                token, self.secret, algorithms=[self.algorithm])
            return request.create_response(json.dumps(data))
        except jwt.exceptions.InvalidSignatureError:
            return {"error": "Invalid token"}
        except jwt.ExpiredSignatureError:
            return {"error": "Token expired"}



if __name__ == "__main__":
    service = JWTService("swordfish")
    resp_tube = Tube(
        name='JWTService',
        addr='tcp://127.0.0.1:5559',
        server=True,
        tube_type="REP"
    )
    node = TubeNode()
    node.register_tube(resp_tube, "jwt/#")
    node.register_handler("jwt/get", service.get_token)
    node.register_handler("jwt/verify", service.verify_token)
    server = node.start()
    server.join()
