import boto3
import json
import os
from boto3.dynamodb.conditions import Key
from datetime import datetime, timezone

# Instantiate messages table
messages_table = boto3.resource('dynamodb').Table(os.environ.get('DYNAMODB_MESSAGES_TABLE'))


# Define a function named get_messages which takes two arguments: event and context
def get_messages(event, context):
    """Return the messages published in the chat room

    :param chat_id: (path parameter) ID of the chat
    :type chat_id: str

    :rtype: dict
        return example:
        {
            "messages": [
                {   "ts": "timestamp",   "user_id"": "author1",   "text": "text message"   },
                ...
            ]
        }
    """

    # Extract the chat_id from the pathParameters in the event object, if not found, set it to None
    chat_id = event.get('pathParameters', {}).get('chat_id')

    # Query the messages_table using the chat_id as a KeyConditionExpression
    messages = messages_table.query(KeyConditionExpression=Key('chat_id').eq(chat_id))

    # Check if the "Items" key exists in the messages dictionary
    if "Items" in messages:
        # Construct a body dictionary containing status code 200 and a list of messages
        body = {
            "status": 200,
            'messages': [ {'ts': x['ts'], 'user_id': x['user_id'], 'text': x['text']} for x in messages["Items"] ],
        }
        # Construct a response dictionary with statusCode 200 and the body containing JSON serialized body dictionary
        response = {
            "statusCode": 200,
            "body": json.dumps(body)
        }
    else: # If no items found, construct a body dictionary for 404 error
        # No Item == 404
        body = {
            "status": 404,
            "title": "Chat not found",
            "detail": f"Chat {chat_id} not found in database",
        }
        # Construct a response dictionary with statusCode 404 and the body containing JSON serialized body dictionary
        response = {
            "statusCode": 404,
            "body": json.dumps(body)
        }
    # Return the constructed response
    return response


# Define a function named send_message which takes two arguments: event and context
def send_message(event, context):
    """Send a message into a chat room

    :param chat_id: (path parameter) ID of the chat
    :type chat_id: str
    :param message: (body) new info
    :type message: dict
        message example:
        {
            "user_id": "user ID of the author",
            "text": "content written by the user",
        }

    :rtype: SimpleResponse
    """
    # Extract the chat_id from the pathParameters in the event object, if not found, set it to None
    chat_id = event.get('pathParameters', {}).get('chat_id')

    # Load the JSON data from the body of the event, if no body present, set it to an empty dictionary
    message = json.loads(event.get('body', '{}'))

    # Put a new item into the messages_table with the provided chat_id, timestamp, user_id, and text
    messages_table.put_item(
        Item={
            'chat_id': chat_id,
            'ts': datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
            'user_id': message['user_id'],
            'text': message['text'],
        }
    )
    # Construct a body dictionary indicating a successful creation (status code 201)
    body = {
        "status": 201, # 201 means the request has succeeded and has led to the creation of a resource
        "title": "OK",
        "detail": f"New message posted into chat {chat_id}",
    }

    # Return a dictionary containing the statusCode 201 and the body containing JSON serialized body dictionary
    return {
        "statusCode": 201,
        "body": json.dumps(body)
    }
