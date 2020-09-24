import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('traininglog-1600859902029-087c22a24196.json', scope)
client = gspread.authorize(creds)
sheet = client.open('Commercial Training Log 20/21')


def update_google_sheets(workout_data, user):
    
    try:
        worksheet = sheet.worksheet(user)
        dataframe = pd.DataFrame(worksheet.get_all_records())
        workout_data = pd.DataFrame([workout_data], columns=dataframe.columns)
        updated_dataframe = dataframe.append(workout_data)
        worksheet.update([updated_dataframe.columns.values.tolist()] + updated_dataframe.values.tolist())
    
    except gspread.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=user, rows="1000", cols="20")
        workout_data = pd.DataFrame([workout_data], columns=['Date','Type','Distance','Duration','Split','Rate'])
        worksheet.update([workout_data.columns.values.tolist()] + workout_data.values.tolist())
        worksheet.format('A1:F1000', {'horizontalAlignment':'LEFT'})
        worksheet.format('A1:F1', {'textFormat': {'bold': True}})
        
