# Oblivious Squirrel

### About
Backend of a simple Task Tracker ( jira clone ) made with FastAPI & SQLalchemy.
Uses password hashing, bearer jwt, [pagination by key](https://ivopereira.net/efficient-pagination-dont-use-offset-limit), logging.

### DB Structure

#### Task 
* id
* parent (another task, nullable)
* header
* content
* type
* status
* assigned_to
* changed_by
* changed_at
* created_at
* created_by

#### User
* login
* joined (date)
* pass_hash
* pass_salt

#### History
History of task changes

* task_id
* changed_at
* parent
* header
* content
* type
* status
* assigned_to
* changed_by