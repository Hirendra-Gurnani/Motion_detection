# import requests

# url = "https://messagebird-sms-gateway.p.rapidapi.com/sms"

# querystring = {"username":"hirendragurnaniddmca18@acropolis.in","password":"Myfiles@cdrive2"}

# payload = {
# 	"sender": "MessageBird",
# 	"body": "This is a gsm 7-bit test message.",
# 	"destination": "9589200582",
# 	"reference": "268431687",
# 	"timestamp": "201308020025",
# 	"replacechars": "checked",
# 	"type": "normal",
# 	"dlr_url": "http://www.example.com/dlr-messagebird.php"
# }
# headers = {
# 	"content-type": "application/x-www-form-urlencoded",
# 	"X-RapidAPI-Key": "a5c0989ce7mshe5fc30f77806dabp1a2b54jsn98aed6579184",
# 	"X-RapidAPI-Host": "messagebird-sms-gateway.p.rapidapi.com"
# }

# response = requests.post(url, data=payload, headers=headers, params=querystring)

# print(response.json())





































import json
import requests
url = "https://api2.juvlon.com/v4/httpSendMail"
data = {"ApiKey":"OTU1NTAjIyMyMDIzLTA1LTE3IDE1OjQ1OjAy",
        "requests":[{"subject":"Hello",
                        "from":"hirendragurnaniddmca18@acropolis.in",
                        "body":"This is an API test from Juvlon",
                          "to":"adityanarayanan7@gmail.com"}]}
data_json = json.dumps(data)
r = requests.post(url, data=data_json)

print(r)