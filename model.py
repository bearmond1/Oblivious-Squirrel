import sqlalchemy as sql
from pydantic import BaseModel
import datetime as dt
import db_conn as db


metadata = sql.MetaData(schema='public')
seq = sql.Sequence('my_serial', metadata=metadata)

# task type for http exchange
class Task(BaseModel):
    id: int
    parent: int
    header: str
    content: str
    type: str
    assigned_to: str
    status: str
    created_at: dt.datetime
    created_by: str
    changed_by: str
    changed_at: dt.datetime

# task type for DB
class TaskDB(db.Base):
    __tablename__ = "Task"

    id = sql.Column(sql.Integer, autoincrement=True, primary_key=True) 
    parent = sql.Column(sql.Integer, nullable=True)
    header = sql.Column(sql.String(20))
    content = sql.Column(sql.String, nullable=True)
    type = sql.Column(sql.String(10))
    assigned_to = sql.Column(sql.String(10))
    status = sql.Column(sql.String(10))
    created_at = sql.Column(sql.TIMESTAMP)
    created_by = sql.Column(sql.String(10))
    changed_by = sql.Column(sql.String(10))
    changed_at = sql.Column(sql.TIMESTAMP)


class TaskHistory(db.Base):

    __tablename__ = "History"

    task_id = sql.Column(sql.Integer, primary_key=True) 
    changed_at = sql.Column(sql.TIMESTAMP, primary_key = True)
    parent = sql.Column(sql.Integer)
    header = sql.Column(sql.String(20))
    content = sql.Column(sql.String)
    type = sql.Column(sql.String(10))
    assigned_to = sql.Column(sql.String(10))
    status = sql.Column(sql.String(10))
    changed_by = sql.Column(sql.String(10))

    

# user type registration
class NewUser(BaseModel):
    login: str
    password: str

# user type to return to front
class returnUser(BaseModel):
    login: str
    joined: str #dt.datetime


# user type for db
class UserDB(db.Base):
    __tablename__ = "User"

    login = sql.Column(sql.String(10), primary_key=True)
    pass_hash = sql.Column(sql.LargeBinary)
    pass_salt = sql.Column(sql.String(10))
    joined = sql.Column(sql.TIMESTAMP)