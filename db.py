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

#================================= TO GET TOKEN ==============================================================================

try:
    with open("rs.token", "r") as file:
        token = file.read()
        print(" Current token:", token)
except Exception as file_exception:
    with open("rs.token", "w") as file:
        token = get_token(auth_server_url, clientId, clientSecret, open_itemId, open_itemType)
        file.write(str(token))

status_code, introspect_result = introspect_token(auth_server_url, token)
print("\n Token status code:", status_code)
if status_code == 401:
    try:
        with open("rs.token", "w") as file:
            token = get_token(auth_server_url, clientId, clientSecret, open_itemId, open_itemType)
            file.write(str(token))
    except Exception as token_expired:
        pass
else:
    pass

#================================== TO GET LATEST DATA ==========================================================================
print("Latest Data")
status_code, latest_data = get_latest_data(resource_server_url, aqm_resource_id, token)
latest_data_json = json.loads(latest_data)
print("\n Latest data of " + aqm_resource_id + ":")
print(json.dumps(latest_data_json, indent=4))

#================================== TO GET TEMPORAL DATA ==========================================================================
"""
    options = [str] The value should be equal to count and it is case sensitive {optional}

"""



uri = "mongodb+srv://sai:sai@cluster0.muh1mrb.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Access the "test" database and "api_responses" collection
db = client.test
collection = db.api_responses

# Insert the API response as a new document
response_document = {
    "type": "latest_data",
    "resource_id": aqm_resource_id,
    "response": latest_data_json
}

insert_result = collection.insert_one(response_document)
print("Inserted response document ID:", insert_result.inserted_id)
