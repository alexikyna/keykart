create database keykart;
use keykart;

-- USERS TABLE
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin','staff','customer') NOT NULL DEFAULT 'customer',
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PRODUCTS TABLE
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category ENUM('game_key', 'in_game_currency', 'merch') NOT NULL,
    price_php DECIMAL(10,2) NOT NULL,
    price_usd DECIMAL(10,2) NOT NULL,
    price_krw DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0,
    description TEXT,
    image_url VARCHAR(255)
);

-- ORDERS TABLE
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_php DECIMAL(10,2),
    total_usd DECIMAL(10,2),
    total_krw DECIMAL(10,2),
    status ENUM('pending', 'completed', 'cancelled') DEFAULT 'pending',
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- ORDER ITEMS
CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    qty INT,
    price_at_purchase DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- KEY DELIVERIES (for digital keys)
CREATE TABLE key_deliveries (
    delivery_id INT AUTO_INCREMENT PRIMARY KEY,
    order_item_id INT,
    game_key VARCHAR(100),
    delivered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_item_id) REFERENCES order_items(order_item_id)
);

-- STOCK AUDIT
CREATE TABLE stock_audit (
    audit_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    change_type ENUM('add', 'deduct', 'revert'),
    change_qty INT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    by_user_id INT,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (by_user_id) REFERENCES users(user_id)
);

-- USER ARCHIVE (for deleted users)
CREATE TABLE user_archive (
    archived_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    username VARCHAR(50),
    email VARCHAR(100),
    role VARCHAR(10),
    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 1. Auto-deduct stock when order item is inserted
DELIMITER $$
CREATE TRIGGER trg_deduct_stock
AFTER INSERT ON order_items
FOR EACH ROW
BEGIN
    UPDATE products
    SET stock = stock - NEW.qty
    WHERE product_id = NEW.product_id;

    -- Audit log
    INSERT INTO stock_audit (product_id, change_type, change_qty, by_user_id)
    VALUES (NEW.product_id, 'deduct', NEW.qty, (SELECT user_id FROM orders WHERE order_id = NEW.order_id));
END$$
DELIMITER ;

-- 2. Log key delivery when new key is delivered
DELIMITER $$
CREATE TRIGGER trg_log_key_delivery
AFTER INSERT ON key_deliveries
FOR EACH ROW
BEGIN
    UPDATE orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    SET o.status = 'completed'
    WHERE oi.order_item_id = NEW.order_item_id;
END$$
DELIMITER ;

-- 3. Low stock alert (write to stock_audit with type 'alert' if stock < 3)
DELIMITER $$
CREATE TRIGGER trg_low_stock_alert
AFTER UPDATE ON products
FOR EACH ROW
BEGIN
    IF NEW.stock < 3 THEN
        INSERT INTO stock_audit (product_id, change_type, change_qty, by_user_id)
        VALUES (NEW.product_id, 'alert', NEW.stock, NULL);
    END IF;
END$$
DELIMITER ;

-- 4. Auto-calculate order total after order_items insertion
DELIMITER $$
CREATE TRIGGER trg_update_order_total
AFTER INSERT ON order_items
FOR EACH ROW
BEGIN
    UPDATE orders o
    SET o.total_php = (
        SELECT SUM(price_at_purchase * qty) FROM order_items WHERE order_id = o.order_id
    )
    WHERE o.order_id = NEW.order_id;
END$$
DELIMITER ;

-- 5. Archive user on delete (BEFORE DELETE)
DELIMITER $$
CREATE TRIGGER trg_archive_user
BEFORE DELETE ON users
FOR EACH ROW
BEGIN
    INSERT INTO user_archive (user_id, username, email, role)
    VALUES (OLD.user_id, OLD.username, OLD.email, OLD.role);
END$$
DELIMITER ;

-- 1. Place Order (simplified version)
DELIMITER $$
CREATE PROCEDURE sp_place_order(
    IN p_user_id INT,
    IN p_product_id INT,
    IN p_qty INT
)
BEGIN
    DECLARE prod_price DECIMAL(10,2);
    SELECT price_php INTO prod_price FROM products WHERE product_id = p_product_id;

    INSERT INTO orders (user_id, total_php, status) VALUES (p_user_id, 0, 'pending');
    SET @last_order_id = LAST_INSERT_ID();

    INSERT INTO order_items (order_id, product_id, qty, price_at_purchase)
    VALUES (@last_order_id, p_product_id, p_qty, prod_price);

    -- total will be recalculated by trigger
END$$
DELIMITER ;

-- 2. Cancel Order (reverts stock and updates order status)
DELIMITER $$
CREATE PROCEDURE sp_cancel_order(IN p_order_id INT)
BEGIN
    UPDATE orders SET status = 'cancelled' WHERE order_id = p_order_id;
    -- revert stock
    UPDATE products p
    JOIN order_items oi ON p.product_id = oi.product_id
    SET p.stock = p.stock + oi.qty
    WHERE oi.order_id = p_order_id;
    -- audit
    INSERT INTO stock_audit (product_id, change_type, change_qty)
    SELECT product_id, 'revert', qty FROM order_items WHERE order_id = p_order_id;
END$$
DELIMITER ;

-- 3. Update stock (admin/staff)
DELIMITER $$
CREATE PROCEDURE sp_update_stock(IN p_product_id INT, IN p_new_stock INT, IN p_user_id INT)
BEGIN
    UPDATE products SET stock = p_new_stock WHERE product_id = p_product_id;
    INSERT INTO stock_audit (product_id, change_type, change_qty, by_user_id)
    VALUES (p_product_id, 'add', p_new_stock, p_user_id);
END$$
DELIMITER ;

-- 4. Manage User Roles
DELIMITER $$
CREATE PROCEDURE sp_manage_user_roles(IN p_user_id INT, IN p_new_role ENUM('admin','staff','customer'))
BEGIN
    UPDATE users SET role = p_new_role WHERE user_id = p_user_id;
END$$
DELIMITER ;

-- 5. Generate Sales Report
DELIMITER $$
CREATE PROCEDURE sp_generate_sales_report(
    IN p_start_date DATE, IN p_end_date DATE
)
BEGIN
    SELECT o.order_id, u.username, o.order_date, o.total_php, o.status
    FROM orders o
    JOIN users u ON o.user_id = u.user_id
    WHERE o.order_date BETWEEN p_start_date AND p_end_date;
END$$
DELIMITER ;


-- Admin (full privileges)
CREATE USER 'adminuser'@'localhost' IDENTIFIED BY 'adminpass';
GRANT ALL PRIVILEGES ON keykart.* TO 'adminuser'@'localhost';

-- Staff (limited DML privileges, but not user management)
CREATE USER 'staffuser'@'localhost' IDENTIFIED BY 'staffpass';
GRANT SELECT, INSERT, UPDATE ON keykart.products TO 'staffuser'@'localhost';
GRANT SELECT, INSERT, UPDATE ON keykart.orders TO 'staffuser'@'localhost';
GRANT SELECT, INSERT, UPDATE ON keykart.order_items TO 'staffuser'@'localhost';
GRANT EXECUTE ON PROCEDURE keykart.sp_update_stock TO 'staffuser'@'localhost';
GRANT EXECUTE ON PROCEDURE keykart.sp_place_order TO 'staffuser'@'localhost';

-- Gamer (customer: can only select products, and insert orders)
CREATE USER 'gameruser'@'localhost' IDENTIFIED BY 'gamerpass';
GRANT SELECT ON keykart.products TO 'gameruser'@'localhost';
GRANT INSERT ON keykart.orders TO 'gameruser'@'localhost';
GRANT INSERT ON keykart.order_items TO 'gameruser'@'localhost';
GRANT EXECUTE ON PROCEDURE keykart.sp_place_order TO 'gameruser'@'localhost';

-- After creating the users as above:
FLUSH PRIVILEGES;


ALTER TABLE products
ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1;

DESCRIBE products;

INSERT INTO users (username, password, role, email) VALUES
('admin', 'admin123', 'admin', 'admin@keykart.com'),
('staff1', 'staffpass', 'staff', 'staff@keykart.com'),
('gamer1', 'gamerpass', 'customer', 'gamer1@email.com');

INSERT INTO products (name, category, price_php, price_usd, price_krw, stock, description)
VALUES ('Elden Ring Steam Key', 'game_key', 2500, 45, 60000, 10, 'PC Steam Key - Elden Ring');

-- Insert some products
INSERT INTO products (name, category, price_php, price_usd, price_krw, stock, description)
VALUES
('Genshin Genesis Crystals', 'in_game_currency', 500, 9, 12000, 50, 'In-game top-up for Genshin Impact'),
('Kirby Plush', 'merch', 1200, 22, 29000, 5, 'Soft Kirby Plush Toy');

ALTER TABLE users ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1;
