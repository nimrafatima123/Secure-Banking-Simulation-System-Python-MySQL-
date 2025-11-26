
from user_module import register, login, logout, SESSION
from banking_ops import check_balance, deposit, withdraw, transfer, history
from admin_module import view_logs, unlock_user

def guest_menu():
    print("\n Secure Banking ")
    print("1. Register")
    print("2. Login")
    print("3. Exit")
    return input("Choice: ").strip()

def user_menu():
    print(f"\n--- Banking Menu ({SESSION['username']}) ---")
    print("1. Check Balance")
    print("2. Deposit")
    print("3. Withdraw")
    print("4. Transfer")
    print("5. Transaction History")
    if SESSION['role'] == 'admin':
        print("6. View Logs (Admin)")
        print("7. Unlock User (Admin)")
        print("8. Logout")
    else:
        print("6. Logout")
    return input("Choice: ").strip()

def main():
    while True:
        if not SESSION["user_id"]:
            ch = guest_menu()
            if ch == "1":
                register()
            elif ch == "2":
                if login():
                    continue
            elif ch == "3":
                print("Goodbye.")
                break
            else:
                print("Invalid choice.")
        else:
            ch = user_menu()
            if ch == "1":
                check_balance()
            elif ch == "2":
                deposit()
            elif ch == "3":
                withdraw()
            elif ch == "4":
                transfer()
            elif ch == "5":
                history()
            elif ch == "6" and SESSION['role']=='admin':
                view_logs()
            elif ch == "7" and SESSION['role']=='admin':
                unlock_user()
            elif (ch == "6" and SESSION['role']!='admin') or (ch == "8" and SESSION['role']=='admin'):
                logout()
            else:
                print("Invalid choice.")

if __name__ == "__main__":
    main()
