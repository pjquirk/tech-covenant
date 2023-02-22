from __future__ import print_function

import os.path
import csv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata']

def auth():
    """Gets credentials to use with the client.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def fixFilenames(files):
    creds = auth()

    try:
        service = build('drive', 'v3', credentials=creds)

        for hood, files in files.items():
            print(f'Fixing {hood}')
            fixFilename(service, hood, files)
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')

def fixFilename(service, hood, files):
    i = 0
    # Update metadata
    for url in files:
        i += 1
        filename = hood + ' ' + str(i)
        fileId = url.replace('https://drive.google.com/open?id=', '')
        if (len(fileId) == 0):
            print(f'Skipping url {url}')
            continue;

        print(f'Fixing {fileId} to be {filename}')
        service.files().update(
            fileId=fileId,
            body={
                'name': filename
            }
        ).execute()

    # results = service.files().get(
    #     pageSize=10, fields="nextPageToken, files(id, name)").execute()
    # items = results.get('files', [])

def readFilenames():
    # Read the CSV file and get the two columns
    reader = csv.reader(open('data.csv', 'r'))
    next(reader, None)  # skip the headers

    files = list(map(lambda row: (row[1], list(map(lambda url: url.strip(), row[2].split(',')))),
          filter(lambda row: row[2] != '', reader)))

    # merge duplicate keys
    merged_files = {}
    for file in files:
        if file[0] in merged_files:
            merged_files[file[0]] += file[1]
        else:
            merged_files[file[0]] = file[1]

    return merged_files

def main():
    files = readFilenames()
    fixFilenames(files)

if __name__ == '__main__':
    main()