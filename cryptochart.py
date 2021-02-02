#https://api.coindesk.com/v1/bpi/currentprice.json

import requests as requ
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime 
import time

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'keys.json'
SPREADSHEET_ID = '13Z9ZHNa2aa_EXu11cEeiKCwtjs8HROUtJ4CfQkY-D_o'

credentials = None
credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('sheets', 'v4', credentials=credentials)

sheet = service.spreadsheets()

global row
row = 4
global date
date = datetime.date.today()

apikey = #enter public api key
secretkey = #enter private key

def req():
    global row
    global date
    #requests price
    r = requ.get('https://api.coindesk.com/v1/bpi/currentprice.json', auth=('user','pass'))
    i = json.loads(r.text)
    price = i['bpi']['USD']['rate_float']
    
    #gets values of high and low    
    d = sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=f'A{row}').execute()
    hl = sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=f'E{row}:F{row}').execute()
    #processes .get()s
    highslows = hl.get('values', [])
    dates = d.get('values', [])
    #used to compare cells to current price
    highcell = float(highslows[0][0])
    lowcell = float(highslows[0][1])

    #retarded google formating shit
    priceL = [[price]]
    Jprice = {"values":priceL}
    
    diffL = [[highcell - lowcell]]
    Jdiff = {"values":diffL}
    #updates
    he = sheet.values().update(spreadsheetId=SPREADSHEET_ID,range=f'E{row}',valueInputOption='USER_ENTERED',body=Jprice)
    le = sheet.values().update(spreadsheetId=SPREADSHEET_ID,range=f'F{row}',valueInputOption='USER_ENTERED',body=Jprice)
    diff = sheet.values().update(spreadsheetId=SPREADSHEET_ID,range=f'G{row}',valueInputOption='USER_ENTERED',body=Jdiff).execute()

    if price>=highcell:
        he.execute()
    if price<=lowcell:
        le.execute()
    if datetime.date.today() != date:
        date = datetime.date.today()
        he.execute()
        le.execute()
        row+=1   
    if highcell == 0 or lowcell == 0:
        he.execute()
        le.execute()
def balance(a,s):
    r = requ.get('https://fapi.binance.com/fapi/v2/balance', auth=(a,s))
    print(r)

while(True):
    time.sleep(10)
    balance(apikey, secretkey)
    req()
