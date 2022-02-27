from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
from re import T
from bson import json_util, ObjectId
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
    print("Azure Blob Storage v" + __version__ + " - Python quickstart sample")
    params = req.params.get('name')
    print(params)
    query(params)  
    #with open("Assets/graph.png", 'rb') as f:
    #    mimetype = mimetypes.guess_type("Assets/graph.png")
    #    return func.HttpResponse(f.read(), mimetype=mimetype[0])
    return func.HttpResponse("", status_code=200)

def query(param):

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
    
    #Salvo il file 
    with open('data.json', 'w') as f:
        json.dump(data, f)

    
    client.close()


def graph(qty,price):
    
    print(qty,price)
    
    plt.plot(qty,price)
    plt.ylabel('some numbers')
    plt.show()
    

    plt.savefig('Assets/graph.png')
    
