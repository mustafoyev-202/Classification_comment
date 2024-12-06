import requests

url = "http://127.0.0.1:8000/comment"

payload = {"comment": "Mehmed chiz gap yo’q prosta👍🏻 yeb ko’rila tavsiyuu )"}
response = requests.post(url, json=payload)

if response.status_code == 200:
    print("Response from server:", response.json()['result'])
else:
    print(f"Failed to get a response. Status code: {response.status_code}")
    print("Response:", response.text)
