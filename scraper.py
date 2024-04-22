import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import base64
from datetime import datetime
from colorama import Style,Fore,init
import threading
import time

lock = threading.Lock()

init(convert=True)
init(autoreset=True)

from DHL import DHL_TRACKING
from PostNL import PostNL_tracking


def log(content):
    with lock:
        print(f'[{datetime.now()}] {Fore.LIGHTBLUE_EX}{content}{Style.RESET_ALL}')
def log_success(content):
    with lock:
        print(f'[{datetime.now()}] {Fore.LIGHTGREEN_EX}{content}{Style.RESET_ALL}')
def log_error(content):
    with lock:
        print(f'[{datetime.now()}] {Fore.LIGHTRED_EX}{content}{Style.RESET_ALL}')   

import json

def save_status_to_json(orderNO, tracking, status):
    data = {
        "orderNO": orderNO,
        "tracking": tracking,
        "status": status,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        
        with open('shipment_status.json', 'r') as file:
            status_list = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        status_list = []

    status_list.append(data)

    with open('shipment_status.json', 'w') as file:
        json.dump(status_list, file, indent=4)

    log_success(f"Saved status for {orderNO} to JSON")

def get_order_status_from_json(orderNO):
    try:
        with open('shipment_status.json', 'r') as file:
            status_list = json.load(file)

        for status_entry in status_list:
            if status_entry['orderNO'] == orderNO:
                return status_entry['status']
        
        return None

    except FileNotFoundError:
        return None

    except json.JSONDecodeError:
        return None


def create_buildSheets():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = None
    if os.path.exists('tokenSheet.json'):
        creds = Credentials.from_authorized_user_file('tokenSheet.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('tokenSheet.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    return service

def get_all_sheets(service, spreadsheet_id):
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get('sheets', '')
    return [sheet['properties']['title'] for sheet in sheets]

def fetch_spreadsheets():
    with open('settings.json', 'r') as file:
        data = json.load(file)
    
    spreadsheet_ids = data['spreadsheets_id']    
    return spreadsheet_ids


def scrap_spreadsheet():
    service = create_buildSheets()
    spreadsheet_ids = fetch_spreadsheets()
    
    for SPREADSHEET_ID in spreadsheet_ids:
        if 'WWkUxnOH6Ks' in SPREADSHEET_ID:
            all_sheets = ['ZAMÓWIENIA NAOS']
        else:
            all_sheets = get_all_sheets(service,SPREADSHEET_ID)

        for RANGE_NAME in all_sheets:
            log(f"Now checking {RANGE_NAME}")
            # RANGE_NAME = f"{RANGE_NAME}!A:S"
            result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,range=RANGE_NAME).execute()
            rows = result.get('values')

            if not rows:
                continue

            header = rows[0]
            try:
                order_col = header.index('ORDER NUMBER')
                tracking_col = header.index('TRACKING')
                status_col = header.index('STATUS TRACKINGU (SKRYPT PODŁĄCZONY)')
              
                for row in rows[1:]:
                    try:
                        ORDERNO = row[order_col]
                        if ORDERNO != "" or ORDERNO is None:
                            if row[status_col] != "Shipment delivered" or row[status_col] != 'delivered':
                                log(f'Looking for {ORDERNO}')

                                try:
                                    nrpaczki = look_for_email(ORDERNO) 
                                except:
                                    nrpaczki = None

                                if nrpaczki != None:
                                    try:
                                        status = PostNL_tracking(nrpaczki)
                                        if status == 'Package not found':
                                            status = DHL_TRACKING(nrpaczki)
                                    except:
                                        status = 'N/A'

                                    if status is not None and status != 'N/A':
                                        log_success(f"{ORDERNO} - {status}")
                                        update_status(ORDERNO, nrpaczki, status, RANGE_NAME,SPREADSHEET_ID)
                                        save_status_to_json(ORDERNO, nrpaczki, status)
                                    else:
                                        try:
                                            status = get_order_status_from_json(ORDERNO)
                                        except:
                                            status = 'not shipped'
                                        update_status(ORDERNO, nrpaczki, status, RANGE_NAME,SPREADSHEET_ID)
                                        log_error(f"Invalid status for {ORDERNO}. Updated with previous one.")
                    except Exception as E:
                        log_error(str(E))
                        continue

            except ValueError:
                log_error('No orders found')
                continue
            except Exception as e:
                log_error(str(e))
                continue

def create_build():
    SCOPES = ['https://mail.google.com/']
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    return service

def look_for_email(orderNO):
    service = create_build()
    results = service.users().messages().list(userId='me', q=orderNO).execute()
    messages = results.get('messages', [])

    if not messages:
        # log_error(f'Cannot find email with tracking for {orderNO}')
        return
    else:
        for message in messages:
            try:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                payload = msg['payload']
                headers = payload['headers']

                for d in headers:
                    if d['name'] == 'Subject':
                        subject = d['value']
                    if d['name'] == 'From':
                        sender = d['value']

                parts = payload.get('parts')[0]
                # print(parts)
                data = parts['body']['data']
                data = data.replace("-","+").replace("_","/")
                decoded_data1 = base64.b64decode(data)
                decoded_data = decoded_data1.decode('utf-8')
                if 'Jouw Zalando-team' in decoded_data:
                    if 'Je track-and-tracecode:' in decoded_data:
                        nrpaczki = decoded_data.split('Je track-and-tracecode:')[1].split('Volg je pakket')[0].replace('\n','').replace(' ','').replace('\r','')
                        try:
                            nrzamowienia = decoded_data.split('gecombineerd uit je bestellingen')[1].split('Dat betekent')[0].replace('.','').split('<')[0].replace('\n','')
                        except:
                            nrzamowienia = decoded_data.split('Bestelnummer')[1].split('<')[0].replace('\n','').replace(' ','').replace('\r','')

                        log_success(f'Email found for {nrzamowienia} - {nrpaczki}')
                        return nrpaczki
                    
            except Exception as er:
                time.sleep(1)
                if 'data' not in str(er):
                    print(er)
                    continue


def update_status(orderNO, tracking, Status,RANGE_NAME,SPREADSHEET_ID):
    if Status is None:
        Status = 'N/A'

    service = create_buildSheets()


    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    header = values[0]
    try:
        order_col = header.index('ORDER NUMBER')  
        tracking_col = header.index('TRACKING')  
        status_col = header.index('STATUS TRACKINGU (SKRYPT PODŁĄCZONY)')  
    except ValueError as e:
        print(f"Column not found: {e}")
        return
    
        
    def column_letter(col_index):
        col = ""
        while col_index > 0:
            col_index, remainder = divmod(col_index - 1, 26)
            col = chr(65 + remainder) + col
        return col

    tracking_col_letter = column_letter(tracking_col + 1)
    status_col_letter = column_letter(status_col + 1)

    for i, row in enumerate(values):
        if orderNO in row[order_col]: 
            tracking_range = f"{RANGE_NAME}!{tracking_col_letter}{i+1}"
            tracking_body = {
                'values': [[tracking]]
            }
            service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range=tracking_range,
                                                    valueInputOption='USER_ENTERED', body=tracking_body).execute()

            
            status_range = f"{RANGE_NAME}!{status_col_letter}{i+1}"
            status_body = {
                'values': [[Status]]
            }
            service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range=status_range,
                                                    valueInputOption='USER_ENTERED', body=status_body).execute()

            print('Updated Row:', i+1)
            break  


while True:
    scrap_spreadsheet()
    time.sleep(3600)