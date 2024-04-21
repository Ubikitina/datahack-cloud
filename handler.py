import boto3
import json
import os
from boto3.dynamodb.conditions import Key
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
messages_table = dynamodb.Table(os.environ.get('DYNAMODB_MESSAGES_TABLE'))
ads_table = dynamodb.Table(os.environ.get('DYNAMODB_PRODUCTS_TABLE'))
ad_id_counter = 1


# Define a function named send_message which takes two arguments: event and context
def send_message(event, context):
    # Try to execute the following code block
    try:

        # Extract the chat_id from the pathParameters in the event object, if not found, set it to None
        chat_id = event.get('pathParameters', {}).get('chat_id')

        # Load the JSON data from the body of the event, if no body present, set it to an empty dictionary
        message = json.loads(event['body'])

        # Put a new item into the messages_table with the provided chat_id, timestamp, user_id, and text
        messages_table.put_item(
            Item={
                'chat_id': chat_id,
                'ts': datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
                'user_id': message['user_id'],
                'text': message['text']
            }
        )

        # Construct a body dictionary indicating a successful creation (status code 201)
        body = {
            "status": 201, # 201 means the request has succeeded and has led to the creation of a resource
            "title": "OK",
            "detail": f"New message posted into chat {message['user_id']}",
        }

        # Return a dictionary containing the statusCode 201 and the body containing JSON serialized body dictionary
        return {
            'statusCode': 201,
            'body': json.dumps(body)
        }
    
    # If an exception occurs, return a dictionary containing a 500 status code (Internal Server Error) and an error message
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


# Define a function named get_messages which takes two arguments: event and context
def get_messages(event, context):

    try:
        # Extract the chat_id from the pathParameters in the event object, if not found, set it to None
        chat_id = event.get('pathParameters', {}).get('chat_id')

        # Query the messages_table using the chat_id as a KeyConditionExpression
        messages = messages_table.query(KeyConditionExpression=Key('chat_id').eq(chat_id))

        # Check if the messages dictionary has items
        if len(messages["Items"]) > 0:
            # Construct a body dictionary containing status code 200 and a list of messages
            body = {
                "status": 200,
                'messages': [ {'ts': x['ts'], 'user_id': x['user_id'], 'text': x['text'], 'chat_id': x['chat_id']} for x in messages["Items"] ]
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
        return response

    except Exception as e:
        return {
            'statusCode': 500,  # Internal Server Error
            'body': json.dumps({'error': str(e)})
        }


def send_ad(event, context):
    global ad_id_counter
    try:
        # Load the JSON data from the body of the event
        body = json.loads(event['body'])

        # Put a new item into the ads_table
        ads_table.put_item(
            Item={
                'ad_id': str(ad_id_counter),
                'ts': datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
                'user_id': body['user_id'],
                'product_title': body['product_title'],
                'product_description': body['product_description'],
                'product_prize': body['product_prize']
            }
        )
        ad_id_counter+=1

        # Construct a body dictionary indicating a successful creation (status code 201)
        body = {
            "status": 201,
            "title": "OK",
            "detail": f"New ad posted into for user {body['user_id']}",
        }

        # Return statusCode 201 and the body containing JSON serialized body dictionary
        return {
            'statusCode': 201,
            'body': json.dumps(body)
        }

    # If an exception occurs, 500 status code (Internal Server Error)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def get_ads(event, context):
    try:
        # Perform a scan operation on the 'ads_table' DynamoDB table
        # A single Scan only returns a result set that fits within the 1 MB size limit according to
        # https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Scan.html
        # To fix this, the below while code is added according to
        # https://stackoverflow.com/questions/36780856/complete-scan-of-dynamodb-with-boto3
        response = ads_table.scan()  # Will only get up to 1 MB
        ads_data = response.get('Items', [])
        
        while 'LastEvaluatedKey' in response:  # If there're more itemss, continue scaning
            response = ads_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            ads_data.extend(response['Items']) # Extend with the 'Items' retrieved
        
        if len(ads_data) > 0:

            # Construct a body dictionary containing status code 200 and a list of ads
            body = {
                "status": 200,
                'ads': [ {'ad_id': x['ad_id'], 'ts': x['ts'], 'user_id': x['user_id'], 'product_title': x['product_title'], 'product_description': x['product_description'], 'product_prize': x['product_prize']} for x in ads_data ]
            }

            response = {
                'statusCode': 200,
                'body': json.dumps(body)
            }

        else: # If no ads found, construct a body dictionary for 404 error
            body = {
                "status": 404,
                "title": "Ads not found",
                "detail": "Ads not found in database"
            }
            
            response = {
                "statusCode": 404,
                "body": json.dumps(body)
            }
        return response
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }



def get_ad(event, context):
    try:
        # Extract the ad_id from the pathParameters in the event object, if not found, set it to None
        ad_id = event.get('pathParameters', {}).get('ad_id')

        # Query the ads_table using the ad_id as a KeyConditionExpression
        ad = ads_table.query(KeyConditionExpression=Key('ad_id').eq(ad_id))

        # Check if the ad dictionary has items
        if len(ad["Items"]) > 0:
            # Construct a body dictionary containing status code 200 and ad info
            body = {
                "status": 200,
                'ad': ad["Items"][0]
            }
            # Construct a response dictionary with statusCode 200 and the body containing JSON serialized body dictionary
            response = {
                "statusCode": 200,
                "body": json.dumps(body)
            }


        else: # If no ad found, construct a body dictionary for 404 error
            body = {
                "status": 404,
                "title": "Ad not found",
                "detail": f"Ad {ad_id} not found in database"
            }
            
            response = {
                "statusCode": 404,
                "body": json.dumps(body)
            }
        return response
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def delete_ad(event, context):
    try:
        # Extract the ad_id from the pathParameters in the event object, if not found, set it to None
        ad_id = event.get('pathParameters', {}).get('ad_id')

        # Query the ads_table using the ad_id as a KeyConditionExpression
        ad = ads_table.query(KeyConditionExpression=Key('ad_id').eq(ad_id))

        # Check if the ad dictionary has items, to see if ad exists
        if len(ad["Items"]) > 0:

            # Deletes the ad with ad_id
            ads_table.delete_item(Key={'ad_id': str(ad_id)})

            # Construct a body dictionary containing status code 200
            body = {
                "status": 200,
                'body': f"Ad # {ad_id} successfully deleted."
            }

            # Return a dictionary with statusCode 200 and the body containing JSON serialized body dictionary
            response = {
                "statusCode": 200,
                "body": json.dumps(body)
            }
        else: # if the dictionary is empty, means that ad_id does not exist, therefore no deletion
            body = {
                "status": 404,
                "title": "Ad not found",
                "detail": f"Ad {ad_id} not found in database"
            }
            
            response = {
                "statusCode": 404,
                "body": json.dumps(body)
            }
        return response

    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
