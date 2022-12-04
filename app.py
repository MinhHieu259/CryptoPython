from flask import Flask, render_template, jsonify
import mysql.connector
import requests
import time
import threading

conn = mysql.connector.connect(user='root', password='1234',
                              host='localhost', port='3307',
                              database='crypto')
my_cursor = conn.cursor()

print("Connect success")

app  = Flask(__name__)

def getDataFromApi():
    apiKey = "d1c3d25471f91eccd2a657dcc514cb1931b24c5966bdf468e70fa71026b66388"
    API_KEY = '&api_key=' + str(apiKey)
    limit = 'limit=5'
    currency = '&tsym=USD'
    url = 'https://min-api.cryptocompare.com/data/top/totaltoptiervolfull' + '?' + limit + currency + API_KEY
    response = requests.get(url).json()
    coins = response['Data']
    return coins

array_check = []

def insert_coin():
    coins = getDataFromApi()
    sql_check = "select * from coins"
    my_cursor.execute(sql_check)
    
    for c in my_cursor:
        array_check.append(c)
    print(array_check)
    if not array_check:
        for coin in coins:
            name = coin['CoinInfo']['Name']
            fullname = coin['CoinInfo']['FullName']
            image = coin['CoinInfo']['ImageUrl']
            marketcap = coin['RAW']['USD']['MKTCAP']
            price = coin['RAW']['USD']['PRICE']
            print({'name': name, 'fullname': fullname, 'image': image, 'marketcap': marketcap})
            sql_insert = "insert into coins(name, fullname, image, marketcap, price) values(%s, %s, %s, %s, %s)"
            value = (name, fullname, image, marketcap, price)
            my_cursor.execute(sql_insert, value)
            conn.commit()
    else:
           coins = getDataFromApi()
           for coin in coins:
                name = coin['CoinInfo']['Name']
                fullname = coin['CoinInfo']['FullName']
                image = coin['CoinInfo']['ImageUrl']
                marketcap = coin['RAW']['USD']['MKTCAP']
                price = coin['RAW']['USD']['PRICE']
                print({'name': name, 'fullname': fullname, 'image': image, 'marketcap': marketcap, 'price': price})
                sql_update = "update coins set name = %s, fullname=%s, image=%s, marketcap=%s, price =%s where name = %s"
                value = (name, fullname, image, marketcap, price, name)
                my_cursor.execute(sql_update, value)
                conn.commit()       


@app.before_first_request
def light_thread():
    def run():
        while True:
            insert_coin()
            time.sleep(300)

    thread = threading.Thread(target=run)
    thread.start()
    
@app.route('/data_json')
def data_json():
    coins = getDataFromApi()
    data = []
    for coin in coins:
        temp = {
            "id" : coin['CoinInfo']['Id'],
            "image" : coin['CoinInfo']['ImageUrl'],
            "fullname": coin['CoinInfo']['FullName'],
            "name": coin['CoinInfo']['Name'],
            "price": coin['RAW']['USD']['PRICE'],
            "marketcap": coin['RAW']['USD']['MKTCAP']
        }
        data.append(temp)
    return jsonify(data)

@app.route("/")
def home():
    coin = data_json()
    return render_template("index.html", coins=coin.json)

@app.route("/chart")
def chart():
    return render_template("chart.html")

if __name__ == '__main__':
    app.run(debug=True, port=80, threaded=True)
     
    
    