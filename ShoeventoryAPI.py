import requests

#def get_shoeventory(token, merchantId):
def get_shoeventory(merchantId):
    url = "https://localhost:7136/api"  # Replace this with the API endpoint URL
    #headers = {"Authorization": "Bearer " + token}  # Replace with any required headers
    merchant = str(merchantId)

    try:
        # response = requests.get(url, headers=headers)
        full_url = url + "/collections/" + merchant + "/merchant"
        print(full_url)
        response = requests.get(url + "/collections/" + merchant + "/merchant", verify=False)

        if response.status_code == 200:  # Successful response
            data = response.json()
            return data
        else:
            print("Failed to get data from the API:", response.status_code)
            return None

    except requests.exceptions.RequestException as e:
        print("Error sending request to the API:", e)
        return None
