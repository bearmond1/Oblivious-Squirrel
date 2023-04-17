from fastapi import HTTPException
import psycopg2 as pg
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
import os



def get_db():
    db_conn = SessionLocal()
    try:
        yield db_conn
        logging.info(msg="DB conn established", extra={"db_conn": db_conn})
    finally:
        db_conn.close()
        logging.info(msg="DB conn closed", extra={"db_conn": db_conn})


def get_engine():
   db_conn_str = os.getenv('db_connection_string_tt')
   match db_conn_str:
       case None:
           logging.error(msg="Could not find 'db_connection_string_tt' enviroment variable")
           raise Exception
       case other:
           return create_engine(url=db_conn_str) 

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush = False, bind=engine)
Base = declarative_base()