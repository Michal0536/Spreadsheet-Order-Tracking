import requests
import json

def fetch_API_keys():
    with open('settings.json', 'r') as file:
        data = json.load(file)
    
    APIs = data['API_DHL']    
    return APIs

def DHL_TRACKING(trackingNO):
    url = "https://api-eu.dhl.com/track/shipments"
    APIs = fetch_API_keys()
    querystring = {"trackingNumber":trackingNO}
    headers = {"DHL-API-Key": APIs[0]}

    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code != 200:
        headers = {"DHL-API-Key": APIs[1]}
        response = requests.request("GET", url, headers=headers, params=querystring)
        
    return response.json()['shipments'][0]['status']['statusCode']
