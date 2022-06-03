import requests
import json
from decouple import config
import pandas as pd
import time
from discord import discord_webhook


class MakeApiCall:
    # establish authentication token with api
    def post_simple_token(self):
        headers = {"X-SIMPLE-API-ACCESS-TOKEN": config("SIMPLE_TOKEN")}
        response = requests.post(
            f"{self.site}/Api/SimpleAuthentication", headers=headers
        )
        if response.status_code == 200:
            pass
        else:
            print(f"There's a {response.status_code} error with your request")
            msg = f"There's a {response.status_code} error with your request. {response.text}"
            discord_webhook(msg)
        return response.json()

    # gets all targets and prints to file for later reference
    def get_all_targets(self):
        response = requests.get(f"{self.site}/Api/targets", headers=self.headers)
        if response.status_code == 200:
            file_name = "all_targets.json"
            self.save_current_verification(response.json(), file_name)
        else:
            print(f"There's a {response.status_code} error with your request")
            msg = f"There's a {response.status_code} error with your request. {response.text}"
            discord_webhook(msg)

    # create verification (in a pending status)
    def post_create_verification(self):
        response = requests.post(
            f"{self.site}/Api/verifications", headers=self.headers, json=self.target
        )
        if response.status_code == 200:
            print("Created a pending verification!!")
            file_name = "current_verification.json"
            self.save_current_verification(response.json(), file_name)
        elif response.status_code == 402:
            print(response.text)
            msg = response.text
            discord_webhook(msg)
        elif response.status_code == 429:
            self.put_cancel_verification()
            time.sleep(5)
            self.post_create_verification()
        else:
            print(
                f"There's a {response.status_code} error with your request. {response.text}"
            )
            msg = f"There's a {response.status_code} error with your request. {response.text}"
            discord_webhook(msg)
        return response.json()

    # cancel pending verification
    def put_cancel_verification(self):
        headers = {
            "Authorization": "Bearer " + self.bearer_token,
            "content-type": "text/plain",
        }
        file_name = "current_verification.json"
        file_data = self.get_data_from_file(file_name)
        id = file_data["id"]
        response = requests.put(
            f"{self.site}/api/verifications/{id}/cancel",
            headers=headers,
        )
        if response.status_code == 200:
            print("Your pending verification has been cancelled!!")
        else:
            print(f"There's a {response.status_code} error with your request")
            msg = f"There's a {response.status_code} error with your request. {response.text}"
            discord_webhook(msg)

    # get pending verification info
    def get_pending_verification(self):
        response = requests.get(
            f"{self.site}/api/verifications/pending", headers=self.headers
        )
        if response.status_code == 200:
            print(f"Pending verification: {response.json()}")
        else:
            print(f"There's a {response.status_code} error with your request")
            msg = f"There's a {response.status_code} error with your request. {response.text}"
            discord_webhook(msg)
        return response.json()

    # get verification status
    def get_verification_status(self):
        file_name = "current_verification.json"
        file_data = self.get_data_from_file(file_name)
        id = file_data["id"]
        response = requests.get(
            f"{self.site}/api/verifications/{id}",
            headers=self.headers,
        )
        if response.status_code == 200:
            file_name = "verification_status.json"
            self.save_current_verification(response.json(), file_name)
        else:
            print(f"There's a {response.status_code} error with your request")
            msg = f"There's a {response.status_code} error with your request. {response.text}"
            discord_webhook(msg)
        return response.json()

    def save_current_verification(self, obj, file_name):
        with open(file_name, "w") as f:
            json.dump(obj, f)

    def get_data_from_file(self, file_name):
        with open(file_name, "r") as f:
            return json.load(f)

    # pulls target data from json to prep for verification creation
    def pull_toi(self, target_name):
        file = pd.read_json("all_targets.json")
        df = pd.DataFrame(file).set_index("normalizedName")
        target_data = df.loc[target_name]
        target_id = target_data["targetId"]
        return target_id

    def __init__(self, target_name):
        self.site = "https://www.textverified.com"
        # Gets API token
        simple_token_json = self.post_simple_token()
        self.bearer_token = simple_token_json["bearer_token"]
        self.headers = {
            "Authorization": "Bearer " + self.bearer_token,
            "content-type": "application/json",
        }
        # Gets updated info for all targets
        self.get_all_targets()
        self.target = {"id": int(self.pull_toi(target_name))}


# for testing
# target_name = "footlocker"
# api_call = MakeApiCall(target_name)
# verification_data = api_call.post_create_verification()
# verification_data = api_call.get_pending_verification()
# verification_data = api_call.get_verification_status()
# verification_data = api_call.put_cancel_verification()
# verification_data = api_call.get_all_targets()
