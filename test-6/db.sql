

-- Database 1: login_details
-- Purpose
-- This database is dedicated to managing user authentication and registration securely. Keeping user data in a separate database ensures better organization, security, and scalability.
-- Table: user
-- Purpose:
-- This table is used to store information about users who register on the platform. It contains essential fields for user authentication and profile management.

CREATE TABLE user (
    userid INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

INSERT INTO user (name, email, password) 
VALUES ('John Doe', 'john.doe@example.com', 'hashed_password');


-- ===================================================================================================================================================================================================================

-- Database 2: redeemcode_database
-- Purpose
-- This database manages the application's primary functionality: handling redeemable items and tracking user redemptions. It separates this functionality from the user authentication system for modularity and better scalability.
-- Table: items
-- Purpose:
-- Stores the list of redeemable items, their redeem codes, and additional metadata about the item (e.g., creation date and redemption count).

CREATE TABLE items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    redeem_code VARCHAR(255) NOT NULL,
    temp_count INT DEFAULT 0,
    created_at DATETIME NOT NULL
);

INSERT INTO items (name, redeem_code, temp_count, created_at)
VALUES ('Free Coffee Voucher', 'CODE12345', 0, NOW());

DELETE FROM items WHERE created_at < NOW() - INTERVAL 7 DAY;
DELETE FROM items WHERE temp_count > 10;



-- ==================================================================================================================================================================================================================

-- Table 2: user_redemptions
-- Purpose:
-- Tracks which user has redeemed which items and when. This prevents users from redeeming the same item multiple times and enables a history of redemptions.

USE redeemcode_database;

CREATE TABLE user_redemptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    item_id INT NOT NULL,
    redeemed_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES login_details.user(userid),
    FOREIGN KEY (item_id) REFERENCES items(id),
    UNIQUE(user_id, item_id)  -- Ensures each user can redeem an item only once
);
INSERT INTO user_redemptions (user_id, item_id, redeemed_at)
VALUES (user_id_value, item_id_value, NOW());

SELECT * FROM user_redemptions
WHERE user_id = user_id_value AND item_id = item_id_value;






-- ====================================================================================================================================================================================
----------------------------------------------------------------------------------------------------------------------------
-- ===================================================================================================================================================================================


-- Why Two Databases?
-- Modularity:

-- Separating user authentication (login_details) from application functionality (redeemcode_database) ensures that each database has a clear and focused purpose.
-- Security:

-- Sensitive user data (like hashed passwords) is stored in a dedicated database, reducing the risk of exposure if the other database is compromised.
-- Scalability:

-- By keeping the databases separate, they can scale independently. For instance:
-- If user registrations increase, the login_details database can scale without impacting the performance of redeem code management.
-- Similarly, if redeem code usage grows, the redeemcode_database can be optimized independently.
-- Maintainability:

-- Having separate databases makes it easier to manage, backup, and restore specific aspects of the application.

--  ===================================================================================================================================================================================

-- Why Two Databases?

-- Why Use These Tables?
-- user Table:

-- Central to user authentication and registration.
-- Prevents duplicate accounts and ensures secure password storage.
-- items Table:

-- Tracks all redeemable items and their details.
-- Enables filtering, sorting, and managing the availability of items.
-- user_redemptions Table:

-- Tracks individual user redemptions.
-- Prevents duplicate redemptions by users.
-- Allows developers to analyze user behavior and optimize the system accordingly.

-- =========================================================================================================================================================================================


