import requests
import time


# def get_shoeventory(token, merchantId):
def create_transaction(merchantId, shoes):
    url = "http://localhost:8080/api/v1/transaction/"  # Replace this with the API endpoint URL
    # headers = {"Authorization": "Bearer " + token}  # Replace with any required headers
    headers = {"Content-Type": "application/json"}
    merchant = str(merchantId)
    data = {
        "merchantId": merchantId,
        "transactionTime": int(time.time()),
        "shoes": []
    }
    for shoe in shoes:
        shoe_payload = {
            "manufacturer": shoe.get("manufacturer", ""),
            "type": shoe.get("shoeType", ""),
            "name": shoe.get("shoeName", ""),
            "color": shoe.get("shoeColor", ""),
            "size": shoe.get("shoeSize", ""),
            "quantity": shoe.get("shoeQuantity", ""),
            "price": shoe.get("shoePrice", "")
        }
        data["shoes"].append(shoe_payload)

    print(data)

    response = requests.post(url, json=data, headers=headers)

    # Check if the request was successful (status code 2xx)
    if response.status_code // 100 == 2:
        # Check if the response content is not empty
        if response.text.strip():
            # Attempt to parse the response JSON
            try:
                response_data = response.json()
                print("Response:", response_data)
            except ValueError as e:
                print("Error parsing response JSON:", e)
        else:
            print("Response is empty (this is a good sign lmao)")
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.text)  # Print the response body for debugging purposes

