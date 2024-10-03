# Entry point of the application
import os
import requests

# Retrieve the GitHub App ID and private key from the environment
client_id = os.getenv("GITHUB_CLIENT_ID")
private_key_file = os.getenv("GITHUB_APP_PRIVATE_KEY_FILE")

# Send a POST request to https://github.com/login/device/code along with a client_id query parameter
# The response will contain a user_code, device_code, and verification_uri
url = "https://github.com/login/device/code"
params = {
    "client_id": client_id
}
headers = {
    "Accept": "application/json"
}
response = requests.post(url, params=params, headers=headers)
response.raise_for_status()

print(f"Device code request status: {response.status_code}")

data = response.json()
device_code = data["device_code"]
user_code = data["user_code"]
verification_uri = data["verification_uri"]
expires_in = data["expires_in"]
interval = data["interval"]

print(f"Enter the code {user_code} at {verification_uri}")

# Retrieve string from command line
#user_input = input("Enter a repo: ")

# Print the string
#print(f"Retrieving repo {user_input}")