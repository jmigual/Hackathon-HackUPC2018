
# coding: utf-8

# In[121]:


import requests
import json
import time

def get_token():
    with open("token.key") as f:
        return f.readline()
    
def add_id(url):
    url += '&client_id=' + get_token()
    return url

def get_lab_buildings():
    labs_url = 'https://api.fib.upc.edu/v2/laboratoris/?format=json'
    labs = json.loads(requests.get(add_id(labs_url)).content)
    return labs['imatges'].keys()

def lab_image(building):
    labs_url = 'https://api.fib.upc.edu/v2/laboratoris/?format=json'
    labs = json.loads(requests.get(add_id(labs_url)).content)
    
    image_url = labs['imatges'][building]
    return add_id(image_url)

def available_labs(building):
    labs_url = 'https://api.fib.upc.edu/v2/laboratoris/?format=json'
    labs = json.loads(requests.get(add_id(labs_url)).content)

    available = {}

    for avla in labs['results']:
        places = avla['places_disponibles']
        if places != None and len(avla['reserves_actuals']) == 0 and places > 0 and avla['id'][:2] == building:
            date = ''
            reserves = json.loads(requests.get(add_id(avla['reserves'])).content)
            for res in reserves['results']:
                if (time.mktime(time.strptime(res['inici'], time_format)) > time.time()):
                    date = res['inici']
                    break
                    
            available[avla['id']] = (avla['places_disponibles'], date)
            
    return available

