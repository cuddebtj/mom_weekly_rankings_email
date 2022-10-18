import yaml
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError



import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

G_OAUTH_CLIENT = list(Path().cwd().glob("**/client-secret.json"))[0]
CREDS_PATH = list(Path().cwd().glob("**/google-credentials.yaml"))[0]
PRIVATE_YAML = list(Path().cwd().glob("**/private.yaml"))[0]

with open(PRIVATE_YAML) as file:
    private = yaml.load(file, Loader=yaml.SafeLoader)

emails = private['email_list']
creds = None

SCOPES = ['https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.modify']

if CREDS_PATH.is_file():
    creds = Credentials.from_authorized_user_file(CREDS_PATH, SCOPES)

if not creds and not creds.valid:
    if creds and creds.expired and creds.refresh_token:
            creds.refresn(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(G_OAUTH_CLIENT, SCOPES)
    with open(CREDS_PATH, 'w') as token:
        yaml.dump(creds, token)

try:
    service = build('gmail', 'v1', credentials=creds)

    my_email = 'menofmadisonffble@gmail.com'
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'MoM FFBL Weekly Rankings'
    msg['From'] = f'{my_email}'
    msg['To'] = f'cuddebtj@gmail.com'
    msgPlain = 'This is my first email!'
    msgHtml = '<b>This is my first email!</b>'
    msg.attach(MIMEText(msgPlain, 'plain'))
    msg.attach(MIMEText(msgHtml, 'html'))
    raw = base64.urlsafe_b64encode(msg.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}

    message1 = body
    message = (
        service.users().messages().send(
            userId="me", body=message1).execute())
    print('Message Id: %s' % message['id'])

except HttpError as error:
    print(f'An error occurred: {error}')

