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
    print(params)
    data = query()
    if not params:
        arrx,arry = graph(data)
    else:
        arrx,arry = graph2(data,params)

    context = {
        'x': arrx,
        'y': arry,
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
    print(arrx,arry)

    return arrx,arry

