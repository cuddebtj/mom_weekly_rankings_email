from __future__ import print_function
from googleapiclient.discovery import build
from apiclient import errors
from httplib2 import Http
from email.mime.text import MIMEText
import base64
from google.oauth2 import service_account

import base64
from email.message import EmailMessage

import base64
import mimetypes
import os
from email.message import EmailMessage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError



from pathlib import Path

# Email variables. Modify this!
EMAIL_FROM = 'cuddebtj@gmail.com'
EMAIL_TO = 'cuddebtj@gmail.com'
EMAIL_SUBJECT = 'Test'
EMAIL_CONTENT = 'Test'

def service_account_login():
  SCOPES = ['https://www.googleapis.com/auth/gmail.send']
  SERVICE_ACCOUNT_FILE = list(Path().cwd().glob("**/service-key.json"))[0]

  credentials = service_account.Credentials.from_service_account_file(
          SERVICE_ACCOUNT_FILE, scopes=SCOPES)
  delegated_credentials = credentials.with_subject(EMAIL_FROM)
  service = build('gmail', 'v1', credentials=delegated_credentials)
  return service

def create_message(sender, to, subject, message_text):
    """
    Create a message for an email.
    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.
    Returns:
    An object containing a base64url encoded email object.
    """
    mime_message = EmailMessage()
    # headers
    mime_message['To'] = to
    mime_message['From'] = sender
    mime_message['Subject'] = subject
    mime_message.set_content(message_text)

    # attachment_filename = 'photo.jpg'

    encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()

    message = {'raw': encoded_message}
    
    return message

def send_message(service, user_id, message):
  """Send an email message.
  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.
  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message).execute())
    print('Message Id: %s' % message['id'])
    return message
  except errors.HttpError as error:
    print('An error occurred: %s' % error)


service = service_account_login()
# Call the Gmail API
message = create_message(EMAIL_FROM, EMAIL_TO, EMAIL_SUBJECT, EMAIL_CONTENT)
sent = send_message(service, 'me', message)