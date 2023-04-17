#from register import * 
import register as rg
import db_conn as db
from passlib.context import CryptContext
from pydantic import BaseModel
import datetime as dt
from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
import hashlib as hs
import sqlalchemy.orm as orm
import logging



SECRET_KEY = "bac3f2844dc2c5647f569d295a32c73cfb1c050b5f3f7adc0f803b6375c645bf"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}, )

class Token(BaseModel):
    access_token: str
    token_type: str
    
    
class TokenData(BaseModel):
    username: str | None = None


def create_access_token(data: dict, expires_delta: dt.timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = dt.datetime.utcnow() + expires_delta
    else:
        expire = dt.datetime.utcnow() + dt.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    username = to_encode.get("sub")
    logging.info(msg="jwt created", extra={"user": username})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(login: str, password: str, session: orm.Session = Depends(db.get_db)) -> rg.UserDB:
    user = session.get(rg.UserDB,login) 
    if not user:
        logging.info(msg="Inconsistent request for token", extra={"user": login})
        raise credentials_exception
    pass_with_hash = password + str(user.pass_salt)
    if not hs.sha256(pass_with_hash.encode("utf-8")).digest() == user.pass_hash:
        logging.info(msg="Attempt to get token with wrong credentials", extra={"user": login})
        raise credentials_exception
    logging.info(msg="User authenticated", extra={"user": login})
    return user


def check_credentials(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: orm.Session = Depends(db.get_db)
    ) -> rg.UserDB:   

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            logging.error(msg="Inconsistent jwt, no username", extra={"user": username})
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWKError:
        logging.error(msg="Inconsistent jwt", extra={"user": username})
        raise credentials_exception
    _user = session.get(rg.UserDB,token_data.username) 
    match _user:
        case None:
            logging.error(msg="Inconsistent jwt, user not found in db", extra={"user": username})
            raise credentials_exception
        case other:
            logging.info(msg="User authenticated using jwt", extra={"user": username})
            return _user 