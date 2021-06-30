import requests

baseurl = 'http://www.indeed.com/jobs?'
params = {
    "q": 'Financial+Analyst',
    "l": "Vancouver,BC",
    "fromage": "27"
}
headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get(url=baseurl,params=params,headers=headers)
res.encoding = 'utf-8'
print(res.text)