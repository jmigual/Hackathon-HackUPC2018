
# coding: utf-8

# In[48]:


import requests
import json

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


if __name__=="__main__":
    print(get_lab_buildings())

