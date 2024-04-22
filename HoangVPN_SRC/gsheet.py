import gspread
from google.oauth2.service_account import Credentials
import os

os.chdir(os.path.dirname(__file__))

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file("api.json", scopes=scope)
client = gspread.authorize(creds)


spreadsheet = client.open('VPN INSTALLED DEVICE')
sheet_server = spreadsheet.worksheet("server")
sheet = spreadsheet.sheet1 

def push_data_to_gsheet(UUID, TOKEN_REGISTER, TUNNEL_ID, PUBLIC_IP, VPN_CONFIG, API_KEY):
    row = [UUID, TOKEN_REGISTER, TUNNEL_ID, PUBLIC_IP, VPN_CONFIG, API_KEY]
    sheet.append_row(row)
    
    for i, row in enumerate(sheet_server.get_all_values()[1:]):
        if row[1] == API_KEY:
            current_value = int(row[2])
            new_value = current_value + 1
            sheet_server.update_cell(i + 2, 3, str(new_value))
            break
    
def get_api_and_secret_key():
    for row in sheet_server.get_all_values()[1:]:
        api_server, secret_key, machine_used = row[0:3]
        if int(machine_used) < 100:
            return api_server.strip(), secret_key.strip(), machine_used.strip()
    return None, None, None