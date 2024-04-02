INSERT
INTO cookies(c_name)
VALUES ("Nut ring"), ("Nut cookie"), ("Amneris"), ("Tango"), ("Almond delight"), ("Berliner");

INSERT
INTO storages(ingredient, unit, store_quantity, store_date, store_last_quantity)
VALUES ('Flour', "g", 1000, "2023-03-13", 1000), ('Butter', "g", 500, "2023-03-12", 500),
('Icing sugar', "dl", 400, "2023-03-13", 400), ('Roasted, chopped nuts', "g", 600, "2023-03-12", 600),
('Fine-ground nuts', "g", 1500, "2023-03-13", 1500), ('Ground, roasted nuts', "g", 2000, "2023-03-12", 2000), ('Sugar', "dl", 2500, "2023-03-12", 2500),
('Egg whites', "g", 400, "2023-03-13", 400), ('Chocolate', "g", 100, "2023-03-12", 100);

INSERT 
INTO ingredients(quantity, c_name, ingredient)
VALUES (450, "Nut ring", "Flour"), (450, "Nut ring", "Butter"),
(190, "Nut ring", "Icing sugar"), (225, "Nut ring", "Roasted, chopped nuts"),
(750, "Nut cookie", "Fine-ground nuts"), (625, "Nut cookie", "Ground, roasted nuts"),
(125, "Nut cookie", "Bread crumbs"), (375, "Nut cookie", "Sugar"),
(3.5, "Nut cookie", "Egg whites"), (50, "Nut cookie", "Chocolate");


INSERT
INTO customers(customer_name, customer_address)
VALUES ("Finkakor AB", "Helsingborg"), ("Småbröd AB", "Malmö"), ("Kaffebröd AB", "Landskrona"),
("Bjudkakor AB", "Ystad"), ("Kalaskakor AB", "Trelleborg"), ("Partykakor AB", "Kristianstad"), 
("Gästkakor AB", "Hässleholm"), ("Skånekakor AB", "Perstorp");

INSERT
INTO orders(estimated_delivery, customer_id)
VALUES ("2023-04-30", (SELECT customer_id FROM customers WHERE customer_name="Kaffebröd AB")), 
("2023-04-15", (SELECT customer_id FROM customers WHERE customer_name="Partykakor AB"));

INSERT
INTO pallets(c_name)
VALUES ("Nut ring"), ("Nut cookie"), ("Tango");

