import boto3
import pandas as pd
import numpy as np
from StringIO import StringIO

#S3 operation
def get_s3_object(s3_key, bucket_name):
    client = boto3.client('s3')
    response = client.get_object(Key=s3_key, Bucket=bucket_name)
    return response


def get_keys_of_bucket(bucket_name, prefix_path=""):
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    keys = bucket.objects.filter(Prefix=prefix_path)
    return [key.key for key in keys if "." in key.key]


def write_buffer_to_s3(file_obj, bucket_name, s3_key):
    s3 = boto3.client('s3')
    s3.put_object(
        Body=file_obj,
        Bucket=bucket_name,
        Key=s3_key,
        ServerSideEncryption='AES256'
    )
    return

#Process definition for different types of file.
def process_1(s3_buffer):
    df = pd.read_csv(StringIO(s3_buffer)).rename(
        columns=lambda x: x.strip().replace('.', '_'))
    df.drop(0, inplace=True)
    columns = list(df.columns)
    for col in columns:
        df[col] = df[col].apply(
    lambda x: x.strip() if isinstance(x, str) else x).apply(
    lambda x: np.NaN if not x else x)
    df.fillna('missing_values')
    return df.to_csv(index=False, sep='|')


def process_2(s3_buffer):
    df = pd.read_csv(StringIO(s3_buffer)).rename(
        columns=lambda x: x.strip().replace('.', '_'))
    df.drop_duplicates(inplace=True)
    df.drop(0, inplace=True)
    columns = list(df.columns)
    for col in columns:
        df[col] = df[col].apply(
            lambda x: x.strip() if isinstance(x, str) else x).apply(
            lambda x: np.NaN if not x else x)
    return df.to_csv(index=False, sep='|')


def process_3(s3_buffer):
    df = pd.read_csv(StringIO(s3_buffer), sep=r',(?!\s)',
                     engine='python').rename(
        columns=lambda x: x.strip().replace('.', '_'))
    columns = list(df.columns)
    for col in columns:
        df[col] = df[col].apply(lambda x: x.replace(',','/'))
    df.drop(0, inplace=True)
    return df.to_csv(index=False, sep='|')

def process_4(s3_buffer):
    df = pd.read_csv(StringIO(s3_buffer)).rename(
        columns=lambda x: x.strip().replace('.', '_'))
    columns = list(df.columns)
    for col in columns:
        df[col] = df[col].apply(
    lambda x: x.strip() if isinstance(x, str) else x).apply(
    lambda x: np.NaN if not x else x)
    df.fillna(0.0)
    return df.to_csv(index=False, sep='|')

#File listing
def main(*args):
    """

    """
    s3_path = args[0]
    bucket_name = args[1]
    keys = get_keys_of_bucket(bucket_name, s3_path)
    key_mapping = {
        "NIBRS_AGE": "process_1",
        "NIBRS_ASSIGNMENT_TYPE": "process_1",
        "NIBRS_ARREST_TYPE": "process_1",
        "NIBRS_CIRCUMSTANCES": "process_1",
        "NIBRS_DRUG_MEASURE_TYPE": "process_1",
        "NIBRS_INJURY": "process_1",
        "NIBRS_ETHNICITY": "process_1",
        "NIBRS_LOCATION_TYPE": "process_1",
        "NIBRS_JUSTIFIABLE_FORCE": "process_1",
        "NIBRS_RELATIONSHIP": "process_1",
        "NIBRS_USING_LIST": "process_1",
        "NIBRS_SUSPECTED_DRUG_TYPE": "process_1",
        "NIBRS_WEAPON_TYPE": "process_1",
        "NIBRS_VICTIM_TYPE": "process_1",
        "REF_STATE": "process_1",
        "agency_participation": "process_1",
        "agencies": "process_1",
        "NIBRS_ARRESTEE_WEAPON": "process_2",
        "NIBRS_ARRESTEE": "process_2",
        "NIBRS_BIAS_MOTIVATION": "process_2",
        "NIBRS_CRIMINAL_ACT": "process_2",
        "NIBRS_incident": "process_2",
        "NIBRS_month": "process_2",
        "NIBRS_OFFENDER": "process_2",
        "NIBRS_OFFENSE": "process_2",
        "NIBRS_PROPERTY_DESC": "process_2",
        "NIBRS_PROPERTY": "process_2",
        "NIBRS_SUSPECT_USING": "process_2",
        "NIBRS_SUSPECTED_DRUG": "process_2",
        "NIBRS_VICTIM_CIRCUMSTANCES": "process_2",
        "NIBRS_VICTIM_INJURY": "process_2",
        "NIBRS_VICTIM_OFFENDER_REL": "process_2",
        "NIBRS_VICTIM_OFFENSE": "process_2",
        "NIBRS_VICTIM": "process_2",
        "NIBRS_WEAPON": "process_2",
        "NIBRS_ACTIVITY_TYPE": "process_3",
        "NIBRS_BIAS_LIST": "process_3",
        "NIBRS_CLEARED_EXCEPT": "process_3",
        "NIBRS_CRIMINAL_ACT_TYPE": "process_3",
        "NIBRS_PROP_LOSS_TYPE": "process_3",
        "NIBRS_PROP_DESC_TYPE": "process_3",
        "weather": "process_4"
    }

    for key in keys:
        try:
            key_name = key.split('/')[-1].split('.')[0]
            s3_obj = get_s3_object(key, bucket_name)['Body'].read()
            if key_mapping[key_name] == 'process_1':
                df_csv = process_1(s3_obj)
            if key_mapping[key_name] == 'process_2':
                df_csv = process_2(s3_obj)
            if key_mapping[key_name] == 'process_3':
                df_csv = process_3(s3_obj)
            if key_mapping[key_name] == 'process_4':
                df_csv = process_3(s3_obj)
            write_buffer_to_s3(df_csv, bucket_name, key.replace('raw',
                                                                'cleansed'))
        except Exception as e:
            print(e)
            continue
    return
