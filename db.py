import time
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from iudx_api_functions import *
import requests
import json
import os

#================================== DECLARE VARIABLES ==============================================================================

resource_server_url = "https://iudx-rs-onem2m.iiit.ac.in/"
auth_server_url = "https://authorization.iudx.org.in"
clientId = 'eb061f48-33ba-4dae-ae3c-d271c464e5ce'
clientSecret = '68848025e7a8c147490115b5f716b09a69cc24dd'
open_itemId = "iudx-rs-onem2m.iiit.ac.in"
open_itemType = "resource_server"
aqm_version_id = "research.iiit.ac.in/4786f10afbf48ed5c8c7be9b4d38b33ca16c1d9a/iudx-rs-onem2m.iiit.ac.in/iiith-env-aqm-version/version-info"
deviceID = "WE-VN04-00"
aqm_resource_id = "research.iiit.ac.in/4786f10afbf48ed5c8c7be9b4d38b33ca16c1d9a/iudx-rs-onem2m.iiit.ac.in/iiith-env-weather/WE-VN04-00"

# MongoDB Connection
uri = "mongodb+srv://sai:sai@cluster0.muh1mrb.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.test
collection = db.api_responses

#================================= TO GET TOKEN ==============================================================================

def get_updated_token():
    try:
        with open("rs.token", "r") as file:
            token = file.read()
        return token
    except Exception as file_exception:
        token = get_token(auth_server_url, clientId, clientSecret, open_itemId, open_itemType)
        with open("rs.token", "w") as file:
            file.write(str(token))
        return token

# Main Loop
while True:
    token = get_updated_token()

    status_code, introspect_result = introspect_token(auth_server_url, token)
    print("\n Token status code:", status_code)

    if status_code == 401:
        token = get_updated_token()

    print("Latest Data")
    status_code, latest_data = get_latest_data(resource_server_url, aqm_resource_id, token)
    latest_data_json = json.loads(latest_data)
    print("\n Latest data of " + aqm_resource_id + ":")
    print(json.dumps(latest_data_json, indent=4))

    # Insert the API response as a new document
    response_document = {
        "type": "latest_data",
        "resource_id": aqm_resource_id,
        "response": latest_data_json,
        "timestamp": datetime.now()
    }

    insert_result = collection.insert_one(response_document)
    print("Inserted response document ID:", insert_result.inserted_id)

    # Sleep for 30 minutes
    time.sleep(30 * 60)  # 30 minutes in seconds
