
import mysql.connector

config = {
    "host": "localhost",
    "user": "root",
    "password": "yahyeet123"   
}

conn = mysql.connector.connect(**config)
cur = conn.cursor()

cur.execute("CREATE DATABASE IF NOT EXISTS banking_system")
cur.execute("USE banking_system")


cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    balance DECIMAL(12,2) DEFAULT 0.00,
    failed_attempts INT DEFAULT 0,
    is_locked BOOLEAN DEFAULT FALSE,
    role VARCHAR(20) DEFAULT 'customer'
)
""")


cur.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    tx_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    tx_type VARCHAR(50),
    amount DECIMAL(12,2),
    tx_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
)
""")


cur.execute("""
CREATE TABLE IF NOT EXISTS system_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(50),
    username VARCHAR(100),
    description TEXT,
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
cur.close()
conn.close()
print("Database and tables created (banking_system).")
