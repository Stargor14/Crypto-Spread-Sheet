#https://api.coindesk.com/v1/bpi/currentprice.json

#nicehash
#9c218054-23c1-483d-a8d0-6ef99a0d99bf
#ba8c1aa5-e76a-48a5-bc9e-c2b1080ec38ab22678ca-2634-40ed-94af-ac29be8331bc
import json
import time
import datetime 
import requests as requ
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from binance.client import Client
import nicehash

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'keys.json'
SPREADSHEET_ID = '13Z9ZHNa2aa_EXu11cEeiKCwtjs8HROUtJ4CfQkY-D_o'

credentials = None
credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('sheets', 'v4', credentials=credentials)

sheet = service.spreadsheets()

global row
row = 7
global date
date = datetime.date.today()
#binance keys
apikey = "x15G8QtfrUCJG1F7tCahCwyCwxE7a3Mbykg8Q4Uf0Q7QKjB1B3GvCYkfzRUTS96e"
secretkey = "YyATCoS7OwFFAdaqK3UCw0zZLZoz6RWRqarMrHhGi7P08c7Muay8zDWZfV86SxA5"
#nicehash keys and declarations
niceapikey = '9c218054-23c1-483d-a8d0-6ef99a0d99bf'
nicesecretkey = 'ba8c1aa5-e76a-48a5-bc9e-c2b1080ec38ab22678ca-2634-40ed-94af-ac29be8331bc'

host = 'https://api2.nicehash.com'

private_api = nicehash.private_api(host, '', niceapikey, nicesecretkey, True)
btcbalance = private_api.get_accounts_for_currency('BTC')['totalBalance']

global fbalance
client = Client(apikey, secretkey)
fbalance = client.futures_account_balance()[0]['balance']
#use historical trade data, write to sheet and calculate average pNl per trade, maybe median? some kind of averadgeing. weighted average? 

def req(client,priv):
    global row
    global date
    global fbalance
    #requests price
    r = requ.get('https://api.coindesk.com/v1/bpi/currentprice.json', auth=('user','pass'))
    i = json.loads(r.text)
    price = i['bpi']['USD']['rate_float']
    fbalance = client.futures_account_balance()[0]['balance']

    #gets values of high and low    
    d = sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=f'A{row}').execute()
    hl = sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=f'E{row}:F{row}').execute()
    #processes .get()s
    highslows = hl.get('values', [])
    dates = d.get('values', [])
    #used to compare cells to current price
    highcell = float(highslows[0][0])
    lowcell = float(highslows[0][1])
    diffp = ((highcell/lowcell)-1)*100
    #retarded google formating shit
    priceL = [[price]]
    Jprice = {"values":priceL}
    
    diffL = [[highcell - lowcell]]
    Jdiff = {"values":diffL}

    fbalanceL = [[fbalance]]
    Jfbalance = {"values":fbalanceL}

    diffpL = [[diffp]]
    Jdiffp = {"values":diffpL}
    #updates
    he = sheet.values().update(spreadsheetId=SPREADSHEET_ID,range=f'E{row}',valueInputOption='USER_ENTERED',body=Jprice)
    le = sheet.values().update(spreadsheetId=SPREADSHEET_ID,range=f'F{row}',valueInputOption='USER_ENTERED',body=Jprice)
    diff = sheet.values().update(spreadsheetId=SPREADSHEET_ID,range=f'G{row}',valueInputOption='USER_ENTERED',body=Jdiff).execute()
    fb = sheet.values().update(spreadsheetId=SPREADSHEET_ID,range=f'B{row}',valueInputOption='USER_ENTERED',body=Jfbalance).execute()
    dp = sheet.values().update(spreadsheetId=SPREADSHEET_ID,range=f'H{row}',valueInputOption='USER_ENTERED',body=Jdiffp).execute()
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

while(True):
    time.sleep(3)
    req(client,private_api)
