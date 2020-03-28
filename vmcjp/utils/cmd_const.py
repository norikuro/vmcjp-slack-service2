#!/usr/bin/env python

import sys

class _const:
  #followings are commands which we can run on slack app
  REGISTER_ORG = "register org"
  DELETE_ORG = "delete org"
  CREATE_ZERO_SDDC = "create zerocloud sddc"
  CREATE_SDDC = "create sddc"
  DELETE_SDDC = "delete sddc"
  LIST_SDDCS = "list sddcs"
  RESTORE_SDDC = "restore sddc" # for internal use
  CANCEL = "cancel"
  HELP = "help"
  
  
  #followings are command names which we can do on slack app
  REGISTER_ORG_FUNC = "register_org"
  DELETE_ORG_FUNC = "delete_org"
  CREATE_ZERO_SDDC_FUNC = "create_zero_sddc"
  CREATE_SDDC_FUNC = "create_sddc"
  DELETE_SDDC_FUNC = "delete_sddc"
  LIST_SDDCS_FUNC = "list_sddcs"
  RESTORE_SDDC_FUNC = "restore_sddc" # for internal use
    
  COMMAND_SDDC = {
    CREATE_ZERO_SDDC: CREATE_ZERO_SDDC_FUNC,
    CREATE_SDDC: CREATE_SDDC_FUNC,
    DELETE_SDDC: DELETE_SDDC_FUNC,
    LIST_SDDCS: LIST_SDDCS_FUNC,
    RESTORE_SDDC: RESTORE_SDDC_FUNC, # for internal use
  }
  
  COMMAND_ORG = {
    REGISTER_ORG: REGISTER_ORG_FUNC,
    DELETE_ORG: DELETE_ORG_FUNC
  }
  
  #followings are status of register ORG and token
  REGISTER_ORG_ID = "register_org_id"
  REGISTER_TOKEN = "register_token"
  REGISTERED = "registered"
  CANCEL_REGISTER = "cancel_register"
  
  #followings are status of create SDDC
  CHECK_MAX_HOSTS = "check_max_hosts"
  AWS_REGION = "aws_region"
  SDDC_NAME = "sddc_name"
  MEDIUM_LARGE = "medium_large"
  SINGLE_MULTI = "single_multi"
  LINK_AWS = "link_aws"
  INSTANCE_TYPE = "instance_type"
  STORAGE_CAPACITY = "storage_capacity"
  NUM_HOSTS = "num_hosts"
  AWS_ACCOUNT = "aws_account"
  AWS_VPC = "aws_vpc"
  AWS_SUBNET = "aws_subnet"
  MGMT_CIDR = "mgmt_cidr"
  CHECK_CONFIG = "check_config"
  CREATING = "creating"
  
  #followings are status of delete SDDC
  DELETE_SDDC = "delete_sddc"

  class ConstError(TypeError):
    pass
  
  def __setattr__(self, name, value):
    if name in self.__dict__:
      raise self.ConstError("Can't rebind const (%s)" % name)
    self.__dict__[name] = value

sys.modules[__name__]=_const()
