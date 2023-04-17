from register import * 
import register as rg
from authentication import * 
from tasks_handlers import * 
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import db_conn as db
import sqlalchemy.orm as orm
from typing import Annotated
import datetime as dt
import logging
import os

# initialization
server = FastAPI()

match os.getenv('tt_logging_file'):
    case None:
        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',  level=logging.INFO)
    case filename: 
        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename=filename, level=logging.INFO)



@server.post("/register/")
async def handle_registration(user: NewUser,session: orm.Session = Depends(db.get_db)):
    return(register_handler(user,session ) )


@server.post("/token/", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: orm.Session = Depends(db.get_db) ):

    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = dt.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.login}, expires_delta=access_token_expires )
    return {"access_token": access_token, "token_type": "bearer"}



@server.get("/get_user/{login}", response_model=dict)
async def get_single_user(
    login: str,
    user: Annotated[UserDB, Depends(check_credentials)],
    session: orm.Session = Depends(db.get_db) 
    ) :

    _user: rg.UserDB | None = session.get(rg.UserDB,login)
    match _user:
        case None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND )
        case other:
            return returnUser(login = str(_user.login), joined = str(_user.joined))


@server.post("/post_task/", response_model=Task)
async def post_task(
    task: Task,
    user: Annotated[UserDB, Depends(check_credentials)],
    db: orm.Session = Depends(db.get_db) ) :
    
    return post_task_handler(task= task, user = user, db = db)


@server.get("/get_tasks")
async def get_tasks(
    user: Annotated[UserDB, Depends(check_credentials)],    
    db: orm.Session = Depends(db.get_db),
    parent: int | None = None,
    type: str | None = None,
    status: str | None = None,
    limit: int | None = None,
    offset_entity_id: int | None = None,
    sorting_field_name: str | None = None,
    sorting_field_val: str | None = None,
    header_text: str | None = None,
    content_text: str | None = None ):

    return get_tasks_handler(parent, type, status, limit, offset_entity_id, sorting_field_name, sorting_field_val, header_text, content_text, db, user)


@server.put ("/update_task/")
async def update_task(
    task: Task,
    user: Annotated[UserDB, Depends(check_credentials)],
    db: orm.Session = Depends(db.get_db) ) :
    
    return update_task_handler(task= task, user = user, db = db)


@server.get("/get_task_history/{task_id}")
async def get_task_history(
    task_id: int,
    user: Annotated[UserDB, Depends(check_credentials)],
    db: orm.Session = Depends(db.get_db) ):

    return get_task_history_handler(task_id, db)