from bottle import get, post, run, request, response
import bottle
import sqlite3
import inspect
from urllib.parse import quote, unquote
import json

db = sqlite3.connect('krusty-db.sqlite')  
PORT = 8888
db.execute("PRAGMA foreign_keys = ON")

@post('/reset')
def reset():
    c = db.cursor()
    c.executescript(
        """
        PRAGMA foreign_keys = OFF;
        DELETE FROM customers;
        DELETE FROM cookies;
        DELETE FROM orders;
        DELETE FROM pallets;
        DELETE FROM order_specs;
        DELETE FROM ingredients;
        DELETE FROM storages;
        PRAGMA foreign_keys = ON;

        """
    )
    db.commit()
    return bottle.HTTPResponse(status=205, body={ "location": "/" })

@post('/customers')
def post_customer():
    try:
        customer = request.json
        c = db.cursor()
        c.execute(
            """
            INSERT
            INTO       customers(customer_name, customer_address)
            VALUES     (?, ?)
            RETURNING  customer_name
            """,
            [customer['name'], customer['address']]
        )
        found, = c.fetchone()
        db.commit()
        title = found
        url_encoded_title = quote(title)
        return bottle.HTTPResponse(status=201, body={ "location": f"/customers/{url_encoded_title}" })
    except sqlite3.IntegrityError as e:
        response.status = 400
        print(e)
        return ""

@get('/customer')
def get_customer():
    try:
        with db:
            c = db.cursor()
            c.execute(
                """
                SELECT  customer_name, customer_address
                FROM    customers

                """,
            )
            found = [{'customer_name': customer_name, 'customer_address': customer_address}
                     for customer_name, customer_address in c]
            return bottle.HTTPResponse(status=200, body={ "data": found})
    except Exception as e:
        print('Exception occured on line' + str(inspect.currentframe().f_lineno))
        print(e)
        response.status = 400
        return ''
    
@post('/storages')
def post_ingredient():
    try:
        ingredient = request.json
        c = db.cursor()
        c.execute(
            """
            INSERT
            INTO       storages(ingredient, unit)
            VALUES     (?, ?)
            RETURNING  ingredient
            """,
            [ingredient['ingredient'], ingredient['unit']]
        )
        found, = c.fetchone()
        db.commit()
        title = found
        url_encoded_title = quote(title)
        return bottle.HTTPResponse(status=201, body={ "location": f"/storages/{url_encoded_title}" })
    except sqlite3.IntegrityError as e:
        response.status = 400
        print(e)
        return ""
    
@get('/storages')
def get_ingredient():
    try:
        with db:
            c = db.cursor()
            c.execute(
                """
                SELECT  ingredient, store_quantity, unit
                FROM    storages
                ORDER BY ingredient

                """,
            )
            found = [{'ingredient': ingredient, 'quantity': store_quantity, 'unit': unit}
                     for ingredient, store_quantity, unit in c]
            return bottle.HTTPResponse(status=200, body={ 'data': found })
    except Exception as e:
        print('Exception occured on line' + str(inspect.currentframe().f_lineno))

        print(e)
        response.status = 400
        return ''

@post('/storages/<ingredient>/deliveries')
def post_ingredient(ingredient):
    try:
        deliveries = request.json
        c = db.cursor()
        c.execute(
            """
            UPDATE     storages
            SET        store_date = ?, store_quantity = store_quantity + ?, store_last_quantity = ?
            WHERE      ingredient = ?
    
            RETURNING  ingredient, store_quantity, unit
            """, 
            [deliveries['deliveryTime'], deliveries['quantity'], deliveries['quantity'], unquote(ingredient)]
        )
        found, = c.fetchall()
        ret = [{"ingredient": ingredient, "quantity": store_quantity, "unit": unit} 
        for ingredient, store_quantity, unit in c]
        db.commit()
        return bottle.HTTPResponse(status=201, body= {"data": ret})
    except sqlite3.IntegrityError as e:
        response.status = 400
        print(e)
        return ""

@post('/cookies')
def post_cookies():
    try:
        cookie = request.json
        c = db.cursor()
        c.execute(
            """
            INSERT
            INTO       cookies(c_name)
            VALUES     (?)
            RETURNING  c_name;
            """,
            [cookie['name']]   
        )
        found, = c.fetchone()
        for i in cookie['recipe']:
            c.execute(
                """
                INSERT 
                INTO ingredients(quantity, c_name, ingredient)
                VALUES (?, ?,?)
                """,
                [i['amount'],cookie['name'], i['ingredient']]
            )
        db.commit()
        title = found
        url_encoded_title = quote(title)
        return bottle.HTTPResponse(status=201, body={ "location": f"/cookies/{url_encoded_title}" })
    except sqlite3.IntegrityError as e:
        response.status = 400
        print(e)
        return ""
    
@get('/cookies')
def get_cookies():
    try:
        with db:
            c = db.cursor()
            c.execute(
                """
                WITH pallet_count(c_name, cnt) AS(
                    SELECT      c_name, count() as cnt
                    FROM        pallets
                    WHERE       blocked = 0
                    GROUP BY    c_name  
                )
                SELECT      cookies.c_name, coalesce(cnt, 0) as nbr
                FROM        cookies 
                LEFT JOIN   pallet_count on cookies.c_name = pallet_count.c_name
                """,
            )
            found = [{'name': c_name, 'pallets': nbr} for c_name, nbr in c]
            db.commit()
            if found:
                return bottle.HTTPResponse(status=200, body={"data": found})
            if not found:
                return bottle.HTTPResponse(status=400, body={'data': []})
    except Exception as e:
        print('Exception occured on line' + str(inspect.currentframe().f_lineno))

        print(e)
        response.status = 400
        return ''
    
@get('/cookies/<c_name>/recipe')
def get_cookies(c_name):
    try:
        with db:
            c = db.cursor()
            c.execute(
                """
                SELECT  ingredient, quantity, unit
                FROM    ingredients
                JOIN    storages
                USING   (ingredient)
                WHERE   c_name = ?

                """,
                [c_name]
            )
            found = [{'ingredient': ingredient, 'amount': quantity, 'unit': unit}
                     for ingredient, quantity, unit in c]
            db.commit()
            if (found):
                return bottle.HTTPResponse(status=200, body={ 'data': found })
            else:
                return bottle.HTTPResponse(status=404, body={ 'data': [] })
    except Exception as e:
        print('Exception occured on line' + str(inspect.currentframe().f_lineno))
        print(e)
        return {'data': ''}

@post('/pallets')
def post_pallets():
    try:
        pallet = request.json
        c = db.cursor()
        c.execute(
            """
            INSERT
            INTO       pallets(c_name)
            VALUES     (?)
            RETURNING  pallet_nbr
            """,
            [pallet['cookie']]
        )
        found, = c.fetchone()
        db.commit()
        return bottle.HTTPResponse(status=201, body={ "location": f"/pallets/{found}" })
    except sqlite3.IntegrityError as e:
        print(e)
        return bottle.HTTPResponse(status=422, body={"location": ""})

@get('/pallets')
def get_pallets():
    try:
        with db:
            response.content_type = 'application/json'
            query =  """
                SELECT pallet_nbr, c_name, date_produced, coalesce(blocked, 0) AS blocked
                FROM pallets
                WHERE 1=1
                """
            params = []
            if request.query.after:
                query += "AND date_produced > ?"
                params.append(request.query.after)
            if request.query.before:
                query += "AND date_produced < ?"
                params.append(request.query.before)
            if request.query.cookie:
                query += "AND c_name = ?"
                params.append(request.query.cookie)

            c = db.cursor() 
            c.execute(
                query, 
                params
            )
            db.commit()
            found = [{"id": pallet_nbr, "cookie": c_name, "productionDate": date_produced, "blocked": blocked}
                    for (pallet_nbr, c_name, date_produced, blocked) in c]
        return bottle.HTTPResponse(status=200, body={'data': found})
    except Exception as e:
        print(e)
        return bottle.HTTPResponse(status=400, body={''})

@post('/cookies/<cookie_name>/block')
def post_blockdate(cookie_name):
    try:
        dates = request.json
        c = db.cursor()
        if not dates:
            c.execute(
                """
                UPDATE pallets
                SET    blocked = 1 
                WHERE  c_name = ?     
                """,
                [unquote(cookie_name)]
            )    
        elif 'before' in dates and 'after' in dates:
            c.execute(
                """
                UPDATE pallets
                SET    blocked = 1 
                WHERE  c_name = ?
                AND    date_produced >= ?     
                AND    date_produced <= ?
                """,
                [unquote(cookie_name), dates['after'], dates['before']]
            )
        elif 'before' in dates:
            c.execute(
                """
                UPDATE pallets
                SET    blocked = 1 
                WHERE  c_name = ?     
                AND    date_produced <= ?
                """,
                [unquote(cookie_name), dates['before']]
            )
        elif 'after' in dates:
            c.execute(
                """
                UPDATE pallets
                SET    blocked = 1 
                WHERE  c_name = ?     
                AND    date_produced >= ? 
                """,
                [unquote(cookie_name), dates['after']]
            )
            
        db.commit()
        return bottle.HTTPResponse(status=201, body={''})
    except sqlite3.IntegrityError as e:
        print(e)
        return bottle.HTTPResponse(status=422, body={''})
    
@post('/cookies/<cookie_name>/unblock')
def post_unblockdate(cookie_name):
    try:
        dates = request.json
        c = db.cursor()
        if not dates:
            c.execute(
                """
                UPDATE pallets
                SET    blocked = 0 
                WHERE  c_name = ?     
                """,
                [unquote(cookie_name)]
            )   
        elif 'before' in dates and 'after' in dates:
            c.execute(
                """
                UPDATE pallets
                SET    blocked = 0 
                WHERE  c_name = ?
                AND    date_produced >= ?     
                AND    date_produced <= ?
                """,
                [unquote(cookie_name), dates['after'], dates['before']]
            )
        elif 'before' in dates:
            c.execute(
                """
                UPDATE pallets
                SET    blocked = 0 
                WHERE  c_name = ?     
                AND    date_produced <= ?
                """,
                [unquote(cookie_name), dates['before']]
            )
        elif 'after' in dates:
            c.execute(
                """
                UPDATE pallets
                SET    blocked = 0 
                WHERE  c_name = ?     
                AND    date_produced >= ? 
                """,
                [unquote(cookie_name), dates['after']]
            )

        db.commit()
        return bottle.HTTPResponse(status=201, body={''})
    except sqlite3.IntegrityError as e:
        print(e)
        return bottle.HTTPResponse(status=422, body={''})

            
run(host='localhost', port=8888)

