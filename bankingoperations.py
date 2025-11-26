
from db_config import get_connection
from security import validate_amount, log_event
from user_module import SESSION

def require_login(func):
    def wrapper(*args, **kwargs):
        if not SESSION["user_id"]:
            print("Please login first.")
            return None
        return func(*args, **kwargs)
    return wrapper

@require_login
def check_balance():
    uid = SESSION["user_id"]
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE user_id=%s", (uid,))
    row = cur.fetchone()
    cur.close(); conn.close()
    print(f"Your balance: ₹{row[0]:.2f}")

@require_login
def deposit():
    uid = SESSION["user_id"]
    try:
        amount = float(input("Amount to deposit: "))
    except:
        print("Invalid number.")
        return
    if not validate_amount(amount):
        print("Enter positive amount.")
        return
    conn = get_connection(); cur = conn.cursor()
    cur.execute("UPDATE users SET balance = balance + %s WHERE user_id=%s", (amount, uid))
    cur.execute("INSERT INTO transactions (user_id, tx_type, amount) VALUES (%s,%s,%s)", (uid, "DEPOSIT", amount))
    conn.commit()
    cur.close(); conn.close()
    print(f"Deposited ₹{amount:.2f}")
    log_event("DEPOSIT", SESSION["username"], f"Deposited ₹{amount:.2f}")

@require_login
def withdraw():
    uid = SESSION["user_id"]
    try:
        amount = float(input("Amount to withdraw: "))
    except:
        print("Invalid number.")
        return
    if not validate_amount(amount):
        print("Enter positive amount.")
        return
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE user_id=%s", (uid,))
    balance = float(cur.fetchone()[0])
    if amount > balance:
        print("Insufficient funds.")
        cur.close(); conn.close()
        log_event("FAILED_WITHDRAW", SESSION["username"], f"Tried withdraw ₹{amount:.2f} with balance ₹{balance:.2f}")
        return
    cur.execute("UPDATE users SET balance = balance - %s WHERE user_id=%s", (amount, uid))
    cur.execute("INSERT INTO transactions (user_id, tx_type, amount) VALUES (%s,%s,%s)", (uid, "WITHDRAW", amount))
    conn.commit(); cur.close(); conn.close()
    print(f"Withdrew ₹{amount:.2f}")
    log_event("WITHDRAW", SESSION["username"], f"Withdrew ₹{amount:.2f}")

@require_login
def transfer():
    uid = SESSION["user_id"]
    receiver = input("Receiver username: ").strip()
    try:
        amount = float(input("Amount to transfer: "))
    except:
        print("Invalid number.")
        return
    if not validate_amount(amount):
        print("Enter positive amount.")
        return
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE username=%s", (receiver,))
    r = cur.fetchone()
    if r is None:
        print("Receiver not found.")
        cur.close(); conn.close()
        return
    receiver_id = r[0]
    cur.execute("SELECT balance FROM users WHERE user_id=%s", (uid,))
    balance = float(cur.fetchone()[0])
    if amount > balance:
        print("Insufficient funds.")
        cur.close(); conn.close()
        return
 
    try:
        cur.execute("UPDATE users SET balance = balance - %s WHERE user_id=%s", (amount, uid))
        cur.execute("UPDATE users SET balance = balance + %s WHERE user_id=%s", (amount, receiver_id))
        cur.execute("INSERT INTO transactions (user_id, tx_type, amount) VALUES (%s,%s,%s)", (uid, "TRANSFER_OUT", amount))
        cur.execute("INSERT INTO transactions (user_id, tx_type, amount) VALUES (%s,%s,%s)", (receiver_id, "TRANSFER_IN", amount))
        conn.commit()
        print(f"Transferred ₹{amount:.2f} to {receiver}")
        log_event("TRANSFER", SESSION["username"], f"Transferred ₹{amount:.2f} to {receiver}")
        # Fraud alert threshold
        if amount >= 50000:  # threshold example
            log_event("FRAUD_ALERT", SESSION["username"], f"High-value transfer ₹{amount:.2f} to {receiver}")
            print("⚠ Fraud alert logged for high-value transfer.")
    except Exception as e:
        conn.rollback()
        print("Transfer failed:", e)
    finally:
        cur.close(); conn.close()

@require_login
def history():
    uid = SESSION["user_id"]
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT tx_time, tx_type, amount FROM transactions WHERE user_id=%s ORDER BY tx_time DESC LIMIT 20", (uid,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    if not rows:
        print("No transactions found.")
        return
    print("Time | Type | Amount")
    for r in rows:
        print(f"{r[0]} | {r[1]} | ₹{r[2]:.2f}")
