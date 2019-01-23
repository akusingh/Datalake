import requests
import boto3
import pandas as pd
from io import StringIO
import os
import zipfile

#URL = "https://www.dropbox.com/s/29b85ihtoysmveu/DFV-Daily-Weather-2017.tsv
# ?raw=1"

#API call settings for Dropbox.

def downloadData(URL, api_token=""):
    try:
        url_header = {'Authorization': 'No Auth'}
        response = requests.get(url=URL, headers=url_header)
        if int(response.status_code) == 200:
            return response
        else:
            raise Exception("Response failure : " + str(
                response.status_code) + " for URL : " + str(URL))
            return None
    except Exception as e:
        print "Exception generated while downloading data from URL " + URL
        print "Exception is " + str(e)
        notification['Message'] = str(e)
        notification['Notification Type'] = "DataSourceNotAccessible"
        notification['Notification Time'] = time.strftime('%d-%m-%Y %H:%M',
                                                          time.localtime(int(
                                                              get_current_date_time_in_millisec())))
        return None

#Upload response from EC2 to S3 bucket.

def upload_data_to_s3(s3_bucket, path, response):
    try:
        s3 = boto3.resource('s3')
        s3.Object(s3_bucket, path).put(Body=response)
    except Exception as e:
        print "Failed while uploading file {}".format(path)
        print e
    return



def upload_file_s3(local_file_path, s3_file_name, bucket_name):
    s3 = boto3.client('s3')
    with open(local_file_path, 'rb') as data:
        s3.upload_fileobj(data, bucket_name, s3_file_name)

#wget to download files from S3

def execute_wget_command(s3_url):
    os.system('wget {}'.format(s3_url))
    return

#Unzipping file.

def unzip_files_to_a_folder(source_file, location_to_unzip):
    zip_ref = zipfile.ZipFile(source_file, 'r')
    zip_ref.extractall(location_to_unzip)
    zip_ref.close()
    return

def list_files_in_a_folder(folder_path):
    files = os.listdir(folder_path)
    return files

#Arguments

def main(*args):
    # argument values
    api_url = args[0]
    bucket_name = args[1]
    s3_path = args[2]
    s3_url = args[3]
    criminal_s3_path = args[4]
    response = downloadData(api_url)
    response_text = response.text
    if response is None:
        return
    # Upload data to s3
    #pandas
    buffer_data = StringIO(response_text)
    df = pd.read_csv(buffer_data, sep='\t')
    df_csv = df.to_csv(sep=',', index=False)
    upload_data_to_s3(bucket_name, s3_path, df_csv)

    # Process S3 Data
    execute_wget_command(s3_url)
    unzip_files_to_a_folder('TX-2017.zip',
                            '/home/ubuntu/Data/TX_Data/')
    extracted_files = list_files_in_a_folder(
        '/home/ubuntu/ubuntu/Data/TX_Data/TX/')
    for file in extracted_files:
        upload_file_s3('{}/{}'.format('/home/ubuntu/ubuntu/Data/TX_Data/TX/',file), '{}{}'.format(criminal_s3_path,
                                                        file), bucket_name)
    return
