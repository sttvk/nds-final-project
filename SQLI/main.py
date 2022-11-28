import sqlite3, os
from flask import Flask, jsonify, render_template, request, g

app = Flask(__name__)
app.database = "sample.db"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/restock')
def restock():
    return render_template('restock.html')

@app.route('/api/v1.0/storeAPI', methods=['GET', 'POST'])
def storeapi():
    if request.method == 'GET':
        g.db = connect_db()
        curs = g.db.execute("SELECT * FROM shop_items")
        cur2 = g.db.execute("SELECT * FROM employees")
        items = [{'items':[dict(name=row[0], quantity=row[1], price=row[2]) for row in curs.fetchall()]}]
        empls = [{'employees':[dict(username=row[0], password=row[1]) for row in cur2.fetchall()]}]
        g.db.close()
        return jsonify(items+empls)

    elif request.method == 'POST':
        g.db = connect_db()
        name,quan,price = (request.json['name'],request.json['quantity'],request.json['price'])
        curs = g.db.execute("""INSERT INTO shop_items(name, quantitiy, price) VALUES(?,?,?)""", (name, quan, price))
        g.db.commit()
        g.db.close()
        return jsonify({'status':'OK','name':name,'quantity':quan,'price':price})

@app.route('/api/v1.0/storeAPI/<item>', methods=['GET'])
def searchAPI(item):
    g.db = connect_db()
    #curs = g.db.execute("SELECT * FROM shop_items WHERE name=?", item) #The safe way to actually get data from db
    curs = g.db.execute("SELECT * FROM shop_items WHERE name = '%s'" %item)
    results = [dict(name=row[0], quantity=row[1], price=row[2]) for row in curs.fetchall()]
    g.db.close()
    return jsonify(results)

def connect_db():
    return sqlite3.connect(app.database)

if __name__ == "__main__":
    if not os.path.exists(app.database):
        with sqlite3.connect(app.database) as connection:
            c = connection.cursor()
            c.execute("""CREATE TABLE shop_items(name TEXT, quantitiy TEXT, price TEXT)""")
            c.execute('INSERT INTO shop_items VALUES("Apples", "90", "150")')
            c.execute('INSERT INTO shop_items VALUES("Bananas", "40", "80")')
            c.execute('INSERT INTO shop_items VALUES("Oranges", "120", "200")')
            connection.commit()
            connection.close()

    app.run(host='0.0.0.0', port=8080)
