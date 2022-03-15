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
    
    #Get parameter from HTTP request
    params = req.params.get('name')
    user = req.params.get('user')
    
    print(params)
    print(user)
    #Get all data
    data = query()
    #Filter by user
    if user == "user":
        arrx, arry = graph(data)
        arr2x, arr2y = graph4(data)
        arr3x = 0
        arr3y = 0
        arr4x = 0
        arr4y = 0
    elif user == "admin":
        arrx, arry = graph3(data)
        arr3x, arr3y = graph(data)
        arr4x, arr4y = graph4(data)
        if params:
            arr2x, arr2y = graph2(data, params)
        else:
            arr2x = 0
            arr2y = 0

    #Generate JSON
    context = {
        'x': arrx,
        'y': arry,
        'x2': arr2x,
        'y2': arr2y,
        'x3': arr3x,
        'y3': arr3y,
        'x4': arr4x,
        'y4': arr4y
    }
    #Saving json 
    data = json.dumps(context, indent=4, sort_keys=True, default=str)
    #Return json as httpresponse
    return func.HttpResponse(data, status_code=200)


def query():
    # Connection to db with pymongo
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
    #Take all value
    for item in col.find():
        items.append(dict(item))

    #print('Query returned {0} items.'.format(len(items)))

    # return items
    data = json.loads(json_util.dumps(items))

    #Close connection with db
    client.close()
    return data


#Most popular drink
def graph(data):
    title = []
    qty = []
    for d in data:
        c = d['cart']
        for sd in c['items'].values():
            title.append(sd['item']['title'])
            qty.append(sd['qty'])
  
    current = 0
    arrx = []
    arry = []
    #Filtering same data
    for t, q in zip(title, qty):
        current += 1
        if t in arrx:#Check if element is already in arrx
            index = arrx.index(t)
            arry[index] = arry[index]+qty[current-1]#Increment number of occurrency
        else:
            arrx.append(t)
            arry.append(q)
    return arrx, arry


#Check single drink popularity
def graph2(data, params):
    qty = []
    date = []
    for d in data:
        c = d['cart']
        for sd in c['items'].values():
            if sd['item']['title'] == params:
                date.append(d['date'])
                qty.append(sd['qty'])
    #Filtering same data
    current = 0
    arrx = []
    arry = []
    for d, q in zip(date, qty):
        current += 1
        if d in arrx:
            index = arrx.index(d)
            arry[index] = arry[index]+qty[current-1]
        else:
            arrx.append(d)
            arry.append(q)

    return arrx, arry


#Daily earn
def graph3(data):
    prices = []
    dates = []
    for d in data:
        c = d['cart']
        for sd in c['items'].values():
            prices.append(sd['item']['price'])
            dates.append(d['date'])
    print(prices, dates)
    float_map = map(float, prices)
    float_prices = list(float_map)
    #Filtering same data
    current = 0
    arrx = []
    arry = []
    for t, q in zip(dates, float_prices):
        current += 1
        if t in arrx:
            index = arrx.index(t)
            arry[index] = float("{:.2f}".format(arry[index]+float_prices[current-1]))
        else:
            arrx.append(t)
            arry.append(q)
    return arrx, arry

#Most popular extras
def graph4(data):
    extras = []
    for d in data:
        c = d['cart']
        if 'extra' in d:
            if d['extra'] != "empty":#Extra in orders !=empty
                extras.append(d['extra'])
    print(extras)
    #Filtering same data
    current = 0
    arrx = []
    arry = []
    for t in (extras):
        current += 1
        if t in arrx:
            index = arrx.index(t)
            arry[index] = arry[index]+1
        else:
            arrx.append(t)
            arry.append(1)
    return arrx, arry
