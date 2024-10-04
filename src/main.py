# Entry point of the application
import os
import time
import requests

# Retrieve the GitHub App ID and private key from the environment
client_id = os.getenv("GITHUB_CLIENT_ID")
private_key_file = os.getenv("GITHUB_APP_PRIVATE_KEY_FILE")

# Send a POST request to https://github.com/login/device/code along with a client_id query parameter
# The response will contain a user_code, device_code, and verification_uri
device_code_url = "https://github.com/login/device/code"
params = {
    "client_id": client_id
}
headers = {
    "Accept": "application/json"
}
response = requests.post(device_code_url, params=params, headers=headers)
response.raise_for_status()

print(f"Device code request status: {response.status_code}")

data = response.json()
device_code = data["device_code"]
user_code = data["user_code"]
verification_uri = data["verification_uri"]
expires_in = data["expires_in"]
interval = data["interval"]

print(f"Enter the code {user_code} at {verification_uri}")

# Poll the verification endpoint based on the interval value until the user has successfully authenticated
# The response will contain an access_token that can be used to authenticate as the installation
verification_uri = "https://github.com/login/oauth/access_token"
params = {
    "device_code": device_code,
    "client_id": client_id,
    "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
}

while True:
    response = requests.post(verification_uri, data=params, headers=headers)
    response.raise_for_status()

    if response.status_code != 200:
        print(response.status_code)
        print(response.text)
        exit(1)

    data = response.json()
    error = data.get("error")
    access_token = data.get("access_token")

    if access_token:
        # The user has successfully authenticated
        break
    
    if error:
        # Print the error
        print(error)
        if error == "authorization_pending":
            # The user has not yet entered the code.
            # Wait, then poll again.
            time.sleep(interval)
            continue
        elif error == "slow_down":
            # The app polled too fast.
            # Wait for the interval plus 5 seconds, then poll again.
            time.sleep(interval + 5)
            continue
        elif error == "expired_token":
            # The `device_code` expired, and the process needs to restart.
            print("The device code has expired. Please run `login` again.")
            exit(1)
        elif error == "access_denied":
            # The user cancelled the process. Stop polling.
            print("Login cancelled by user.")
            exit(1)
        else:
            print(response)
            exit(1)
        

print(f"Access token: {access_token}")
