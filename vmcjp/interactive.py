#import logging

from vmcjp.utils import msg_const
from vmcjp.slack.db import read_event_db, read_cred_db
from vmcjp.slack.messages import message_handler
from vmcjp.slack.command import command_handler

#logger = logging.getLogger()
#logger.setLevel(logging.INFO)

def lambda_handler(event, context):
#    logging.info(event)
    user_id = event.get("user_id")
    db_url = event.get("db_url")
    
    event_db = read_event_db(db_url, user_id, 5)
    
    if event_db is None:
      message_handler(msg_const.MAY_I, event)
      return
    
    cred_db = read_cred_db(db_url, user_id)
    event.update(
        {
            "token": cred_db.get("token"),
            "org_id": cred_db.get("org_id"),
            "user_name": cred_db.get("user_name"),
            "access_token": cred_db.get("access_token"),
            "expire_time": cred_db.get("expire_time")
        }
    )
    event.update(event_db)
    
    command_handler(
        event.get("callback_id"), 
        event
    )
