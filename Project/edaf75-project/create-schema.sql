DROP TABLE IF EXISTS order_specs;
DROP TABLE IF EXISTS cookies;
DROP TABLE IF EXISTS ingredients;
DROP TABLE IF EXISTS storages;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS pallets;
DROP TABLE IF EXISTS customers;

CREATE TABLE cookies (
    c_name  TEXT,
    PRIMARY KEY (c_name)
);

CREATE TABLE orders (
    order_id            TEXT DEFAULT (lower(hex(randomblob(16)))),
    estimated_delivery  DATE,
    date_delivery       DATE,
    time_delivery       TIME,
    customer_id         TEXT,
    PRIMARY KEY (order_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE customers (
    customer_id         TEXT DEFAULT (lower(hex(randomblob(16)))),
    customer_name       TEXT,
    customer_address    TEXT,
    PRIMARY KEY (customer_id)
);

CREATE TABLE pallets (
    pallet_nbr      TEXT DEFAULT (lower(hex(randomblob(16)))),
    date_produced   DATETIME DEFAULT CURRENT_TIMESTAMP,
    order_id        TEXT,
    c_name          TEXT,
    blocked         INTEGER DEFAULT 0,         
    PRIMARY KEY (pallet_nbr),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (c_name) REFERENCES cookies(c_name)
);

CREATE TABLE order_specs (
    c_name            TEXT,
    order_id        TEXT,
    PRIMARY KEY (c_name, order_id),
    FOREIGN KEY (c_name) REFERENCES cookies(c_name),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE ingredients (
    quantity        FLOAT, 
    c_name          TEXT,
    ingredient      TEXT,
    PRIMARY KEY (c_name, ingredient),
    FOREIGN KEY (c_name) REFERENCES cookies(c_name),
    FOREIGN KEY (ingredient) REFERENCES storages(ingredient)
);

CREATE TABLE storages (
    ingredient          TEXT,
    unit                TEXT,
    store_quantity      INTEGER DEFAULT 0,
    store_date          DATETIME,
    store_last_quantity INT,
    PRIMARY KEY (ingredient)
);

CREATE TRIGGER IF NOT EXISTS ingredient_check
BEFORE INSERT ON pallets
WHEN 
    (SELECT store_quantity-(quantity*54)
    FROM storages
    JOIN ingredients USING (ingredient)
    WHERE c_name = NEW.c_name) < 0
BEGIN
    SELECT RAISE (ROLLBACK, "Not enough of ingredients in storage");
END;

CREATE TRIGGER IF NOT EXISTS storage_update
AFTER INSERT ON pallets
BEGIN
    UPDATE storages
    SET store_quantity = vals
    FROM (
    SELECT ingredient as ingred, (store_quantity-(quantity*54)) AS vals 
    FROM storages
    JOIN ingredients USING (ingredient)
    WHERE c_name = NEW.c_name
) WHERE storages.ingredient = ingred;
END;

CREATE TRIGGER IF NOT EXISTS storage_check
BEFORE UPDATE ON storages
WHEN (SELECT NEW.store_quantity FROM storages) < 0
BEGIN
    SELECT RAISE(ROLLBACK, "negative value before insert");
END;





