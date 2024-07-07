# import requests
# http_proxy  = "http://10.10.1.10:3128"
# https_proxy = "https://10.10.1.11:1080"
# ftp_proxy   = "ftp://10.10.1.10:3128"

# proxies = { 
#               "http"  : http_proxy, 
#               "https" : https_proxy, 
#               "ftp"   : ftp_proxy
#             }

import requests

proxies = {
    "http": "http://123.45.67.89:8080",
    "https": "https://123.45.67.89:8080",
}

r=requests.get("https://api.ipify.org?format=json", proxies=proxies)

# r = requests.get("")
print(r.json())


