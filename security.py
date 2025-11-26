

import bcrypt
import re
from db_config import get_connection

def hash_password_secure(password: str):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password: str, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

def validate_username(username: str):
    return bool(re.match(r"^[A-Za-z0-9_]{3,30}$", username))

def validate_amount(amount):
  
    return isinstance(amount, (int, float)) and amount > 0

def log_event(event_type: str, username: str, details: str):

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO system_logs (event_type, username, description) VALUES (%s, %s, %s)",
            (event_type, username, details)  # details → description
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("[LOGGING ERROR]", e)
