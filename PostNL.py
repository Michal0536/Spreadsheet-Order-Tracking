import requests
import random

def PostNL_tracking(tracking):
    try:
        post_code = '1323SG'


        headers = {
            'authority': 'jouw.postnl.nl',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
            'dnt': '1',
            'referer': f'https://jouw.postnl.nl/track-and-trace/{tracking}-NL-{post_code}',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Opera";v="91", "Chromium";v="105"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 OPR/91.0.4516.65',
        }

        params = {
            'language': 'en',
        }

        response = requests.get(f'https://jouw.postnl.nl/track-and-trace/api/trackAndTrace/{tracking}-NL-{post_code}', params=params, headers=headers)
        if response.status_code != 200:
            raise Exception
        else:
            # print(response.json())
            if response.json()['colli']:
                latest_status = response.json()['colli'][tracking]['statusPhase']['message']
                try:
                    delivery_date = response.json()['colli'][tracking]['deliveryDate']
                except ValueError:
                    delivery_date = "N/A"
                shippedDate = response.json()['colli'][tracking]['observations'][-1]['observationDate']

                return latest_status
            else:
                return "Package not found"
                # print(response.json())
    except Exception as ER:
        print(ER)
        pass
