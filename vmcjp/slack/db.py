from vmcjp.utils.lambdautils import call_lambda_sync, call_lambda_async

def read_event_db(db_url, user_id, minuites=None):
    event = {
      "db_url": db_url,
      "user_id": user_id,
      "minuites": minuites,
      "db_command": "read_event_db"
    }
    return call_lambda_sync("slack_db", event)

def write_event_db(db_url, user_id, data):
    event = {
        "db_url": db_url,
        "user_id": user_id,
        "db_command": "write_event_db",
        "data": data
    }
    call_lambda_async("slack_db", event)

def delete_event_db(db_url, user_id):
    event = {
        "db_url": db_url,
        "user_id": user_id,
        "db_command": "delete_event_db"
    }
    call_lambda_async("slack_db", event)
    

def read_cred_db(db_url, user_id):
    event = {
      "db_url": db_url,
      "user_id": user_id,
      "db_command": "read_cred_db"
    }
    return call_lambda_sync("slack_db", event)

def write_cred_db(db_url, user_id, data):
    event = {
        "db_url": db_url,
        "user_id": user_id,
        "db_command": "write_cred_db",
        "data": data
    }
    call_lambda_async("slack_db", event)

def delete_cred_db(db_url, user_id):
    event = {
        "db_url": db_url,
        "user_id": user_id,
        "db_command": "delete_cred_db"
    }
    call_lambda_async("slack_db", event)
