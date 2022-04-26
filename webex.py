""" Copyright (c) 2020 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. 
"""

from webexteamssdk import WebexTeamsAPI
from dotenv import load_dotenv
import os
import tempfile
import shutil
from prettyprinter import pprint
import requests
import  magic
from mimetypes import guess_extension
import pandas as pd
import datetime
import traceback
import json

load_dotenv()
domain = os.environ['COMPANY_DOMAIN']
oauth_client_id = os.environ['CLIENT_ID']
oauth_client_secret = os.environ['CLIENT_SECRET']
oauth_redirect_uri = os.environ['REDIRECT_URI']

domain = domain.lower()
mime = magic.Magic(mime=True)

def get_users(token):
    webex = WebexTeamsAPI(access_token=token)
    internal_emails = []
    external_emails = []
    try:
        users = webex.people.list()
        for user in users:
            for email in user.emails:
                email_domain = email.partition("@")[2].lower()
                if domain == email_domain:
                    internal_emails.append({"email": email, "firstName":user.firstName, "lastName": user.lastName, "id":user.id})
                else:
                    external_emails.append({"email": email, "firstName":user.firstName, "lastName": user.lastName, "id":user.id})

        return internal_emails,external_emails


    except Exception as e:
        print(traceback.format_exc())
        print(e)

def audit_user(token, users=[]):
    webex = WebexTeamsAPI(access_token=token)
    try:
        for user_id in users:
            user_events = webex.events.list(actorId=user_id)
            user_email  = webex.people.get(user_id).emails
            yield user_events, user_email
    except Exception as e:
        print(e)


def create_zip_files(users, token):
    webex = WebexTeamsAPI(access_token=token)
    with tempfile.TemporaryDirectory() as dirpath:
        for user, user_emails in audit_user(users=users, token=token):
            rows = []
            user_dirpath = f"{dirpath}/{user_emails[0]}"
            if not os.path.isdir(user_dirpath):
                os.mkdir(user_dirpath)
            for event in user:
                data = {}
                data.update({"Resource":event.resource})
                data.update({"Type":event.type})
                data.update({"Actor's Email(s)": "".join(user_emails)})
                for k, v in event.data.__dict__['_json_data'].items():
                    if k == "roomId":
                        room = webex.rooms.get(v)
                        if "roomType" in event.data.__dict__['_json_data']:
                            if event.data.roomType == "direct":
                                membership = webex.memberships.list(roomId=room.id)
                                for member in membership:
                                    if member.personId != event.actorId:
                                        if event.type == "created":
                                            data.update({"Direct Message Recipient": member.personEmail.lower()})
                                        elif event.type == "read":
                                            data.update({"Direct Message Sender": member.personEmail.lower()})
                        if "roomType" in event.data.__dict__['_json_data']:
                            if event.data.roomType == "direct":
                                data.update({"Room Title": "Direct Message"})
                        else:
                            data.update({"Room Title":room.title})
                    elif k == "created":
                        data.update({"Created": v})
                    elif k == "text":
                        data.update({"Message Text": v})
                    elif k == "roomType":
                        data.update({"Room Type" : v})
                    elif k == "contentUrl":
                        content = requests.get(v, headers={"Authorization": f"Bearer {token}"})
                        file_extension = guess_extension(mime.from_buffer(content.content))
                        if file_extension == ".txt":
                            data.update({"File Content": content.text})
                        else:
                            if not os.path.isdir(f"{user_dirpath}/files"):
                                os.mkdir(f"{user_dirpath}/files")
                            with open(f"{user_dirpath}/files/webex_file-{event.data.id}{file_extension}", "wb") as f:
                                f.write(content.content)
                                data.update({"File Content": f"{user_emails[0]}/files/webex_file-{event.data.id}{file_extension}"})

                    elif k == "files":
                        if not os.path.isdir(f"{user_dirpath}/files"):
                            os.mkdir(f"{user_dirpath}/files")

                        i = 0
                        for file in v:
                            content = requests.get(file, headers={"Authorization": f"Bearer {token}"})
                            file_extension = guess_extension(mime.from_buffer(content.content))

                            with open(f"{user_dirpath}/files/webex_file-{event.data.id}-{i}{file_extension}", "wb") as f:
                                f.write(content.content)
                                data.update({"File Content": f"{user_emails[0]}/files/webex_file-{event.data.id}-{i}{file_extension}"})
                            i += 1




                rows.append(data)
                print(data)

            pprint(rows)
            df = pd.DataFrame(rows)
            try:
                print(user_dirpath)
                df.to_excel(f"{user_dirpath}/{user_emails[0]}-AUDIT.xlsx", index=False)
                user_dirpath = None


            except Exception as e:
                print(traceback.format_exc())
                print(e)

        destination_dir = os.path.dirname(os.path.abspath(__file__))
        dtime = str(datetime.datetime.now())
        shutil.make_archive(f"{destination_dir}/media/AUDIT_REPORT_{dtime}", 'zip', dirpath)
        return f"{destination_dir}/media", f"AUDIT_REPORT_{dtime}"


def oauth(auth_code):
    url="https://webexapis.com/v1/access_token"
    headers = {'Content-Type':'application/x-www-form-urlencoded'}
    data = {'grant_type':'authorization_code','client_id':oauth_client_id,'client_secret':oauth_client_secret,'code':auth_code,'redirect_uri':oauth_redirect_uri}

    response = requests.post(url=url, headers=headers, data=data)

    return json.loads(response.content)['access_token']


if __name__ == "__main__":
    internal_emails, external_emails = get_users()
    create_zip_files(external_emails)




