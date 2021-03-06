import os
from erg_data_recog import get_erg_data
from update_google_sheets import update_google_sheets
from preprocessing import preprocessing

preprocessing()
whatsapp_download_folder= 'output'
for filename in os.listdir(whatsapp_download_folder):
    if filename.endswith(".jpg"):
        try:
            date, user, _ = filename.replace('.jpg','').split('-')
            erg_data = get_erg_data(filename, whatsapp_download_folder)
            erg_data = [item for sublist in [[date,'Erg'],erg_data] for item in sublist]
            update_google_sheets(erg_data, user)
        except:
            print(f"{filename} was shite quality")
            pass