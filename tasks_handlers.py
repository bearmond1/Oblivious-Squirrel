import datetime as dt
import sqlalchemy as sql
import sqlalchemy.orm as orm
from register import *
from model import *



def post_task_handler(task: Task, user: returnUser, db: orm.Session) -> api.Response:

    task.created_at = dt.datetime.utcnow()
    task.created_by = user.login
    task.changed_by = user.login
    task.changed_at = dt.datetime.utcnow()
    task.status = "New"
    if task.parent == 0:
        task.parent = None

    task.id = seq.next_value()

    task_db = TaskDB(**task.dict())
    try:
        db.add(task_db)
        db.commit()
        logging.info("Task was created", extra={"task": task, "task_db": task_db, "user": user.login, "db_conn": db})
        response = api.Response(status_code=200)
    except Exception as e:
        db.rollback()
        logging.exception(msg= "Exception during writing task to the database", extra = {"Exception obj": e, "task": task, "task_db": task_db, "user": user, "db_conn": db})
        raise api.HTTPException(status_code=500, detail="Internal error")
    db.refresh(task_db)
    return response


def get_tasks_handler(
    parent: int | None,
    type: str | None,
    status: str | None,
    limit: int | None,
    offset_entity_id: int | None,
    sorting_field_name: str | None,
    sorting_field_val: str | None,
    header_text: str | None ,
    content_text: str | None  ,
    db: orm.Session,
    user: UserDB
    ):

    
    query_details = {
        "parent": parent,
        "type": type,
        "status": status,
        "offset_entity_id": offset_entity_id,
        "sorting_field_name": sorting_field_name,
        "sorting_field_val": sorting_field_val,
        "header_text": header_text,
        "content_text": content_text
    }

    # if we perform sorted query with offset: primary key, sorting field name and value should be specified
    
    # offset without specified sorting field means offset is by id
    if sorting_field_val != None and sorting_field_name == None:
        sorting_field_name = "id"
    else:
        # offset by sort field but no PK specified
        if sorting_field_val != None and sorting_field_name != None and offset_entity_id == None:
            logging.error(msg="Inconsistent request from front", extra={"query_details": query_details, "user": user.login})
            raise api.HTTPException(status_code=400, detail="For sorted queries with offset PK should be specified")
        

    if sorting_field_name == None:
        sorting_field_name = "id"

    if not parent:
        parent_clause = sql.or_(TaskDB.parent == None, TaskDB.parent != None)
    else:
        parent_clause = TaskDB.parent == parent
    
    if not type:
        type_clause = TaskDB.type != None
    else:
        type_clause = TaskDB.type == type
    
    if not status:
        status_clause = TaskDB.status != None
    else:
        status_clause = TaskDB.status == status
    
    if not offset_entity_id:
        id_clause = TaskDB.id != None
    else:
        id_clause = TaskDB.id > offset_entity_id


    match sorting_field_name:
        case "parent":
            sorting_field = TaskDB.parent
        case "type":
            sorting_field = TaskDB.type
        case "status":
            sorting_field = TaskDB.status
        case "header":
            sorting_field = TaskDB.header
        case "created_at":
            sorting_field = TaskDB.created_at
        case "changed_by":
            sorting_field = TaskDB.changed_by
        case "changed_at":
            sorting_field = TaskDB.changed_at
        case "changed_at":
            sorting_field = TaskDB.changed_at        
        case "assigned_to":
            sorting_field = TaskDB.assigned_to        
        case "id":
            sorting_field = TaskDB.id
        case other:
            logging.error(msg="Invalid sotring field", extra={"query_details": query_details, "user": user.login})
            raise api.HTTPException(status_code=400, detail=("Could not parse sorting field name: " + sorting_field_name))
    
    
    if sorting_field_val != None:
        sorting_field_clause = sorting_field >= sorting_field_val
    else:
        sorting_field_clause = TaskDB.id != None

    if header_text is None:
        header_clause = TaskDB.header.like("%")
    else:
        header_clause = TaskDB.header.like(f"%{header_text}%")

    if content_text is None:
        content_clause = TaskDB.header.like("%")
    else:
        content_clause = TaskDB.header.like(f"%{content_text}%")
    
    result = db.query(TaskDB).where( sql.and_(parent_clause,type_clause,status_clause, id_clause, sorting_field_clause,header_clause,content_clause ) ).order_by(sorting_field).limit(limit).all() 
    logging.info(msg = "Tasks requested", extra={"query_details": query_details, "user": user.login})
    return result


def update_task_handler(task: Task, user: returnUser, db: orm.Session):

    task.changed_by = user.login
    task.changed_at = dt.datetime.utcnow()
    new_task_db = TaskDB(**task.dict())

    task_history = TaskHistory()
    task_history.task_id = task.id
    task_history.changed_at = task.changed_at
    task_history.changed_by = task.changed_by
    task_history.assigned_to = task.assigned_to
    task_history.content = task.content
    task_history.header = task.header
    task_history.parent = task.parent
    task_history.status = task.status
    task_history.type = task.type


    try:
        task_db = db.query(TaskDB).where(TaskDB.id == new_task_db.id).first()
        task_db.parent = new_task_db.parent
        task_db.header = new_task_db.parent
        task_db.content = new_task_db.content
        task_db.type = new_task_db.type
        task_db.assigned_to = new_task_db.assigned_to
        task_db.status = task_db.status
        task_db.changed_at = dt.datetime.utcnow()
        task_db.changed_by = user.login
        task_db.created_by = new_task_db.created_by

        db.add(task_history)

        db.commit()
        response = api.Response(status_code=200)
        logging.info( msg="Task changed", extra= {"task": task, "task_db": task_db, "user": user.login})
    except Exception as e:
        db.rollback()
        logging.exception(msg="Error when updating task", extra={"task": task, "task_db": task_db, "user": user.login, "db_conn": db})
        raise api.HTTPException(status_code=500, detail="Internal error")
    db.refresh(task_db)

    return response


def get_task_history_handler(task_id: int, db: orm.Session):

    return db.query(TaskHistory).where(TaskHistory.task_id == task_id).all()