import ipaddress
import requests

# IP = '192.0.2.0/28'
# IP2 = '10.0.2.0/29'
# net4 = ipaddress.ip_network(IP2)
# for net in net4.hosts():
#     print(net)

# single IP request
# response = requests.get('http://ip-api.com/json/24.48.0.1').json()
# print(response)
# print(response['lat'])
# print(response['lon'])

#batch IP request, only works with POST
response = requests.post('http://ip-api.com/batch',json=[
    {"query":"208.80.152.201"},
    {"query":"167.71.3.52"},
    {"query":"206.189.198.234"},
    {"query":"157.230.75.212"}
]).json()

for ip_info in response:
    for k,v in ip_info.items():
        print(k,v)
    print('\n')
