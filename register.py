import hashlib as hs
import random as r
import string as s
import datetime as dt
import sqlalchemy.orm as orm
import sqlalchemy.exc as exc
import fastapi as api
import logging
from model import *



salt_length = 10



def register_handler(user: NewUser,db: orm.Session):

    # salt password and get hash
    salt = ''.join(r.choices(s.ascii_uppercase + s.digits, k=salt_length)) 
    pass_with_hash = user.password + ''.join(salt)
    hash = hs.sha256(pass_with_hash.encode("utf-8")).digest() 
    new_user = UserDB(login = user.login, pass_hash = hash, pass_salt = salt,  joined = dt.datetime.utcnow() ) 
    
    # insert and make response
    try:
        db.add(new_user)
        db.commit()        
        response = api.Response(status_code=200)
        logging.info(msg="Registered user", extra={"user": new_user.login})
    except exc.IntegrityError:
        db.rollback()
        logging.exception(msg="Attempt to create user with existing login", extra={"user": user.login})
        raise api.HTTPException(status_code=400, detail=f"Login {user.login} already in use.")
    except Exception:
        db.rollback()
        logging.exception(msg="Exception during creating new user", extra={"user": user, "db_conn": db})
        raise api.HTTPException(status_code=500, detail="Internal error")
    db.refresh(new_user)

    return response