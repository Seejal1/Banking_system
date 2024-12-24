import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re

class BankingSystem:
    def __init__(self):
        self.customers = {}
        self.admin_credentials = {
            "username": "Arthur",
            "password_hash": hashlib.sha256("123".encode()).hexdigest()
        }
        self._initialize_sample_data()

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def _initialize_sample_data(self):
        # Sample customer data
        customers_data = [
            ("Boris", "ABC", "10 london road", [("current", 2000, 0)]),
            ("Chloe", "1+x", "99 queens road", [("current", 1000, 2.99), ("savings", 4000, 2.99)]),
            ("David", "aBC", "2 birmingham street", [("savings1", 200, 0.99), ("savings2", 5000, 4.99)])
        ]
        
        for username, password, address, accounts in customers_data:
            self.customers[username] = {
                "password_hash": self._hash_password(password),
                "address": address,
                "accounts": {}
            }
            
            for acc_type, balance, interest in accounts:
                self.customers[username]["accounts"][acc_type] = {
                    "balance": balance,
                    "interest_rate": interest,
                    "transactions": []
                }

    def _log_transaction(self, username: str, account_type: str, transaction_type: str, amount: float):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.customers[username]["accounts"][account_type]["transactions"].append(
            f"{timestamp} - {transaction_type}: ${amount:.2f}"
        )

    def authenticate(self, username: str, password: str) -> str:
        if username == self.admin_credentials["username"] and \
           self._hash_password(password) == self.admin_credentials["password_hash"]:
            return "admin"
        elif username in self.customers and \
             self._hash_password(password) == self.customers[username]["password_hash"]:
            return "customer"
        return "invalid"

    def transfer_money(self, from_user: str, to_user: str, amount: float) -> Tuple[bool, str]:
        if from_user not in self.customers or to_user not in self.customers:
            return False, "Invalid username"
        
        if amount <= 0:
            return False, "Invalid amount"

        from_account = next(iter(self.customers[from_user]["accounts"].items()))
        to_account = next(iter(self.customers[to_user]["accounts"].items()))
        
        if from_account[1]["balance"] < amount:
            return False, "Insufficient funds"

        # Process transfer
        from_account[1]["balance"] -= amount
        to_account[1]["balance"] += amount
        
        # Log transactions
        self._log_transaction(from_user, from_account[0], "Transfer Out", amount)
        self._log_transaction(to_user, to_account[0], "Transfer In", amount)
        
        return True, f"Successfully transferred ${amount:.2f}"

    def process_transaction(self, username: str, account_type: str, amount: float, 
                          transaction_type: str) -> Tuple[bool, str]:
        if username not in self.customers:
            return False, "Invalid username"
        
        if account_type not in self.customers[username]["accounts"]:
            return False, "Invalid account type"
            
        if amount <= 0:
            return False, "Invalid amount"

        account = self.customers[username]["accounts"][account_type]
        
        if transaction_type == "withdraw":
            if account["balance"] < amount:
                return False, "Insufficient funds"
            account["balance"] -= amount
        else:  # deposit
            account["balance"] += amount
            
        self._log_transaction(username, account_type, 
                            "Withdrawal" if transaction_type == "withdraw" else "Deposit", 
                            amount)
        return True, f"Successfully {'withdrew' if transaction_type == 'withdraw' else 'deposited'} ${amount:.2f}"

    def get_customer_summary(self, username: str) -> Optional[Dict]:
        return self.customers.get(username)

    def calculate_forecast(self, username: str) -> Optional[Dict]:
        if username not in self.customers:
            return None
            
        forecast = {}
        for acc_type, details in self.customers[username]["accounts"].items():
            future_balance = details["balance"] * (1 + details["interest_rate"] / 100)
            forecast[acc_type] = {
                "current_balance": details["balance"],
                "interest_rate": details["interest_rate"],
                "forecasted_balance": future_balance
            }
        return forecast

    def main_menu(self):
        while True:
            print("\n=== Banking System Login ===")
            username = input("Username (or 'exit' to quit): ").strip()
            
            if username.lower() == 'exit':
                break
                
            password = input("Password: ").strip()
            auth_status = self.authenticate(username, password)
            
            if auth_status == "admin":
                self._admin_menu()
            elif auth_status == "customer":
                self._customer_menu(username)
            else:
                print("Invalid credentials")

    def _admin_menu(self):
        while True:
            print("\n=== Admin Menu ===")
            print("1. Customer Summary\n2. Financial Forecast\n3. Transfer Money\n4. Exit")
            choice = input("Select option: ").strip()
            
            if choice == "1":
                username = input("Enter customer username: ")
                if summary := self.get_customer_summary(username):
                    print(f"\nUsername: {username}")
                    print(f"Address: {summary['address']}")
                    for acc_type, details in summary["accounts"].items():
                        print(f"\nAccount: {acc_type}")
                        print(f"Balance: ${details['balance']:.2f}")
                        print(f"Interest Rate: {details['interest_rate']}%")
                else:
                    print("Customer not found")

            elif choice == "2":
                username = input("Enter customer username: ")
                if forecast := self.calculate_forecast(username):
                    for acc_type, details in forecast.items():
                        print(f"\nAccount: {acc_type}")
                        print(f"Current Balance: ${details['current_balance']:.2f}")
                        print(f"Forecasted Balance: ${details['forecasted_balance']:.2f}")
                else:
                    print("Customer not found")

            elif choice == "3":
                from_user = input("Transfer from: ")
                to_user = input("Transfer to: ")
                try:
                    amount = float(input("Amount: $"))
                    success, message = self.transfer_money(from_user, to_user, amount)
                    print(message)
                except ValueError:
                    print("Invalid amount")

            elif choice == "4":
                break

    def _customer_menu(self, username: str):
        while True:
            print("\n=== Customer Menu ===")
            print("1. View Accounts\n2. Deposit\n3. Withdraw\n4. Transaction History\n5. Exit")
            choice = input("Select option: ").strip()
            
            if choice == "1":
                customer = self.get_customer_summary(username)
                for acc_type, details in customer["accounts"].items():
                    print(f"\nAccount: {acc_type}")
                    print(f"Balance: ${details['balance']:.2f}")
                    print(f"Interest Rate: {details['interest_rate']}%")

            elif choice in ["2", "3"]:
                acc_type = input("Enter account type: ")
                try:
                    amount = float(input("Amount: $"))
                    success, message = self.process_transaction(
                        username, acc_type, amount,
                        "withdraw" if choice == "3" else "deposit"
                    )
                    print(message)
                except ValueError:
                    print("Invalid amount")

            elif choice == "4":
                customer = self.get_customer_summary(username)
                for acc_type, details in customer["accounts"].items():
                    print(f"\nAccount: {acc_type}")
                    for transaction in details["transactions"]:
                        print(transaction)

            elif choice == "5":
                break

if __name__ == "__main__":
    bank = BankingSystem()
    bank.main_menu()