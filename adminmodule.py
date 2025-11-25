from dbconfig import getconnection
from security import logevent
from usermodule import SESSION

def require_admin(func):
    def wrapper(*args, **kwargs):
        if not SESSION["role"] or SESSION["role"] != "admin":
            print("Admin access required.")
            return
        return func(*args, **kwargs)
    return wrapper

@requireadmin
def viewlogs(limit=50):
    conn = getconnection(); cur = conn.cursor()
    cur.execute("SELECT timestamp, eventtype, username, details FROM logs ORDER BY timestamp DESC LIMIT %s", (limit,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    for r in rows:
        print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]}")

@requireadmin
def unlockuser():
    username = input("Username to unlock: ").strip()
    conn = getconnection(); cur = conn.cursor()
    cur.execute("UPDATE users SET locked=0, failedattempts=0 WHERE username=%s", (username,))
    conn.commit()
    cur.close(); conn.close()
    print(f"User {username} unlocked (if existed).")
    logevent("UNLOCK", username, f"Account unlocked by admin {SESSION['username']}")
