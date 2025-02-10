import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from project.constant.status_constant import FAIL
import ast
import json

class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = 'SECRET'

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            return False
    

    def datetime_handler(self,x):
        if isinstance(x, datetime):
            return x.isoformat()
        return x #TypeError("Type not serializable")
    
    def encode_token(self, user_dict):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=60),
            'iat': datetime.utcnow(),
            'sub': json.dumps(user_dict,default=self.datetime_handler)
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm='HS256'
        )
    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            return json.loads(payload['sub'], )
            
        except jwt.ExpiredSignatureError:
            response = {}
            response.update(status=FAIL, message="Signature has expired", error=[], data={})
            raise HTTPException(status_code=401, detail=response)
        except jwt.InvalidTokenError as e:
            print(e)
            response = {}
            response.update(status=FAIL, message="Invalid token", error=[], data={})
            raise HTTPException(status_code=401, detail=response)

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)
