#import logging

from vmcjp.utils import cmd_const, msg_const
from vmcjp.slack.db import read_event_db, read_cred_db, delete_event_db
from vmcjp.slack.messages import message_handler
from vmcjp.slack.command import command_handler

#logger = logging.getLogger()
#logger.setLevel(logging.INFO)

def event_cred_update(event, cred):
    event.update(
        {
            "token": cred.get("token"),
            "org_id": cred.get("org_id")
        }
    )

def lambda_handler(event, context):
    text = event.get("text").lower()
    
#    current = read_event_db(
#        event.get("db_url"), 
#        event.get("user_id"), 
#        120
#    )
#    logging.info(current)
#    if current is not None and current.get("status") in [cmd_const.CREATING, cmd_const.DELETING]:
#        message_handler(msg_const.ASK_WAIT_TASK, event)
#        return
    
    event_db = read_event_db(
        event.get("db_url"), 
        event.get("user_id"), 
        5
    )

    if event_db is None: # in the case of event db does not exist
        cred_db = read_cred_db(
            event.get("db_url"),
            event.get("user_id")
        )
        
        if cred_db is not None: # in the case of cred db exists
            cred_status = cred_db.get("status")
            
            if cred_status == cmd_const.REGISTERED:
                if text in cmd_const.COMMAND_SDDC:
                    event_cred_update(event, cred_db)
                    command_handler(cmd_const.COMMAND_SDDC[text], event)
                #elif text = cmd_const.CANCEL:
                    # cancel might come here in case of canceling create sddc etc.
                elif text == cmd_const.DELETE_ORG:
                    command_handler(cmd_const.COMMAND_ORG[text], event)
                elif text == cmd_const.HELP:
                    message_handler(msg_const.HELP, event)
                else:
                    message_handler(msg_const.MAY_I, event)
            elif cred_status == cmd_const.REGISTER_ORG_ID:
                if text == cmd_const.CANCEL:
                    command_handler(cmd_const.CANCEL_REGISTER, event)
                else:
                    command_handler(cmd_const.REGISTER_ORG_ID, event)
            elif cred_status == cmd_const.REGISTER_TOKEN:
                if text == cmd_const.CANCEL:
                    command_handler(cmd_const.CANCEL_REGISTER, event)  
                else:
                    event_cred_update(event, cred_db)
                    command_handler(cmd_const.REGISTER_TOKEN, event)
        
        else: # in the case of cred db does not exist
            if text == cmd_const.HELP:
                message_handler(msg_const.HELP, event)
            elif text == cmd_const.REGISTER_ORG:
                command_handler(cmd_const.COMMAND_ORG[text], event)
            elif text in cmd_const.COMMAND_SDDC:
                message_handler(msg_const.ASK_REGISTER_TOKEN, event)
            elif text == cmd_const.DELETE_ORG:
                message_handler(msg_const.ASK_REGISTER_TOKEN, event)
            else:
                message_handler(msg_const.MAY_I, event)
    
    else: # in the case of event db exists
        command = event_db.get("command")
        status = event_db.get("status")
        if text == cmd_const.CANCEL:
            if command == cmd_const.CREATE_SDDC_FUNC:
                message_handler(msg_const.CANCEL_SDDC, event)
            elif command == cmd_const.DELETE_SDDC_FUNC:
                message_handler(msg_const.CANCEL_DELETE, event)
            delete_event_db(event.get("db_url"), event.get("user_id"))
        elif status == cmd_const.SDDC_NAME:
            event.update(event_db)
            command_handler(cmd_const.SDDC_NAME, event)
        elif status == cmd_const.MGMT_CIDR:
            event.update(event_db)
            command_handler(cmd_const.MGMT_CIDR, event)
        elif command in ["create_sddc", "delete_sddc"]:
            message_handler(msg_const.ASK_SELECT_BUTTON, event)
