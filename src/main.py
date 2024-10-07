# Entry point of the application
import json
import os
import time
import requests

# Retrieve the GitHub App ID and private key from the environment
client_id = os.getenv("GITHUB_CLIENT_ID")
copilot_integration_id = os.getenv("COPILOT_INTEGRATION_ID")

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

messages_for_copilot = [{ "role": "user", "content": "List my issues" }]
url = "https://api.githubcopilot.com/agents/chat"
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Copilot-Integration-Id": copilot_integration_id,
    "Authorization": f"Bearer {access_token}",
}

# type ChatRequest struct {
#     ThreadID         string                                `json:"copilot_thread_id"`
#     Messages         []*agentprompt.Message                `json:"messages"`
#     Stop             []string                              `json:"stop"`
#     TopP             float32                               `json:"top_p"`
#     Temperature      float32                               `json:"temperature"`
#     MaxTokens        int32                                 `json:"max_tokens"`
#     PresencePenalty  float32                               `json:"presence_penalty"`
#     FrequencyPenalty float32                               `json:"frequency_penalty"`
#     ResponseFormat   *schema.ChatCompletionsResponseFormat `json:"response_format"`

#     Skills []string `json:"copilot_skills"`
#     Agent  string   `json:"agent"`
#     Model  string   `json:"model"`
# }
body = {
    "messages": messages_for_copilot,
    "copilot_skills": ["get-github-data"],
    "model": "gpt-4o-mini",
}

response = requests.post(url, headers=headers, data=json.dumps(body))
response.raise_for_status()

print(response.json())