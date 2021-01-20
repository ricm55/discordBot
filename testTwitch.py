#test request twitch

import twitch
import requests
import json

post_url = 'https://id.twitch.tv/oauth2/token'

post_demande = {
    'client_id' : 'jzgteoto59lcisee5tpudqj8t1ae5f',
    'client_secret' : '58znn6ctm4awoowlkkl48hnhmo5tnf',
    'grant_type' : 'client_credentials'
}

post_response = requests.post(post_url,post_demande)

access_token = post_response.json()["access_token"]


get_url = 'https://api.twitch.tv/helix/streams'

get_demande = {
    'Authorization' : 'Bearer ' + access_token,
    'Client-Id' : 'jzgteoto59lcisee5tpudqj8t1ae5f',
}

query = {
    'user_login' : 'lcs'
}
get_response = requests.get(get_url, query, headers=get_demande)

isLive = get_response.json()

if not isLive['data'] :
    print("no live here")
else:
    print("he's in live!!!")




#isLive = get_response.json()

#data = isLive['data']

#data1 = data[0]

#data2 = data1['type']
"""
isLive = isLive[99]
isLive = isLive['type']
"""
#print(data2)
"""
#send http request
response = requests.get(url4, request=api_request,headers=api_header)
print(f"RESPONSE => {response}")
response = response.json()
print(f"RESPONSE => {response}")
"""