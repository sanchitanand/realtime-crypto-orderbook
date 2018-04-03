DROP DATABASE IF EXISTS mydb;
CREATE DATABASE mydb;
GRANT ALL ON mydb.* TO 'myapp'@'%';
DROP USER  'myapp'@'%' ;
CREATE USER 'myapp'@'%' IDENTIFIED BY 'password';
USE mydb;
GRANT ALL ON mydb.* TO 'myapp'@'%';
CREATE TABLE order_book ( type VARCHAR(3) NOT NULL, source VARCHAR(100) NOT NULL, last_update DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, pair VARCHAR(20) NOT NULL, price FLOAT NOT NULL, size FLOAT NOT NULL, PRIMARY KEY(pair,price,source,type));
DROP PROCEDURE IF EXISTS query_snapshot;
DELIMITER //
CREATE PROCEDURE query_snapshot (IN EXCH VARCHAR(100), IN INP_PAIR VARCHAR(20) , IN PRICE_GT FLOAT, IN PRICE_LT FLOAT ) 
BEGIN
IF EXCH IS NULL THEN
    select o.source, o.pair,o.type, o.price, o.size, o.last_update from mydb.order_book as o where o.price >= PRICE_GT and o.price <= PRICE_LT and o.size > 0 and o.pair = UPPER(INP_PAIR)  order by o.type,o.price;
ELSE
    select o.source, o.pair,o.type, o.price, o.size, o.last_update from mydb.order_book as o where o.price >= PRICE_GT and o.price <= PRICE_LT and o.pair = UPPER(INP_PAIR)  and UPPER(o.source) = UPPER(EXCH) order by o.type,o.price;
END IF;
END //
DELIMITER ;
DROP PROCEDURE IF EXISTS query_update;
DELIMITER //
CREATE PROCEDURE query_update (IN INP_PAIR VARCHAR(20) , IN LAST_REQ DATETIME) 
BEGIN
IF LAST_REQ IS NULL THEN
    select  o.pair,o.type, o.price, ROUND(CASE WHEN dups.size is null then o.size else dups.size end ,3)as size, o.last_update from mydb.order_book as o 
    LEFT JOIN (
 SELECT o.type as type ,o.pair as pair , o.price as price, SUM(size) as size FROM order_book as o where UPPER(pair) = UPPER(INP_PAIR) GROUP BY o.type,o.pair,o.price HAVING count(*) > 1 and size > 0
		) dups on o.type = dups.type and o.pair = dups.pair and o.price = dups.price 
        where (case when dups.size is not null then dups.size else o.size end)> 0 and UPPER(o.pair) = UPPER(INP_PAIR)  order by o.type,o.price;
ELSE
    select  o.pair,o.type, o.price,  ROUND(CASE WHEN dups.size is null then o.size else dups.size end ,3) as size, o.last_update from mydb.order_book as o 
    LEFT JOIN (
 SELECT o.type as type ,o.pair as pair , o.price as price, SUM(size) as size FROM order_book as o where UPPER(pair) = UPPER(INP_PAIR)  GROUP BY o.type,o.pair,o.price HAVING count(*) > 1 and size > 0
		) dups on o.type = dups.type and o.pair = dups.pair and o.price = dups.price
    where UPPER(o.pair) = UPPER(INP_PAIR) and o.last_update > LAST_REQ order by o.type,o.price;
END IF;
END //
DELIMITER ;
DROP PROCEDURE IF EXISTS query_pairs;
DELIMITER //
CREATE PROCEDURE query_pairs () 
BEGIN
	 select pair from order_book group by pair;
END //
DELIMITER ;
DROP PROCEDURE IF EXISTS query_date;
DELIMITER //
CREATE PROCEDURE query_date ()
BEGIN
	select max(last_update) from order_book;
END //
DELIMITER ; 






