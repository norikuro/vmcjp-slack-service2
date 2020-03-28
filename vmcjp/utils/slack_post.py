import json
import urllib.request

def post(url, data, bot_oauth_token=None):
    headers = {
        "Content-Type": "application/json"
    }
    
    if bot_oauth_token is not None:
        headers.update(
            {
                "Authorization": "Bearer {}".format(
                    bot_oauth_token
                )
            }
        )
    
    request = urllib.request.Request(
        url, 
        data=json.dumps(data).encode("utf-8"), 
        headers=headers
    )
    
    return urllib.request.urlopen(request)

def post_text(
    url,
    slack_token, 
    channel,
    data,
    bot_token=None
):
    post_data = {
        "token": slack_token,
        "channel": channel,
    }
    post_data.update(data)
    
    response = post(url, post_data, bot_token)
    return response

def post_option(
    url,
    slack_token, 
    channel,
    button, 
    option_list=None, 
    bot_token=None
):
    
    button_set = json.load(open(button, 'r'))
    if option_list is not None:
        button_set["attachments"][0]["actions"][0].update(
            {"options": option_list}
        )
    
    response = post_text(
        url,
        slack_token,
        channel,
        button_set,
        bot_token
    )
    return response

def post_button(
    url, 
    slack_token,
    channel,
    button, 
    bot_token=None
):
    
    button_set = json.load(open(button, 'r'))

    response = post_text(
        url,
        slack_token,
        channel,
        button_set,
        bot_token
    )
    return response

def create_button(field_dics, button):
    button_set = json.load(open(button, 'r'))
    attachments = button_set.get("attachments")
    for attachment in attachments:
        fields = attachment.get("fields")
#        attachment.update(
#            {
#                "fields": None 
#                if fields is None 
#                else [
#                    {
#                        "value": event.get(field.get("value"))
#                    } 
#                    for field in fields
#                ]
#            }
#        )
        if fields is not None:
            for field in fields:
                field.update({"value": field_dics.get(field.get("value"))})
    return button_set

def post_field_button(
    url, 
    slack_token, 
    channel, 
    button, 
    field_dics, 
    bot_token=None
):
    
    button_set = create_button(field_dics, button)
    
    response = post_text(
        url,
        slack_token,
        channel,
        button_set,
        bot_token
    )
    return response
