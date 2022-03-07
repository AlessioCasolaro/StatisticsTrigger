from re import T
from bson import json_util
import json
from dotenv import load_dotenv
import os
import pymongo
import logging
import azure.functions as func
import matplotlib.pyplot as plt


plt.rcdefaults()

def main(req: func.HttpRequest) -> func.HttpResponse:
    load_dotenv()
    logging.info('Python HTTP trigger function processed a request.')
    
    params = req.params.get('name')
    user = req.params.get('user')
    print(params)
    print(user)
    data = query()
    if user == "user":
        arrx,arry = graph(data)
        arr2x,arr2y = graph4(data)
       
    elif user == "admin":
        arrx,arry = graph3(data)
        if params:
            arr2x,arr2y = graph2(data,params)
        else:
            arr2x = 0
            arr2y = 0
    
    context = {
        'x': arrx,
        'y': arry,
        'x2': arr2x,
        'y2': arr2y
    }
    data = json.dumps(context, indent=4, sort_keys=True, default=str)
  
    return func.HttpResponse(data, status_code=200)

def query():

    uri = os.getenv('URI')
    client = pymongo.MongoClient(uri)

    # Database name
    db = client[os.getenv('DB_NAME')]

    # Collection name
    col = db[os.getenv('COLLECTION_NAME')]

    try:
        client.server_info()  # validate connection string
        print("Connection OK")
    except pymongo.errors.ServerSelectionTimeoutError:
        raise TimeoutError(
            "Invalid API for MongoDB connection string or timed out when attempting to connect")

    items = []

    for item in col.find():
        items.append(dict(item))

    print('Query returned {0} items.'.format(len(items)))
    
    # return items
    data = json.loads(json_util.dumps(items))
    
    client.close()
    return data
    
#Utente
def graph(data):
    #Prendo i dati che mi servono        
    title = []
    qty = []
    for d in data:
        c = d['cart']
        for sd in c['items'].values():
            title.append(sd['item']['title'])
            qty.append(sd['qty'])   
    print(title,qty)
    
    #Filtro quelli uguali
    current = 0
    arrx = []
    arry=[]
    for t,q in zip(title,qty):
            current+=1
            if t in arrx:
                index = arrx.index(t)
                arry[index]= arry[index]+qty[current-1]     
            else:
                arrx.append(t)
                arry.append(q)
    print(arrx,arry)
    
    return arrx,arry
#admin
def graph2(data,params):
    #Prendo i dati che mi servono        
    title = []
    qty = []
    date = []
    for d in data:
        c = d['cart']
        for sd in c['items'].values():
            if sd['item']['title'] == params:
                date.append(d['date'])
                qty.append(sd['qty'])   
    print(qty,date)

    #Filtro quelli uguali
    current = 0
    arrx = []
    arry=[]
    for d,q in zip(date,qty):
            current+=1
            if d in arrx:
                index = arrx.index(d)
                arry[index]= arry[index]+qty[current-1]     
            else:
                arrx.append(d)
                arry.append(q)
    

    return arrx,arry


#Admin
def graph3(data):
    #Prendo i dati che mi servono
    prices = []
    dates = []
    for d in data:
        c = d['cart']
        for sd in c['items'].values():
            prices.append(sd['item']['price'])
            dates.append(d['date'])
    print(prices,dates)
    float_map = map(int,prices)
    float_prices = list(float_map)
    #Filtro quelli uguali
    current = 0
    arrx = []
    arry=[]
    for t,q in zip(dates,float_prices):
            current+=1
            if t in arrx:
                index = arrx.index(t)
                arry[index]= arry[index]+float_prices[current-1]
            else:
                arrx.append(t)
                arry.append(q)
    print("Array finale",arrx,arry)

    return arrx,arry

def graph4(data):
    #Prendo i dati che mi servono
    extras = []

    for d in data:
        c = d['cart']
        if 'extra' in d:
            if d['extra'] != "empty":
                extras.append(d['extra'])
    print(extras)

    #Filtro quelli uguali
    current = 0
    arrx = []
    arry=[]
    for t in (extras):
            current+=1
            if t in arrx:
                index = arrx.index(t)
                arry[index]= arry[index]+1
            else:
                arrx.append(t)
                arry.append(1)
    print(arrx,arry)

    return arrx,arry