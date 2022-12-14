# Import the necessary modules
import os
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Set the credentials file path and the name of the sheet to be deleted
credentials_file_path = 'path/to/credentials.json'
sheet_name = 'Sheet1'

# Set the Google Drive directory ID
directory_id = 'abc123'

# Load the credentials from the JSON file
credentials = service_account.Credentials.from_service_account_file(
    credentials_file_path, scopes=['https://www.googleapis.com/auth/drive']
)

# Make sure the credentials are valid and authorized
credentials.refresh(Request())

# Build the Drive API client
drive_service = build('drive', 'v3', credentials=credentials)

# Get a list of all files in the specified Google Drive directory
results = drive_service.files().list(
    q=f"'{directory_id}' in parents", fields='nextPageToken, files(id, name)'
).execute()

# Get the list of files from the results
files = results.get('files', [])

# Loop through the files
for file in files:
  # Check if the file is a Google Sheets
  if file['name'].endswith('.gsheet'):
    # Get the file ID and name
    file_id = file['id']
    file_name = file['name']

    # Build the Sheets API client
    sheets_service = build('sheets', 'v4', credentials=credentials)

    # Get a list of sheets in the Google Sheets file
    sheets = sheets_service.spreadsheets().get(spreadsheetId=file_id).execute()

    # Loop through the sheets
    for sheet in sheets['sheets']:
      # Check if the sheet name matches the sheet to be deleted
      if sheet['properties']['title'] == sheet_name:
        # Delete the sheet
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=file_id,
            body={
                'requests': [
                    {
                        'deleteSheet': {
                            'sheetId': sheet['properties']['sheetId']
                        }
                    }
                ]
            }
        ).execute()

        # Print a message
        print(f'Deleted sheet "{sheet_name}" from Google Sheets "{file_name}".')
