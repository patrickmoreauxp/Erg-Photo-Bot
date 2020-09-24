import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError
import io
import re
import distance
from PIL import Image, ImageDraw, ImageFont


ACCESS_KEY = pd.read_csv('rootkey.csv', header= None)[0][0].split('AWSAccessKeyId=')[1]
SECRET_KEY = pd.read_csv('rootkey.csv', header= None)[0][1].split('AWSSecretKey=')[1]
BUCKET_NAME = 'whatsapp-data-bucket'


def retrieve_image_data(file_name, bucket_name, aws_access_key_id, aws_secret_access_key, region_name='eu-west-1'):

    s3_connection = boto3.resource('s3', aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key)

    s3_object = s3_connection.Object(bucket_name, file_name)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image=Image.open(stream)
    client = boto3.client('textract', region_name=region_name, aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key)

    image_binary = stream.getvalue()
    response = client.analyze_document(Document={'Bytes': image_binary},
        FeatureTypes=["TABLES", "FORMS"])
    
    return response


def parse_erg_data(response):
    erg_string = ''
    for block in response['Blocks']:
        if block['BlockType'] == 'LINE':
            erg_string+=(block['Text'])+" "
    # Remove small words from the string
    re_shortwords = re.compile('(?<=\s)[A-Za-z]{1,3}(?=\s)')
    processed_erg_string = re_shortwords.sub('', erg_string)
    # Don't return data in the top part of screen. Returning everything after the lowercase word that looks like'time'
    word_lev_distances = [(word,distance.levenshtein(word,'time')) for word in processed_erg_string.split()]
    best_time_word = sorted(word_lev_distances, key=lambda tup: tup[1])[0][0]
    return erg_string.split(best_time_word)[1] 


def get_time_dist_rate(erg_data):
    # Defining reg expressions
    re_time_split = re.compile("""((\d+[:;'`,.]\d)+)""")
    re_dist = re.compile("""((?<=\s)(\d{3,})(?=\s))""")
    re_rate = re.compile("""((?<=\s)(\d\d)(?=\s))""")
    # Find instances of those reg expressions
    # Replace any common mistakes that the image reader may have made
    time = re.findall(re_time_split,erg_data)[0][0]
    # Once time is found, disregard things in the string before that. Time is first to appear on screen and so on.
    erg_data = erg_data.split(time)[1]
    distance = re.findall(re_dist,erg_data)[0][0]
    erg_data = erg_data.split(distance)[1]
    split = re.findall(re_time_split,erg_data)[0][0]
    erg_data = erg_data.split(split)[1]
    rate = re.findall(re_rate,erg_data)[0][0]
    # Clean time and split
    time = time.replace(';',':').replace(",",'.')
    split = split.replace(';',':').replace(",",'.')
    return [distance, time, split, rate]


def upload_to_s3(file_name, whatsapp_download_folder):
    file_path = whatsapp_download_folder+"/"+file_name
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)
    s3.upload_file(file_path, BUCKET_NAME, file_name)
    

def clean_up_file(file_name):
    s3 = boto3.resource("s3", aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)
    obj = s3.Object(BUCKET_NAME, file_name)
    obj.delete()


def get_erg_data(file_name, whatsapp_download_folder):
    upload_to_s3(file_name, whatsapp_download_folder)
    response = retrieve_image_data(file_name, BUCKET_NAME, ACCESS_KEY, SECRET_KEY, region_name='eu-west-1')
    parsed_data = parse_erg_data(response)
    clean_up_file(file_name)
    return get_time_dist_rate(parsed_data)