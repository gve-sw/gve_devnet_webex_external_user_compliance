# gve_devnet_webex_external_user_compliance
Dashboard that allows a Webex Compliance Officer to view individual external users allowed to communicate within the organization. 


## Contacts
* Charles Llewellyn

## Solution Components
* Python
*  Webex
*  Flask

## Installation/Configuration



### Environment Variables to be filled out:

Description of Environment Variables:
```
COMPANY_DOMAIN: The domain of internal webex users (Example: If User = chllewel@cisco.com, then Domain = cisco.com) 
CLIENT_ID: The Webex App OAuth Client ID
CLIENT_SECRET: The Webex App OAuth Client Secret
REDIRECT_URI: Must be equal to the "/auth" endpoint of this appplication's IP Address. (If running locally: https://127.0.0.1:5001/auth)
AUTHORIZATION_URL: The Webex Authorization API Endpoint
```


.env
```shell
COMPANY_DOMAIN = 
CLIENT_ID = 
CLIENT_SECRET = 
REDIRECT_URI = "https://127.0.0.1:5001/auth"
AUTHORIZATION_URL = "https://webexapis.com/v1/authorize"
```

### OAuth Permmissions that need to be granted for Webex App:
```
spark:all
spark-admin:people_read
spark-compliance:events_read
spark-compliance:memberships_read
spark-compliance:rooms_read
spark-compliance:messages_read
```

### Install Requirements
```python
$ pip install -r requirements.txt
```


## Usage

To launch application:


    $ python app.py



# Screenshots
![/IMAGES/Screenshot.png](/IMAGES/Screenshot.png)

![/IMAGES/0image.png](/IMAGES/0image.png)

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.
