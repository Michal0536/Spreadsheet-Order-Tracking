import requests

def DHL_TRACKING(trackingNO):
    url = "https://api-eu.dhl.com/track/shipments"

    querystring = {"trackingNumber":trackingNO}
    headers = {"DHL-API-Key": "BQR15QTSjey8N4LyJ5viCE1agdatREPX"}

    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code != 200:
        headers = {"DHL-API-Key": "OsIyVM2GI9Z4oCL3lX6sRYfpZmMRCZY5"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        
    return response.json()['shipments'][0]['status']['statusCode']


print(DHL_TRACKING('3SZAL026162052'))