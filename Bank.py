from datetime import datetime
from datetime import date

trx_id = "TRX001"   # Global variable to keep track of the transaction ID


class Customer(object):
    """ Customer class: Stores all information about the customer. """

    def __init__(self, customer_id, name, age, pin, acc_id=None):
        self.customer_id = customer_id      # Customer's ID
        self.name = name                    # Customer's Name
        self.age = age                      # Customer's Age
        self.__pin = pin                    # Customer's PIN
        if acc_id is None:
            self.accounts = []              # List of Customer's Accounts
        else:
            self.accounts = [acc_id]

    def get_pin(self):
        return self.__pin

    def set_pin(self, pin):
        self.__pin = pin

    def pin_verify(self):
        """ Checks PIN entered by the customer with their actual PIN and returns True or False. """
        pin = ""
        while len(pin) != 4 or not pin.isdigit():
            pin = input("Enter your 4-digit PIN: ")
        print()

        if pin == self.get_pin():
            return True
        else:
            return False

    def change_pin(self):
        """ Changes customer's PIN after verifying his current PIN. """
        print("To change your PIN, we have to verify your current PIN first.")
        if self.pin_verify():
            pin = ""
            while len(pin) != 4 or not pin.isdigit():
                pin = input("Enter a new 4-digit PIN: ")
            print()
            self.set_pin(pin)
        else:
            print("Wrong PIN entered")
            print("PIN Remains Unchanged\n")

    def add_acc(self, acc_id):
        """ Add an account to the customer accounts list. """
        self.accounts.append(acc_id)

    def print_balance(self):
        """ Prints the Account ID, Balance and Type of each account the customer holds. """
        if self.accounts:
            print("Accounts:")
            for acc in self.accounts:
                print(acc)
        else:
            print("You have no accounts!")
        print()

    def choose_account(self):
        """
        Returns the index of the Account that the customer chooses.
        Has -1 as the return value if the customer decides to cancel choosing instead.
        """
        # Prints each account that the customer holds
        for index in range(len(self.accounts)):
            print(str(index + 1) + ". " + str(self.accounts[index]))
        print("\n0. Cancel\n")

        choice = -1
        # User input should be in the range of total accounts that he holds + 1 (for exit)
        while choice not in [n for n in range(len(self.accounts) + 1)]:
            print("Which account would you like to choose?")
            try:
                choice = int(input())
            except ValueError:
                print("Please only enter a number!")
                continue
        choice -= 1
        return choice

    def close_account(self):
        """ Closes a Customer's Account after verifying his PIN. """
        if not self.accounts:
            print("You have no accounts!")
        else:
            print("Choose an account to close:\n")
            choice = self.choose_account()

            # If choice is not exit
            if choice != -1:
                print("Please verify your PIN to confirm")
                if self.pin_verify():
                    print(self.accounts.pop(choice))
                    print("Account Closed Successfully")
                else:
                    print("Wrong PIN entered")
                    print("Account Close Unsuccessful. Returning to main menu...")
        print()

    def __str__(self):
        """ Returns a string with the Customer ID, Name, Age and a list of accounts that the customer holds. """
        result = "Customer ID: " + self.customer_id + "\nName: " + self.name + "\nAge: %2d" % self.age + "\nAccounts:\n"
        if self.accounts:
            for acc in self.accounts:
                result += str(acc) + "\n"
        else:
            result += "No Accounts\n"
        return result


class Account(object):
    """ Account class: Stores all information about an account. Has functions to be used for all types of Accounts. """

    def __init__(self, acc_id, balance=0.0, transactions=None):
        self.acc_id = acc_id
        self.balance = balance
        if transactions is None:
            self.transactions = []
        else:
            self.transactions = transactions

    def deposit(self, amount):
        """ Deposits amount into an account. """
        if amount <= 0.0:
            print("You can only deposit a positive value\n")
            return

        transaction = (get_next_trx_id(), self.acc_id, str(date.today()), "Deposit", "+"+str(amount))
        self.transactions.append(transaction)

        self.balance += amount

        print("Deposit Successful")

    def withdraw(self, amount):
        """
        Withdraws amount from an account. It checks for the type of Account passed.
        If the Account is a:
            Savings Account - It checks if the last withdraw or transfer transaction was made in the last 30 days.
            Current Account - No monthly transaction limit.
                              It checks if the resultant balance is less than the minimum balance limit.
        """
        if amount <= 0.0:
            print("You can only withdraw a positive value\n")
            return

        # If the Account is a Savings Account
        if isinstance(self, SavingAccount):
            last = -1

            # To find the last withdraw or transfer (removed from the account) transaction made by the account
            for index in range(len(self.transactions) - 1, -1, -1):
                if self.transactions[index][3] != "Deposit" and self.transactions[index][4].startswith("-"):
                    last = index
                    break

            # If a withdraw or transfer transaction was found
            if last != -1:
                # Get the date of the last withdraw or transfer transaction made by the current account
                last_trx_date = datetime.strptime(self.transactions[last][2], "%Y-%m-%d").date()

                # Difference between the today and the last_trx_date in days
                date_diff = (date.today() - last_trx_date).days

                if date_diff < 30:
                    print("You have already Withdrawn or Transferred this month.")
                    print("You can only Withdraw or Transfer once every 30 days in a Savings Account")
                    return

            # If the balance after withdrawing is less than 0
            if self.balance - amount < 0:
                print("Sorry, you can't withdraw that much")
                return

        # If the Account is a Checking Account
        if isinstance(self, CheckingAccount):
            # If the balance after withdrawing is less than the minimum balance limit
            if self.balance - amount < self.minimum_balance:
                print("Sorry, you can't withdraw that much")
                return

        transaction = (get_next_trx_id(), self.acc_id, str(date.today()), "Withdraw", "-"+str(amount))
        self.transactions.append(transaction)

        self.balance -= amount

        print("Withdrawal Successful")

    def print_transactions(self):
        """ Prints the last 5 transactions done by the Account. """
        last = len(self.transactions)
        first = last - 5
        if first < 0:
            first = 0

        if last == 0:
            print("No Transactions on this Account")
            print("\nCurrent Balance: %.2f" % self.balance)
            return

        print("Account ID: " + self.acc_id)
        print()
        print("Transactions:")
        for index in range(last, first, -1):
            print("TRXID: " + self.transactions[index - 1][0] +
                  " | Date: " + self.transactions[index - 1][2] +
                  " | Type: {:8}".format(self.transactions[index - 1][3]) +
                  " | Amount: {:>8}".format(self.transactions[index - 1][4]))

        print("\nCurrent Balance: %.2f" % self.balance)

    def __add__(self, param):
        """ Add param to the account balance. Allows int and float as the parameter. """
        if type(param) == int:  # convert ints to float
            param = float(param)
        if type(param) == float:
            self.balance += param
        else:
            print("Wrong Type")
            raise TypeError

    def __radd__(self, param):
        """ Add param to the account balance. Allows int and float as the parameter. """
        if type(param) == int:  # convert ints to float
            param = float(param)
        if type(param) == float:
            self.balance += param
        else:
            print("Wrong Type")
            raise TypeError

    def __sub__(self, param):
        """ Remove param from the account balance. Allows int and float as the parameter. """
        if type(param) == int:  # convert ints to float
            param = float(param)
        if type(param) == float:
            self.balance -= param
        else:
            print("Wrong Type")
            raise TypeError

    def __rsub__(self, param):
        """ Remove param from the account balance. Allows int and float as the parameter. """
        if type(param) == int:  # convert ints to float
            param = float(param)
        if type(param) == float:
            self.balance -= param
        else:
            print("Wrong Type")
            raise TypeError

    def __eq__(self, param):
        """ Compare two account objects for equality based on Account ID, return Boolean. """
        if isinstance(param, Account):
            return self.acc_id == param.acc_id
        else:
            print("Wrong Type")
            raise TypeError

    def __str__(self):
        """ Returns a string with the Account ID and Balance. """
        result = "ID: " + self.acc_id + " | Balance: %9.2f" % self.balance
        return result


class SavingAccount(Account):
    """ SavingAccount class: Subclass of Account. Has functions to be used for a Savings Account. """

    def __init__(self, acc_id, balance=0, transactions=None):
        Account.__init__(self, acc_id, balance, transactions)
        self.accType = "Savings"

    def transfer(self, amount, receiver_acc):
        """ Transfers amount into another account"""
        if amount <= 0.0:
            print("You can only transfer a positive value\n")
            return

        last = -1

        # To find the last withdraw or transfer transaction made by the account
        for index in range(len(self.transactions) - 1, -1, -1):
            if self.transactions[index][3] != "Deposit" and self.transactions[index][4].startswith("-"):
                last = index
                break

        # If a withdraw or transfer transaction was found
        if last != -1:
            # Get the date of the last transaction made by the current account
            last_trx_date = datetime.strptime(self.transactions[last][2], "%Y-%m-%d").date()

            # Difference between the today and the last_trx_date in days
            date_diff = (date.today() - last_trx_date).days

            if date_diff < 30:
                print("You have already Withdrawn or Transferred this month.")
                print("You can only Withdraw or Transfer once every 30 days in a Savings Account")
                return

        # If the balance after transferring is less than 0
        if self.balance - amount < 0:
            print("Sorry, you can't transfer that much")
            return

        # Update transactions for the current account
        transaction = (get_next_trx_id(), self.acc_id, str(date.today()), "Transfer", "-"+str(amount))
        self.transactions.append(transaction)

        # Update transactions for the receiver's account
        transaction = (get_next_trx_id(), receiver_acc.acc_id, str(date.today()), "Transfer", "+"+str(amount))
        receiver_acc.transactions.append(transaction)

        self.balance -= amount          # Remove from current account
        receiver_acc.balance += amount  # Add to receiver's account

        print("Transfer Successful")

    def __str__(self):
        """ Returns a string with the Account ID, Balance and Account Type. """
        result = Account.__str__(self) + " | Type: " + self.accType
        return result


class CheckingAccount(Account):
    """ CheckingAccount class: Subclass of Account. Has functions to be used for a Checking Account. """

    def __init__(self, acc_id, balance=0, transactions=None, minimum_balance=-1000):
        Account.__init__(self, acc_id, balance, transactions)
        self.accType = "Checking"
        self.minimum_balance = minimum_balance

    def transfer(self, amount, receiver_acc):
        """ Transfers amount from one account (self) into another account (receiver account). """
        if amount <= 0.0:
            print("You can only transfer a positive value\n")
            return

        # If the balance after transferring is less than 0
        if self.balance - amount < self.minimum_balance:
            print("Sorry, you can't transfer that much")
            return

        # Update transactions for the current account
        transaction = (get_next_trx_id(), self.acc_id, str(date.today()), "Transfer", "-"+str(amount))
        self.transactions.append(transaction)

        # Update transactions for the receiver's account
        transaction = (get_next_trx_id(), receiver_acc.acc_id, str(date.today()), "Transfer", "+"+str(amount))
        receiver_acc.transactions.append(transaction)

        self.balance -= amount          # Remove from current account
        receiver_acc.balance += amount  # Add to receiver's account

        print("Transfer Successful")

    def __str__(self):
        """ Returns a string with the Account ID, Balance and Account Type. """
        result = Account.__str__(self) + " | Type: " + self.accType
        return result


def get_next_trx_id():
    """ Returns the next transaction ID. """
    global trx_id
    trx_id = "TRX{:03}".format(int(trx_id[3:]) + 1)
    return trx_id


def create_savings_account(customer, accounts):
    """ Checks the age of the customer and creates a savings account for the customer if he is eligible. """

    # Find the next Unique ID in accounts
    unqid = "AC{:03}".format(int(max(accounts)[2:]) + 1)

    # Check if the customer is eligible to open a Savings Account
    if customer.age >= 14:
        # Creates a new SavingAccount object and stores it in the accounts dictionary with the Account ID as key
        accounts[unqid] = SavingAccount(acc_id=unqid)
        # Add the newly created Account to the customer
        customer.add_acc(accounts[unqid])

        print("Account created successfully!\n")
        print(accounts[unqid])
    else:
        print("You should be 14 years or older to open a Savings Account!")

    print()


def create_checking_account(customer, accounts):
    """ Checks the age of the customer and creates a checking account for the customer if he is eligible. """

    # Find the next Unique ID in accounts
    unqid = "AC{:03}".format(int(max(accounts)[2:]) + 1)

    # Check if the customer is eligible to open a Checking Account
    if customer.age >= 18:
        # Creates a new CheckingAccount object and stores it in the accounts dictionary with the Account ID as key
        accounts[unqid] = CheckingAccount(acc_id=unqid)
        # Add the newly created Account to the customer
        customer.add_acc(accounts[unqid])

        print("Account created successfully!\n")
        print(accounts[unqid])
    else:
        print("You should be 18 years or older to open a Checking Account!")

    print()


def update_files(customers):
    """
    Updates the files:
        customers.txt            -  With the information about each Customer
        accounts.txt             -  With the information about each Accounts
        accountsTransactions.txt -  With the information about each Transaction
    """

    # Open files to write data of all the Customers and Accounts
    try:
        customers_file = open("customers.txt", "w")
        accounts_file = open("accounts.txt", "w")
        transactions_file = open("accountsTransactions.txt", "w")
    except IOError:
        print("File could not be opened.")
        return

    # Writes details of each customer, accounts and transactions to the files
    for key in customers:
        line = customers[key].customer_id + " " + customers[key].name + " %d" % customers[key].age + " " + customers[key].get_pin() + " "

        # Write the customer detail only if he has an account
        for acc in customers[key].accounts:
            # Write the details of the customer to the file customer.txt
            print(line + acc.acc_id, file=customers_file)

            # Write the details of the account to the file accounts.txt
            line2 = acc.acc_id + " " + acc.accType + " %.2f" % acc.balance
            print(line2, file=accounts_file)

            # Writes details of each transaction to the file accountsTransactions.txt
            for transaction in acc.transactions:
                print(" ".join(transaction), file=transactions_file)

    # Close all the files
    customers_file.close()
    accounts_file.close()
    transactions_file.close()


def menu(customer, allcustomers, accounts):
    """ Displays the menu after logging in and calls the respective functions as the user chooses. """

    while True:
        print("1. Create a New Account")
        print("2. View Balance")
        print("3. Deposit")
        print("4. Withdraw")
        print("5. Transfer")
        print("6. View Transactions")
        print("7. Close an Account")
        print("8. Change PIN")
        print("9. Logout")

        menu_choice = ""
        while menu_choice not in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            menu_choice = input("Enter your choice: ")
        print()

        menu_choice = int(menu_choice)

        # Choice 1: Create a New Account
        if menu_choice == 1:
            print("Which type of account would you like to make?")
            print("1. Savings Account")
            print("2. Checking Account")

            choice = ""
            while choice not in ["1", "2"]:
                choice = input("Enter your choice: ")
            print()

            # Customer chooses Savings Account
            if choice == "1":
                create_savings_account(customer, accounts)
            # Customer chooses Checking Account
            else:
                create_checking_account(customer, accounts)

        # Choice 2: View Balance
        elif menu_choice == 2:
            customer.print_balance()

        # Choice 3: Deposit
        elif menu_choice == 3:
            # If customer has no accounts
            if not customer.accounts:
                print("You have no accounts!")
            else:
                print("Choose an account to deposit to:\n")
                choice = customer.choose_account()

                # If choice is not exit
                if choice != -1:
                    amount = ""
                    while not amount.isdigit():
                        amount = input("Enter amount to deposit: ")
                    print()

                    amount = float(amount)
                    customer.accounts[choice].deposit(amount)
            print()

        # Choice 4: Withdraw
        elif menu_choice == 4:
            # If customer has no accounts
            if not customer.accounts:
                print("You have no accounts!")
            else:
                print("Choose an account to withdraw from:\n")
                choice = customer.choose_account()

                # If choice is not exit
                if choice != -1:
                    amount = ""
                    while not amount.isdigit():
                        amount = input("Enter amount to withdraw: ")
                    print()

                    amount = float(amount)
                    customer.accounts[choice].withdraw(amount)
            print()

        # Choice 5: Transfer
        elif menu_choice == 5:
            # If customer has no accounts
            if not customer.accounts:
                print("You have no accounts!")
            else:
                print("Choose an account to transfer from:\n")
                choice = customer.choose_account()

                # If choice is not exit
                if choice != -1:
                    print("Choose a customer to transfer to:\n")

                    # Choose customer to transfer to
                    for key in allcustomers:
                        print("ID: " + key + " | Name: " + allcustomers[key].name)
                    print()
                    customer_id = ""
                    while customer_id not in [key for key in allcustomers]:
                        customer_id = input("Enter Customer ID: ")

                    # Choose account of the selected customer to transfer to
                    print("Choose an account to transfer to:\n")
                    acc = allcustomers[customer_id].choose_account()

                    # If choice is not exit
                    if choice != -1:
                        amount = ""
                        while not amount.isdigit():
                            amount = input("Enter amount to transfer: ")
                        print()

                        amount = float(amount)
                        customer.accounts[choice].transfer(amount, allcustomers[customer_id].accounts[acc])
            print()

        # Choice 6: View Transactions
        elif menu_choice == 6:
            # If customer has no accounts
            if not customer.accounts:
                print("You have no accounts!")
            else:
                print("Choose an account to view transactions:\n")
                choice = customer.choose_account()
                print()

                # If choice is not exit
                if choice != -1:
                    customer.accounts[choice].print_transactions()

            print()

        # Choice 7: Close an Account
        elif menu_choice == 7:
            customer.close_account()

        # Choice 9: Change PIN
        elif menu_choice == 8:
            customer.change_pin()

        # Choice 9: Logout
        else:
            break


def create_bank_obj(customers, accounts):
    """ Creates previous customer objects and Account objects with information from the files. """

    # Open files to get data to create all the previous Customers and Accounts
    try:
        customers_file = open("customers.txt", "r")
        accounts_file = open("accounts.txt", "r")
        transactions_file = open("accountsTransactions.txt", "r")
    except IOError:
        print("File could not be opened.")
        return

    # Create all the account objects and store them in the accounts dictionary with their ID as the key
    for line in accounts_file:
        record = line.strip().split()

        if record[1] == 'Savings':
            accounts[record[0]] = SavingAccount(acc_id=record[0], balance=float(record[2]))
        else:
            accounts[record[0]] = CheckingAccount(acc_id=record[0], balance=float(record[2]))

    # Create all the customer objects and store them in the customers dictionary with their ID as the key
    for line in customers_file:
        record = line.strip().split()

        # If the Customer object already exists, add the Account to the customer
        if record[0] in customers:
            customers[record[0]].add_acc(accounts[record[4]])
        # If the Customer object does not exist, create a Customer with the Account
        else:
            customers[record[0]] = Customer(customer_id=record[0],
                                            name=record[1],
                                            age=int(record[2]),
                                            pin=record[3],
                                            acc_id=accounts[record[4]])

    global trx_id
    trx_id = "TRX001"

    # Reads each transaction from the transactions file and add them to their respective accounts
    for line in transactions_file:
        record = line.strip().split()

        # To get the max Transaction ID
        if trx_id < record[0]:
            trx_id = record[0]

        # Store the transaction information as a tuple
        transaction = tuple(record)

        # Add the transaction to the respective account, record[1] is the Account ID of the transaction
        accounts[record[1]].transactions.append(transaction)

    # Close all the files
    customers_file.close()
    accounts_file.close()
    transactions_file.close()


def main():
    """ Main function. """

# =============================================================================================
#                                   Create Previous Instances
# =============================================================================================

    customers = {}  # Dictionary to store all the customer objects
    accounts = {}   # Dictionary to store all the account objects

    create_bank_obj(customers, accounts)

# =============================================================================================
#                                           Main Menu
# =============================================================================================

    while True:
        print("1. Create an Account")
        print("2. Login to an Account")
        print("3. Exit")

        choice = ""
        while choice not in ["1", "2", "3"]:
            choice = input("Enter your choice: ")
        print()

        # Choice 1: Create an Account
        if choice == "1":
            name = ""
            age = ""
            pin = ""

            while not name.isalpha():
                name = input("Enter your first name (only letters): ")

            while not age.isdigit():
                age = input("Enter your age: ")

            while len(pin) != 4 or not pin.isdigit():
                pin = input("Enter a 4-digit PIN: ")

            # Find the next Unique ID in customers
            unqid = "C{:03}".format(int(max(customers)[1:]) + 1)

            # Creates a new Customer object and stores it in the customers dictionary with the Customer ID as the key
            customers[unqid] = Customer(customer_id=unqid, name=name, age=int(age), pin=pin)

            print("\nAccount created successfully!\n")
            print(customers[unqid])

        # Choice 2: Login to an Account
        elif choice == "2":
            customer_id = input("Enter your ID: ")

            if customer_id in customers:

                if customers[customer_id].pin_verify():
                    print("Login Successful\n")
                    menu(customers[customer_id], customers, accounts)  # Main menu function after login
                else:
                    print("Wrong PIN entered\n")

            else:
                print("Account does not exist\n")

        # Choice 3: Exit
        else:
            break

        update_files(customers)

    print("Thank you for using our services. Exiting Bank...")
    return


# Call the main function
main()
