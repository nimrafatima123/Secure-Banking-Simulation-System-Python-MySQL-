
from db_config import get_connection
from security import hash_password_secure, check_password, validate_username, log_event


import getpass
import time

SESSION = {"user_id": None, "username": None, "role": None, "start_time": None}

LOCK_THRESHOLD = 3  # failed attempts before lock

def register():
    conn = get_connection()
    cur = conn.cursor()
    username = input("Choose username: ").strip()
    if not validate_username(username):
        print("Invalid username. Only letters, numbers, underscores. 3-30 chars.")
        return
    password = getpass.getpass("Choose password: ")
    if len(password) < 6:
        print("Password too short. Minimum 6 chars.")
        return
    pw_hash = hash_password_secure(password)

    try:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, pw_hash))
        conn.commit()
        print("Registration successful.")
        log_event("USER_REGISTER", username, "New user registered")
    except Exception as e:
        if "Duplicate" in str(e) or "UNIQUE" in str(e):
            print("Username already taken.")
        else:
            print("Registration error:", e)
    finally:
        cur.close()
        conn.close()

def login():
    conn = get_connection()
    cur = conn.cursor()
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    cur.execute("SELECT user_id, password_hash, failed_attempts, is_locked, role FROM users WHERE username=%s", (username,))
    row = cur.fetchone()
    if row is None:
        print("No such user.")
        log_event("FAILED_LOGIN", username, "Username not found")
        cur.close(); conn.close()
        return False

    user_id, pw_hash, failed_attempts, is_locked, role = row
    if is_locked:
        print("Account locked. Contact admin.")
        log_event("FAILED_LOGIN_LOCKED", username, "Attempted login to locked account")
        cur.close(); conn.close()
        return False

    if check_password(password, pw_hash.encode() if isinstance(pw_hash, str) else pw_hash):
        # reset failed attempts
        cur.execute("UPDATE users SET failed_attempts=0 WHERE user_id=%s", (user_id,))
        conn.commit()
        SESSION.update({"user_id": user_id, "username": username, "role": role, "start_time": time.time()})
        print(f"Login successful. Welcome, {username}!")
        log_event("SUCCESSFUL_LOGIN", username, "User logged in")
        cur.close(); conn.close()
        return True
    else:
        failed_attempts = failed_attempts + 1
        cur.execute("UPDATE users SET failed_attempts=%s WHERE user_id=%s", (failed_attempts, user_id))
        conn.commit()

        if failed_attempts >= LOCK_THRESHOLD:
            cur.execute("UPDATE users SET is_locked=1 WHERE user_id=%s", (user_id,))
            conn.commit()
            print("Account locked due to multiple failed attempts.")
            log_event("ACCOUNT_LOCKED", username, "Locked after failed logins")
        else:
            print("Incorrect password.")
            log_event("FAILED_LOGIN", username, f"Failed attempt {failed_attempts}")

        cur.close(); conn.close()
        return False

def logout():
    if SESSION["user_id"]:
        log_event("LOGOUT", SESSION["username"], "User logged out")
    SESSION.update({"user_id": None, "username": None, "role": None, "start_time": None})
    print("Logged out.")
