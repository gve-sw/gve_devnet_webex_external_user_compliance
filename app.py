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

# Import Section
from flask import Flask, render_template, request, url_for, redirect, session, jsonify, send_file
from requests_oauthlib import OAuth2Session
import datetime
import requests
from dotenv import load_dotenv
import webex
import os
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import shutil

# load all environment variables
load_dotenv()



# Global variables
app = Flask(__name__)
app.secret_key = "abc"

# Methods
# Returns location and time of accessing device
def getSystemTimeAndLocation():
    # request user ip
    userIPRequest = requests.get('https://get.geojs.io/v1/ip.json')
    userIP = userIPRequest.json()['ip']

    # request geo information based on ip
    geoRequestURL = 'https://get.geojs.io/v1/ip/geo/' + userIP + '.json'
    geoRequest = requests.get(geoRequestURL)
    geoData = geoRequest.json()
    
    #create info string
    location = geoData['country']
    timezone = geoData['timezone']
    current_time=datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
    timeAndLocation = "System Information: {}, {} (Timezone: {})".format(location, current_time, timezone)
    
    return timeAndLocation


##Routes
#Instructions


#Auth
@app.route('/auth', methods=['GET', 'POST'])
def auth():
    try:
        auth_code = request.args['code']
        token = webex.oauth(auth_code)
        print(token)
        session['token'] = token


        #Page without error message and defined header links
        return redirect(url_for('webapp'))
    except Exception as e:
        print(e)
        #OR the following to show error message
        return redirect(url_for('login'))


#Login
@app.route('/', methods=['GET', 'POST'])
def login():
    try:
        if request.method == "GET":

            #Page without error message and defined header links
            return render_template('login.html', hiddenLinks=True, timeAndLocation=getSystemTimeAndLocation())
        if request.method == "POST":
            CLIENT_ID = os.environ['CLIENT_ID']
            #oauth
            teams = OAuth2Session(CLIENT_ID, redirect_uri=os.environ['REDIRECT_URI'], scope=["spark:all","spark-admin:people_read","spark-compliance:events_read","spark-compliance:memberships_read","spark-compliance:rooms_read","spark-compliance:messages_read"])
            authorization_url, state = teams.authorization_url(url=os.environ['AUTHORIZATION_URL'])

            session['state'] = state

            return redirect(authorization_url)
    except Exception as e:

        print(e)  
        #OR the following to show error message 
        return render_template('login.html', error=False, errormessage=e, errorcode=e, timeAndLocation=getSystemTimeAndLocation())

#APP
@app.route('/app', methods=['GET', 'POST'])
def webapp():
        if request.method == "GET":
            try:
                internal_users, external_users = webex.get_users(token=session['token'])
                return render_template('app.html', internal_users=internal_users, external_users=external_users)

            except Exception as e:
                print(e)
                return redirect(url_for('login'))

        elif request.method == "POST":
            try:
                users = request.get_json(force=True)['users']
                print(users)
                uri, name = webex.create_zip_files(token=session['token'], users=users)
                print(uri)
                print(name)
                memory_file = open(uri+'/'+name+'.zip', 'rb')

                return jsonify({"uri": f"{uri}", "name": f"{name}.zip", "status":"True"})
                # return send_file(memory_file, attachment_filename=f'{name}.zip', as_attachment=True)

            except Exception as e:
                print(e)
                return jsonify({"status":"False"})

@app.route('/<file_uri>/download/', methods=['GET', 'POST'])
def download_file(file_uri):
    try:
        dir = os.path.dirname(os.path.abspath(__file__))
        return send_file(f"{dir}/media/{file_uri}", download_name=f'{file_uri}', as_attachment=True)
    finally:
        os.remove(f"{dir}/media/{file_uri}")

@app.route('/<file_uri>/remove/', methods=['GET', 'POST'])
def remove_file(file_uri):
    try:
        dir = os.path.dirname(os.path.abspath(__file__))
        os.remove(f"{dir}/media/{file_uri}")
        return "True"
    except Exception as e:
        print(e)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001, debug=True, ssl_context='adhoc')