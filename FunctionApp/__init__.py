from ast import Assert
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
    
    #params = req.params.get('name')
    #print(params)
    data = query()
    #if not params:
  
    arrx,arry = graph(data)
   
    writeToJs('chart-area.js',arrx,arry)

    saveToBlob('chart-area.js')
    #else:
        #arrx,arry = graph2(data,params)
        #writeToJs('chart-bar.js',arrx,arry)
        #saveToBlob('chart-bar.js')

    return func.HttpResponse("", status_code=200)

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
    
    #Salvo il file PER TESTING 
    #with open('data.json', 'w') as f:
    #    json.dump(data, f)
    
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
    
    #Salvo il file PER TESTING 
    with open('data.json', 'w') as f:
        json.dump(data, f)
    
    return arrx,arry

def writeToJs(jsfile,arrx,arry):
    with open(jsfile) as f:
        lines = f.readlines()
    string = 'var x = '+(''.join(str(arrx)))+';'+'var y = '+(''.join(str(arry)))+';\n'
    lines[0] = string
   

    with open(jsfile, "w") as f:
        f.writelines(lines)
        
def saveToBlob(jsfile):               
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    
    blob_client = blob_service_client.get_blob_client(container=os.getenv('AZURE_STORAGE_CONTAINER'), blob=jsfile)
    
    with open(jsfile, "rb") as data:
        blob_client.upload_blob(data,overwrite=True)
    