import ipaddress
#import logging

from vmcjp.utils import msg_const, cmd_const
from vmcjp.slack.messages import message_handler
from vmcjp.utils.lambdautils import call_lambda_sync, call_lambda_async
from vmcjp.slack.db import read_cred_db, write_cred_db, delete_cred_db, write_event_db, delete_event_db

#logger = logging.getLogger()
#logger.setLevel(logging.INFO)

def command_handler(cmd, event):
    eval(cmd)(event)

def prepare_data_for_lambda(event, vmc_command):
    data = {
        "vmc_command": vmc_command,
        "user_id": event.get("user_id"),
        "token": event.get("token"),
        "org_id": event.get("org_id"),
        "db_url": event.get("db_url"),
        "access_token": event.get("access_token"),
        "expire_time": event.get("expire_time")
    }
    return data

def cancel_register(event):
    message_handler(msg_const.CANCEL_TOKEN, event)
    delete_cred_db(event.get("db_url"), event.get("user_id"))

def register_org(event):
    message_handler(msg_const.REGISTER_ORG, event)
    write_cred_db(
        event.get("db_url"),
        event.get("user_id"), 
        {
            "status": cmd_const.REGISTER_ORG_ID
        }
    )

def register_org_id(event):
    message_handler(msg_const.REGISTER_TOKEN, event)
    write_cred_db(
        event.get("db_url"),
        event.get("user_id"), 
        {
            "org_id": event.get("text"),
            "status": cmd_const.REGISTER_TOKEN
        }
    )

def register_token(event):
#    cred = read_cred_db(event.get("db_url"), event.get("user_id"))
#    user_name = validate_token(event.get("text"), cred.get("org_id"))
    data = {
        "vmc_command": "validate_token",
        "token": event.get("text"),
        "org_id": event.get("org_id")
    }
    try:
        user_name = call_lambda_sync(
            "slack_vmc", data
        )
        message_handler(msg_const.SUCCESS_TOKEN, event)
        write_cred_db(
            event.get("db_url"),
            event.get("user_id"), 
            {
                "status": cmd_const.REGISTERED, 
                "token": event.get("text"), 
                "user_name": user_name
            }
        )
    except Exception as e:
        message_handler(msg_const.FAILED_TOKEN, event)
        event.update({"text": str(e)})
        message_handler(msg_const.WRONG_TOKEN, event)
        delete_cred_db(event.get("db_url"), event.get("user_id"))

def delete_org(event):
    message_handler(msg_const.DELETE_ORG, event)
    delete_cred_db(event.get("db_url"), event.get("user_id"))

def list_sddcs(event):
    data = prepare_data_for_lambda(event, "list_sddcs")
    try:
        event.update(
            {
                "sddcs": call_lambda_sync(
                    "slack_vmc", data
                )
            }
        )
        message_handler(msg_const.SDDCS_TXT, event)
        message_handler(msg_const.SDDCS_MSG, event)
    except Exception as e:
        event.update({"text": str(e)})
        message_handler(msg_const.ERROR, event)

#def create_zero_sddc(event, db): #for internal test only
#    message_handler(msg_const.SDDC_WIZARD, event)
#    message_handler(msg_const.CHECK_RESOURCE, event)
#    max_hosts = get_max_num_hosts(
#        event.get("token"),
#        event.get("org_id")
#    )
#    event.update({"max_hosts": max_hosts})
#    if max_hosts < 1:
#        message_handler(msg_const.NOT_ENOUGH, event)
#        db.delete_event_db(event.get("user_id"))
#    else:
#        message_handler(msg_const.MAX_HOSTS, event)
#        db.write_event_db(
#            event.get("user_id"), 
#            {
#                "command": cmd_const.COMMAND_SDDC[event.get("text")],
#                "status": cmd_const.CHECK_MAX_HOSTS, 
#                "max_hosts": max_hosts,
#                "provider": "ZEROCLOUD"
#            }
#        )

def create_sddc(event):
    #first create sddc command from text message
    message_handler(msg_const.SDDC_WIZARD, event)
    message_handler(msg_const.CHECK_RESOURCE, event)
    data = prepare_data_for_lambda(event, "check_max_hosts")
    max_hosts = call_lambda_sync(
        "slack_vmc", data
    )
    max_hosts = 10 #for test
    event.update({"max_hosts": max_hosts})
    if max_hosts < 1:
        message_handler(msg_const.NOT_ENOUGH, event)
        delete_event_db(event.get("db_url"), event.get("user_id"))
    else:
        message_handler(msg_const.MAX_HOSTS, event)
        write_event_db(
            event.get("db_url"), 
            event.get("user_id"), 
            {
                "command": cmd_const.COMMAND_SDDC[event.get("text")],
                "status": cmd_const.CHECK_MAX_HOSTS, 
                "max_hosts": max_hosts,
                "provider": "AWS"
            }
        )

def check_max_hosts(event):
    #response if proceed with this wizard or not and send select menu of AWS Region
    if "yes" in event.get("response"):
        data = prepare_data_for_lambda(event, "list_region")
        event.update(
            {
                "region_list": call_lambda_sync(
                    "slack_vmc", data
                )
            }
#            {
#                "region_list": [
#                    {
#                        "text": "AP_NORTHEAST_1", #for internal use
#                        "value": "AP_NORTHEAST_1" #for internal use
#                    }
#                ]
#            }
        )
        message_handler(msg_const.REGION, event)
        write_event_db(
            event.get("db_url"), 
            event.get("user_id"), 
            {
                "status": cmd_const.AWS_REGION
            }
        ) 
    else:
        message_handler(msg_const.CANCEL_SDDC, event)
        delete_event_db(event.get("db_url"), event.get("user_id"))

def aws_region(event):
    #update AWS Region and send sddc name message
    message_handler(msg_const.SDDC_NAME, event)
    write_event_db(
        event.get("db_url"),
        event.get("user_id"), 
        {
            "region": event.get("response"),
            "status": cmd_const.SDDC_NAME
        }
    )

def sddc_name(event):
    #update sddc name and send link aws menu or single mult menu
#    max_hosts = event.get("max_hosts")
    message_handler(msg_const.MEDIUM_LARGE, event)
    status = cmd_const.MEDIUM_LARGE
    
#    if max_hosts == 1:
#        message_handler(msg_const.LINK_AWS, event)
#        status = cmd_const.AWS_ACCOUNT
#    elif max_hosts < 6:
#        message_handler(msg_const.SINGLE_MULTI, event)
#        status = cmd_const.SINGLE_MULTI
#    else:
#        message_handler(msg_const.STRETCH, event)
#        status = cmd_const.SINGLE_MULTI
    
    write_event_db(
        event.get("db_url"), 
        event.get("user_id"), 
        {
            "status": status, 
            "sddc_name": event.get("text")
        }
    )

def medium_large(event):
    max_hosts = event.get("max_hosts")
    
    if max_hosts == 1:
        message_handler(msg_const.LINK_AWS, event)
        status = cmd_const.AWS_ACCOUNT
    elif max_hosts < 6:
        message_handler(msg_const.SINGLE_MULTI, event)
        status = cmd_const.SINGLE_MULTI
    else:
        message_handler(msg_const.STRETCH, event)
        status = cmd_const.SINGLE_MULTI
    
    write_event_db(
        event.get("db_url"), 
        event.get("user_id"), 
        {
            "status": status, 
            "size": event.get("response")
        }
    )

def single_multi(event):
    #update single or multi hosts and send link aws nemu or max hosts menu
    if "single" in event.get("response"):
        message_handler(msg_const.LINK_AWS, event)
        write_event_db(
            event.get("db_url"),
            event.get("user_id"),
            {
                "status": cmd_const.LINK_AWS
            }
        )
    elif "multi" in event.get("response"):
        message_handler(msg_const.INSTANCE_TYPE, event)
        write_event_db(
            event.get("db_url"),
            event.get("user_id"),
            {
                "status": cmd_const.INSTANCE_TYPE,
                "link_aws": "True"
            }
        )
    else:
        message_handler(msg_const.INSTANCE_TYPE, event)
        write_event_db(
            event.get("db_url"),
            event.get("user_id"),
            {
                "status": cmd_const.INSTANCE_TYPE,
                "deployment_type": "MultiAZ",
                "link_aws": "True"
            }
        )
        

def instance_type(event):
    if "i3" == event.get("response"):
        event.update(
            {
                "num_hosts_list": list_num_hosts(
                    event.get("max_hosts"),
                    event.get("deployment_type")
                )
            }
        )
        message_handler(msg_const.NUM_HOSTS, event)
        status = cmd_const.NUM_HOSTS
        instance_type = "I3_METAL"
    elif "r5" == event.get("response"):
        message_handler(msg_const.STORAGE_CAPACITY, event)
        status = cmd_const.STORAGE_CAPACITY
        instance_type = "R5_METAL"
        
    write_event_db(
        event.get("db_url"),
        event.get("user_id"),
        {
            "status": status,
            "host_instance_type": instance_type 
        }
    )
    
def storage_capacity(event):
    #storage capacity is 15003 or 20004,25005,30006,35007 per host
    event.update(
        {
            "num_hosts_list": list_num_hosts(
                event.get("max_hosts"),
                event.get("deployment_type")
            )
        }
    )
    message_handler(msg_const.NUM_HOSTS, event)
    write_event_db(
        event.get("db_url"),
        event.get("user_id"),
        {
            "status": cmd_const.NUM_HOSTS,
            "storage_capacity": int(event.get("response")) #need to multiply by num_hosts later
        }
    )

def list_num_hosts(num_hosts, type):
    if type is None:
        return [
            {
                "text": i + 1, 
                "value": i + 1
            } for i in range(2, num_hosts)
        ]
    else:
        return [
            {
                "text": i + 2, 
                "value": i + 2
            } for i in range(4, num_hosts, 2)
        ]

def num_hosts(event):
    #update num hosts and send AWS account menu
    list_aws_account(event)
    num_hosts = int(event.get("response"))
    storage_capacity = None
    
    if event.get("storage_capacity") is not None:
        storage_capacity = event.get("storage_capacity")
        storage_capacity *= num_hosts
    
    write_event_db(
        event.get("db_url"), 
        event.get("user_id"), 
        {
            "status": cmd_const.AWS_ACCOUNT, 
            "num_hosts": num_hosts, 
            "link_aws": "True",
            "storage_capacity": storage_capacity
        }
    )

def link_aws(event):
    #in case of Single host sddc, and update link aws and send AWS account menu or enter mgmt cider message
    if "True" in event.get("response"): #in case of linking customer AWS VPC to this SDDC
        list_aws_account(event)
        status = cmd_const.AWS_ACCOUNT
    else: #in case of not linking customer AWS VPC
        message_handler(msg_const.CIDR, event)
        status = cmd_const.MGMT_CIDR
        
    write_event_db(
        event.get("db_url"), 
        event.get("user_id"), 
        {
            "status": status, 
            "num_hosts": 1, 
            "sddc_type": "1NODE", 
            "link_aws": event.get("response")
        }
    )

def list_aws_account(event):
    data = prepare_data_for_lambda(event, "list_aws_account")
    event.update(
        {
            "aws_account_list": call_lambda_sync(
                "slack_vmc", data
            )
#            "aws_account_list": [
#                {
#                    "text": event.get("aws_internal_account"), #for internal use
#                    "value": "{}+{}".format(
#                        event.get("aws_internal_account"), 
#                        event.get("aws_internal_id")
#                    ) #for internal use
#                }
#            ]
        }
    )
    message_handler(msg_const.AWS_ACCOUNT, event)

def aws_account(event):
    #update selected AWS account and send VPC list menu
    aws_account = event.get("response").split("+")[0]
    aws_id = event.get("response").split("+")[1]
    
    data = prepare_data_for_lambda(event, "list_vpc")
    data.update(
        {
            "linked_account_id": aws_id,
            "region": event.get("region")
        }
    )
    event.update(
        {
            "vpc_list": call_lambda_sync(
                "slack_vmc", data
            )
        }
    )
    message_handler(msg_const.AWS_VPC, event)
    write_event_db(
        event.get("db_url"),
        event.get("user_id"), 
        {
            "status": cmd_const.AWS_VPC, 
            "aws_account": aws_account,
            "connected_account_id": aws_id
        }
    )

def aws_vpc(event):
    #update selected VPC and send list of AWS Subnet menu
    vpc_id = event.get("response")
    
    data = prepare_data_for_lambda(event, "list_subnet")
    data.update(
        {
            "linked_account_id": event.get("aws_id"),
            "region": event.get("region"),
            "connected_account_id": event.get("connected_account_id"),
            "vpc_id": vpc_id
        }
    )
    event.update(
        {
            "subnet_list": call_lambda_sync(
                "slack_vmc", data
            )
        }
    )
    message_handler(msg_const.AWS_SUBNET, event)
    write_event_db(
        event.get("db_url"), 
        event.get("user_id"),  
        {
            "status": cmd_const.AWS_SUBNET, 
            "vpc_id": vpc_id
        }
    )

def aws_subnet(event):
    message_handler(msg_const.CIDR, event)
    write_event_db(
        event.get("db_url"), 
        event.get("user_id"), 
        {
            "status": cmd_const.MGMT_CIDR, 
            "customer_subnet_id": event.get("response")
        }
    )

def mgmt_cidr(event):
    text = event.get("text")
    
    if is_network(text):
        if is_valid_network(text):
            event.update({"vpc_cidr": text})
            message_handler(msg_const.SDDC_CONFIRM, event)
            write_event_db(
                event.get("db_url"), 
                event.get("user_id"), 
                {
                    "status": cmd_const.CHECK_CONFIG, 
                    "vpc_cidr": text
                }
            )
        else:
            message_handler(msg_const.WRONG_NETWORK, event)
    else:
        message_handler(msg_const.WRONG_NETWORK, event)

def is_network(address):
    try:
        ipaddress.ip_network(address)
        return True
    except ValueError:
        return False

def is_valid_network(address):
    try:
        nw = ipaddress.ip_network(address)
    except ValueError:
        return False
    
    prefix = nw.prefixlen
    if prefix != 23 and prefix != 20 and prefix != 16:
        return False
    
    rs10 = ipaddress.ip_network(u'10.0.0.0/15')
    rs192 = ipaddress.ip_network(u'192.168.1.0/24')
    rs172 = ipaddress.ip_network(u'172.31.0.0/16')

    if nw.subnet_of(rs10):
        return False
    elif rs192.subnet_of(nw):
        return False
    elif nw.subnet_of(rs172):
        return False
    
    nw10 = ipaddress.ip_network(u'10.0.0.0/8')
    nw172 = ipaddress.ip_network(u'172.16.0.0/12')
    nw192 = ipaddress.ip_network(u'192.168.0.0/16')
    
    if nw.subnet_of(nw10):
        return True
    elif nw.subnet_of(nw172):
        return True
    elif nw.subnet_of(nw192):
        return True
    else:
        return False

def check_config(event):
    if "yes" in event.get("response"):
        message_handler(msg_const.CREATE, event)
        event.update({"vmc_command": "create_sddc"})
        
        try:
            task_id = call_lambda_sync("slack_vmc", event)
        except Exception as e:
            event.update(
                {
                    "message": "Sorry, failed to create sddc.  {}".format(str(e)),
#                    "text": str(e),
#                    "status": "task_failed"
                }
            )
            message_handler(msg_const.SDDC_RESULT, event)
            delete_event_db(event.get("db_url"), event.get("user_id"))
        else:
            event.update({"task_id": task_id})
            event.update(
                {"status": "task_started"}
            )
            write_event_db(
                event.get("db_url"),
                event.get("user_id"),
                {
                    "status": "creating", 
                }
            )
            call_lambda_async("check_task", event)
            message_handler(msg_const.TASK_MSG, event)
            message_handler(msg_const.CRUD_SDDC, event)
            message_handler(msg_const.TASK_WH, event)
            
    else:
        message_handler(msg_const.CANCEL_SDDC, event)
        delete_event_db(event.get("db_url"), event.get("user_id"))

def delete_sddc(event):
    data = prepare_data_for_lambda(event, "list_sddcs_name_id")
    try:
        event.update(
            {
                "option_list": call_lambda_sync(
                    "slack_vmc", data
                )
            }
        )
    except Exception as e:
        event.update({"text": str(e)})
        message_handler(msg_const.ERROR, event)
    else:
        message_handler(msg_const.DELETE_SDDC, event)
        write_event_db(
            event.get("db_url"), 
            event.get("user_id"), 
            {
                "command": cmd_const.COMMAND_SDDC[event.get("text")],
                "status": cmd_const.DELETE_SDDC
            }
        )
#    event.update(
#        {
#            "option_list": list_sddcs__(
#                event.get("token"), 
#                event.get("org_id")
#            )
#        }
#    )
#    message_handler(msg_const.DELETE_SDDC, event)
#    db.write_event_db(
#        event.get("user_id"),
#        {
#            "command": cmd_const.COMMAND_SDDC[event.get("text")],
#            "status": cmd_const.DELETE_SDDC
#        }
#    )
    
def selected_sddc_to_delete(event):
    sddc_name = event.get("response").split("+")[0]
    sddc_id = event.get("response").split("+")[1]
    event.update(
        {"sddc_name": sddc_name}
    )
    write_event_db(
        event.get("db_url"),
        event.get("user_id"),
        {
            "sddc_name": sddc_name,
#            "sddc_id": sddc_id
            "sddc_id": "ffcdc226-c3a6-4c8c-bc9b-3b14de2e089c"
        }
    )
    message_handler(msg_const.CONFIRM_DELETE, event)

def delete_confirmation(event):
    response = event.get("response")
    if "yes" in response:
        message_handler(msg_const.START_DELETE, event)
#        event.update(result)
#        event.update(
#            {"user_name": event.get("user_name")}
#        )
        if check_sddc_user(event):
            call_lambda_async("delete_sddc", event)
        else:
            message_handler(msg_const.CANT_DELETE, event)
            delete_event_db(
                event.get("db_url"), 
                event.get("user_id")
            )
    else:
        message_handler(msg_const.CANCEL_DELETE, event)
        delete_event_db(
            event.get("db_url"), 
            event.get("user_id")
        )

def check_sddc_user(event):
    data = prepare_data_for_lambda(event, "get_sddc_user")
    user = call_lambda_sync("slack_vmc", data)
    if user == event.get("user_name"):
        return True
    else:
        return False

#def restore_sddc(event, db): #for internal only
#    hoge = 1
