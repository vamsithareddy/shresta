import sqlite3
import re
from datetime import datetime
from tabulate import tabulate

# Function to create a database connection with a timeout
def create_connection():
    return sqlite3.connect('loans_investments.db', timeout=10)

# Function to create tables
def create_tables():
    with create_connection() as conn:
        cursor = conn.cursor()
        
        # Creating tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Account (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Holder_Name TEXT NOT NULL,
            Bank_Name TEXT NOT NULL,
            IFSC TEXT NOT NULL,
            Number TEXT NOT NULL,
            Branch TEXT NOT NULL,
            Account_Type TEXT NOT NULL
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Borrower (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Mobile TEXT NOT NULL,
            Email TEXT NOT NULL,
            Address TEXT NOT NULL,
            Pan TEXT NOT NULL,
            Account_Id INTEGER,
            Aadhaar TEXT NOT NULL,
            FOREIGN KEY (Account_Id) REFERENCES Account (Id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Facilitator (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL,
            pan TEXT NOT NULL,
            account_id INTEGER,
            aadhaar TEXT NOT NULL,
            FOREIGN KEY (account_id) REFERENCES Account (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Investor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL,
            pan TEXT NOT NULL,
            account_id INTEGER,
            aadhaar TEXT NOT NULL,
            legal_heir_name TEXT,
            legal_heir_pan TEXT,
            FOREIGN KEY (account_id) REFERENCES Account (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Partner (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL,
            pan TEXT NOT NULL,
            account_id INTEGER,
            aadhaar TEXT NOT NULL,
            FOREIGN KEY (account_id) REFERENCES Account (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Firm (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL,
            pan TEXT NOT NULL,
            account_id INTEGER,
            registered_date DATE NOT NULL,
            members INTEGER NOT NULL,
            percent_owned REAL NOT NULL,
            firm_state TEXT NOT NULL,
            FOREIGN KEY (account_id) REFERENCES Account (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Asset (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_type TEXT NOT NULL,
            asset_mode TEXT NOT NULL,
            holder_name TEXT NOT NULL,
            deed_id TEXT NOT NULL,
            size REAL NOT NULL,
            units TEXT NOT NULL
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Loan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        recipient TEXT NOT NULL,
        principal REAL NOT NULL DEFAULT 0,
        interest_rate REAL NOT NULL,
        interest_frequency TEXT NOT NULL,
        interest_expected REAL,
        interest_realized REAL,
        interest_paid_up REAL,
        expenses REAL NOT NULL DEFAULT 0,
        loan_state TEXT NOT NULL,
        asset_id INTEGER,
        FOREIGN KEY (asset_id) REFERENCES Asset(id)
    )
    ''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS Transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        transaction_type TEXT CHECK (
                            transaction_type IN (
                                'PRINCIPAL FROM INVESTOR', 'PRINCIPAL TO INVESTOR', 
                                'PRINCIPAL TO BORROWER', 'PRINCIPAL FROM BORROWER', 
                                'INTEREST FROM BORROWER', 'INTEREST TO INVESTOR', 
                                'BUSINESS EXPENSES'
                            )
                        ),
                        business_expense_subtype TEXT CHECK (
                            (transaction_type != 'BUSINESS EXPENSES') OR 
                            (business_expense_subtype IN ('Legal', 'Travel', 'Registration', 'Brokerage', 'Other'))
                        ),
                        amount REAL,
                        mode TEXT CHECK (mode IN ('CASH', 'ONLINE')),
                        date TEXT,
                        from_account INTEGER,
                        to_account INTEGER,
                        loan_id INTEGER,
                        via TEXT,
                        notes TEXT,
                        FOREIGN KEY (from_account) REFERENCES Account(id),
                        FOREIGN KEY (to_account) REFERENCES Account(id),
                        FOREIGN KEY (loan_id) REFERENCES Loan(id)
                    )''')


def validate_mobile(Mobile):
    return re.fullmatch(r"\d{10}", Mobile) is not None

def validate_aadhaar(Aadhaar):
    return re.fullmatch(r"\d{12}", Aadhaar) is not None

def validate_pan(Pan):
    return re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", Pan) is not None

def validate_email(Email):
    return re.fullmatch(r"[^@]+@[^@]+\.[^@]+", Email) is not None

def insert_Account():
    conn = create_connection()
    cursor = conn.cursor()

    Holder_Name = input("Enter Account Holder Name: ")
    Bank_Name = input("Enter Bank Name: ")
    Number = input("Enter Account Number: ")
    Branch = input("Enter Branch: ")

    # Valid account types
    valid_Account_Types = {"SAVINGS", "CURRENT", "NRO"}

    # Validate IFSC code
    while True:
        IFSC = input("Enter IFSC Code: ").upper()
        if re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', IFSC):
            break
        else:
            print("Invalid IFSC Code. Please enter a valid 11-character IFSC code.")

    # Validate account type
    while True:
        Account_Type = input("Enter Account Type (SAVINGS, CURRENT, NRO): ").upper()
        if Account_Type in valid_Account_Types:
            break
        else:
            print("Invalid account type. Please enter either 'SAVINGS', 'CURRENT', or 'NRO'.")

    cursor.execute('''
    INSERT INTO Account (Holder_Name, Bank_Name, IFSC, Number, Branch, Account_Type)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (Holder_Name, Bank_Name, IFSC, Number, Branch, Account_Type))
    
    conn.commit()
    conn.close()

def view_Account():
    conn = create_connection()
    cursor = conn.cursor()

    while True:
        print("\n--- Account Viewing Options ---")
        print("1. View specific account by ID")
        print("2. View all accounts")
        print("3. Search accounts by holder name")
        print("4. Exit")
        
        option = input("Choose an option (1-4): ").strip()

        if option == '1':
            Account_Id = input("Enter Account ID: ").strip()
            cursor.execute('''
            SELECT 
                Id, Holder_Name, Bank_Name, IFSC, Number, Branch, Account_Type 
            FROM 
                Account 
            WHERE 
                Id = ?
            ''', (Account_Id,))
            
            account = cursor.fetchone()

            if account:
                print("\nAccount Details:")
                print(f"Account ID: {account[0]}")
                print(f"Holder Name: {account[1]}")
                print(f"Bank Name: {account[2]}")
                print(f"IFSC Code: {account[3]}")
                print(f"Account Number: {account[4]}")
                print(f"Branch: {account[5]}")
                print(f"Account Type: {account[6]}")
            else:
                print("No account found with the given ID.")
        
        elif option == '2':
            cursor.execute('''
            SELECT 
                Id, Holder_Name, Bank_Name, IFSC, Number, Branch, Account_Type 
            FROM 
                Account
            ''')
            
            accounts = cursor.fetchall()

            if accounts:
                print("\nAll Account Details:\n")
                for account in accounts:
                    print(f"Account ID: {account[0]}")
                    print(f"Holder Name: {account[1]}")
                    print(f"Bank Name: {account[2]}")
                    print(f"IFSC Code: {account[3]}")
                    print(f"Account Number: {account[4]}")
                    print(f"Branch: {account[5]}")
                    print(f"Account Type: {account[6]}")
                    print("-" * 40)  # Separator between accounts
            else:
                print("No accounts found.")
        
        elif option == '3':
            Holder_Name = input("Enter Account Holder Name to search: ").strip()
            cursor.execute('''
            SELECT 
                Id, Holder_Name, Bank_Name, IFSC, Number, Branch, Account_Type 
            FROM 
                Account 
            WHERE 
                holder_name LIKE ?
            ''', ('%' + Holder_Name + '%',))
            
            accounts = cursor.fetchall()

            if accounts:
                print(f"\nAccounts matching '{Holder_Name}':\n")
                for account in accounts:
                    print(f"Account ID: {account[0]}")
                    print(f"Holder Name: {account[1]}")
                    print(f"Bank Name: {account[2]}")
                    print(f"IFSC Code: {account[3]}")
                    print(f"Account Number: {account[4]}")
                    print(f"Branch: {account[5]}")
                    print(f"Account Type: {account[6]}")
                    print("-" * 40)  # Separator between accounts
            else:
                print(f"No accounts found for holder name '{Holder_Name}'.")
        
        elif option == '4':
            print("Exiting the account view.")
            break
        else:
            print("Invalid option! Please choose a valid option.")

    conn.close()

def update_Account():
    conn = create_connection()
    cursor = conn.cursor()

    # Input account ID to update
    Account_Id = int(input("Enter Account ID to update: "))

    # Fetch the current account details
    cursor.execute('''
    SELECT 
        Holder_Name, 
        Bank_Name, 
        IFSC, 
        Number, 
        Branch, 
        Account_Type 
    FROM 
        Account 
    WHERE 
        Id = ?
    ''', (Account_Id,))

    account = cursor.fetchone()

    if not account:
        print(f"No account found with ID {Account_Id}.")
        conn.close()
        return

    # Unpack current details
    Holder_Name, Bank_Name, IFSC, Number, Branch, Account_Type = account

    print("\nCurrent Account Details:")
    print(f"Holder Name: {Holder_Name}")
    print(f"Bank Name: {Bank_Name}")
    print(f"IFSC: {IFSC}")
    print(f"Account Number: {Number}")
    print(f"Branch: {Branch}")
    print(f"Account Type: {Account_Type}")

    # Input new values (leave blank to keep current)
    new_Holder_Name = input(f"Enter new Holder Name (leave blank to keep '{Holder_Name}'): ") or Holder_Name
    new_Bank_Name = input(f"Enter new Bank Name (leave blank to keep '{Bank_Name}'): ") or Bank_Name
    new_IFSC = input(f"Enter new IFSC (leave blank to keep '{IFSC}'): ") or IFSC
    new_Number = input(f"Enter new Account Number (leave blank to keep '{Number}'): ") or Number
    new_Branch = input(f"Enter new Branch (leave blank to keep '{Branch}'): ") or Branch
    new_Account_Type = input(f"Enter new Account Type (leave blank to keep '{Account_Type}'): ") or Account_Type

    # Validate IFSC Code
    while not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', new_IFSC):
        print("Invalid IFSC Code! It must be 11 characters long, with the first 4 being uppercase letters, the 5th being '0', and the last 6 being alphanumeric.")
        new_IFSC = input(f"Enter new IFSC (leave blank to keep '{IFSC}'): ") or IFSC

    # Validate Account Type
    valid_Account_Types = {"SAVINGS", "CURRENT", "NRO"}
    while new_Account_Type.upper() not in valid_Account_Types:
        print("Invalid account type! Must be one of 'SAVINGS', 'CURRENT', 'NRO'.")
        new_Account_Type = input(f"Enter new Account Type (leave blank to keep '{Account_Type}'): ") or Account_Type

    # Update account details in the database
    cursor.execute('''
    UPDATE Account
    SET 
        Holder_Name = ?, 
        Bank_Name = ?, 
        IFSC = ?, 
        Number = ?, 
        Branch = ?, 
        Account_Type = ?
    WHERE 
        id = ?
    ''', (new_Holder_Name, new_Bank_Name, new_IFSC, new_Number, new_Branch, new_Account_Type, Account_Id))

    # Commit the transaction
    conn.commit()

    print(f"\nAccount ID {Account_Id} successfully updated.")

    conn.close()

def is_account_linked(cursor, account_id):
    """
    Checks if the account ID is linked to any borrower, investor, or partner in the database.
    Returns True if linked, False otherwise.
    """
    # Check if the account ID is linked in the Borrower table
    cursor.execute("SELECT id FROM Borrower WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check if the account ID is linked in the Investor table
    cursor.execute("SELECT id FROM Investor WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check if the account ID is linked in the Partner table
    cursor.execute("SELECT id FROM Partner WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    return False

def insert_borrower():
    conn = create_connection()  # Assuming a function that creates a DB connection
    cursor = conn.cursor()

    # Input borrower details
    print("Enter Borrower Details:")

    name = input("Name: ").strip()

    mobile = input("Mobile: ").strip()
    while not validate_mobile(mobile):
        print("Invalid mobile number! Must be a 10-digit number.")
        mobile = input("Mobile: ").strip()

    email = input("Email: ").strip()
    while not validate_email(email):
        print("Invalid email address!")
        email = input("Email: ").strip()

    address = input("Address: ").strip()

    pan = input("PAN: ").strip()
    while not validate_pan(pan):
        print("Invalid PAN number! Must be a 10-character alphanumeric string in the format ABCDE1234F.")
        pan = input("PAN: ").strip()

    aadhaar = input("Aadhaar: ").strip()
    while not validate_aadhaar(aadhaar):
        print("Invalid Aadhaar number! Must be a 12-digit number.")
        aadhaar = input("Aadhaar: ").strip()

    # Input and validate multiple account IDs as a comma-separated list
    account_ids_input = input("Enter account IDs to link (comma-separated, or leave blank if no accounts): ").strip()
    valid_account_ids = []

    if account_ids_input:  # If the user provided account IDs
        account_ids = account_ids_input.split(',')
        for account_id in account_ids:
            account_id = account_id.strip()
            if is_account_linked(cursor, account_id):
                print(f"Account ID {account_id} is already linked to another entity. Skipping...")
            else:
                cursor.execute("SELECT id FROM Account WHERE id = ?", (account_id,))
                if cursor.fetchone():
                    valid_account_ids.append(account_id)
                else:
                    print(f"Account ID {account_id} is invalid. Skipping...")

    # Set the account ID string: either None (if no valid account IDs) or a comma-separated string of valid account IDs
    account_ids_str = ','.join(valid_account_ids) if valid_account_ids else None

    # Insert borrower details into the Borrower table
    cursor.execute('''
    INSERT INTO Borrower (name, mobile, email, address, pan, aadhaar, account_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, mobile, email, address, pan, aadhaar, account_ids_str))

    # Fetch the last inserted Borrower ID for display
    borrower_id = cursor.lastrowid

    # Confirmation message with horizontal table format
    borrower_details = [[
        borrower_id, name, mobile, email, address, pan, aadhaar, account_ids_str if account_ids_str else "None"
    ]]
    
    headers = [
        "Borrower ID", "Name", "Mobile", "Email", "Address", "PAN", "Aadhaar", "Associated Account IDs"
    ]

    print("\nBorrower successfully inserted:")
    print(tabulate(borrower_details, headers=headers, tablefmt="grid"))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

def view_borrower():
    conn = create_connection()  # Assuming a function that creates a DB connection
    cursor = conn.cursor()

    print("Choose an option:")
    print("1. View a single borrower by ID")
    print("2. View all borrowers")
    choice = input("Enter the number corresponding to your choice: ").strip()

    if choice == '1':
        # View a single borrower
        borrower_id_input = input("Enter Borrower ID to view details: ").strip()

        if not borrower_id_input.isdigit():
            print("Invalid input. Borrower ID must be an integer.")
            conn.close()
            return

        borrower_id = int(borrower_id_input)

        # Fetch borrower details from the Borrower table
        cursor.execute('''
        SELECT 
            id, name, mobile, email, address, pan, aadhaar, account_id
        FROM 
            Borrower
        WHERE 
            id = ?
        ''', (borrower_id,))

        borrower = cursor.fetchone()

        if not borrower:
            print(f"No borrower found with the ID {borrower_id}.")
            conn.close()
            return

        # Display borrower details in a horizontal table format
        borrower_details = [[
            borrower[0], borrower[1], borrower[2], borrower[3], borrower[4], borrower[5], borrower[6],
            borrower[7] if borrower[7] else "None"
        ]]
        headers = [
            "Borrower ID", "Name", "Mobile", "Email", "Address", "PAN", "Aadhaar", "Associated Account IDs"
        ]

        print("\nBorrower Details:")
        print(tabulate(borrower_details, headers=headers, tablefmt="grid"))

    elif choice == '2':
        # View all borrowers
        cursor.execute('''
        SELECT 
            id, name, mobile, email, address, pan, aadhaar, account_id
        FROM 
            Borrower
        ''')

        borrowers = cursor.fetchall()

        if not borrowers:
            print("No borrowers found.")
            conn.close()
            return

        # Display all borrower details in a horizontal table format
        borrower_details = []
        for borrower in borrowers:
            borrower_details.append([
                borrower[0], borrower[1], borrower[2], borrower[3], borrower[4], borrower[5], borrower[6],
                borrower[7] if borrower[7] else "None"
            ])

        headers = [
            "Borrower ID", "Name", "Mobile", "Email", "Address", "PAN", "Aadhaar", "Associated Account IDs"
        ]

        print("\nAll Borrowers:")
        print(tabulate(borrower_details, headers=headers, tablefmt="grid"))

    else:
        print("Invalid choice. Please enter 1 or 2.")

    conn.close()

def is_account_linked(cursor, account_id, exclude_borrower_id=None):
    """
    Check if the account ID is linked with any other entity, excluding the current borrower.
    """
    # Check in the Investor table
    cursor.execute("SELECT id FROM Investor WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check in the Partner table
    cursor.execute("SELECT id FROM Partner WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check in the Borrower table, excluding the current borrower if provided
    cursor.execute("SELECT id FROM Borrower WHERE account_id LIKE ? AND id != ?", ('%' + str(account_id) + '%', exclude_borrower_id))
    if cursor.fetchone():
        return True

    return False

def update_borrower():
    conn = create_connection()
    cursor = conn.cursor()

    borrower_id_input = input("Enter Borrower ID to update details: ").strip()
    if not borrower_id_input.isdigit():
        print("Invalid input. Borrower ID must be an integer.")
        conn.close()
        return

    borrower_id = int(borrower_id_input)

    # Fetch current borrower details
    cursor.execute('''
    SELECT 
        id, name, mobile, email, address, pan, aadhaar, account_id
    FROM 
        Borrower
    WHERE 
        id = ?
    ''', (borrower_id,))

    borrower = cursor.fetchone()

    if not borrower:
        print(f"No borrower found with the ID {borrower_id}.")
        conn.close()
        return

    # Display current borrower details in a horizontal table format
    borrower_details = [[
        borrower[0], borrower[1], borrower[2], borrower[3], borrower[4], borrower[5], borrower[6],
        borrower[7] if borrower[7] else "None"
    ]]
    headers = [
        "Borrower ID", "Name", "Mobile", "Email", "Address", "PAN", "Aadhaar", "Associated Account IDs"
    ]

    print("\nCurrent Borrower Details:")
    print(tabulate(borrower_details, headers=headers, tablefmt="grid"))

    # Display the available fields to update by number
    print("\nWhich fields would you like to update? Enter the numbers (comma-separated):")
    print("1. Name")
    print("2. Mobile")
    print("3. Email")
    print("4. Address")
    print("5. PAN")
    print("6. Aadhaar")
    print("7. Associated Account IDs")
    
    # Ask user for input on which fields they want to update
    fields_to_update = input("\nEnter the numbers of the fields you want to update (e.g., 1,3,5): ").strip().split(',')
    fields_to_update = [field.strip() for field in fields_to_update]

    updates = {}

    # Loop through the selected fields and ask for new values
    for field in fields_to_update:
        if field == '1':  # Update Name
            new_name = input(f"Enter new Name (leave blank to keep '{borrower[1]}'): ").strip()
            if new_name:
                updates['name'] = new_name

        elif field == '2':  # Update Mobile
            new_mobile = input(f"Enter new Mobile (leave blank to keep '{borrower[2]}'): ").strip()
            if new_mobile and validate_mobile(new_mobile):
                updates['mobile'] = new_mobile
            elif new_mobile:
                print("Invalid mobile number! Keeping the existing mobile.")

        elif field == '3':  # Update Email
            new_email = input(f"Enter new Email (leave blank to keep '{borrower[3]}'): ").strip()
            if new_email and validate_email(new_email):
                updates['email'] = new_email
            elif new_email:
                print("Invalid email address! Keeping the existing email.")

        elif field == '4':  # Update Address
            new_address = input(f"Enter new Address (leave blank to keep '{borrower[4]}'): ").strip()
            if new_address:
                updates['address'] = new_address

        elif field == '5':  # Update PAN
            new_pan = input(f"Enter new PAN (leave blank to keep '{borrower[5]}'): ").strip()
            if new_pan and validate_pan(new_pan):
                updates['pan'] = new_pan
            elif new_pan:
                print("Invalid PAN number! Keeping the existing PAN.")

        elif field == '6':  # Update Aadhaar
            new_aadhaar = input(f"Enter new Aadhaar (leave blank to keep '{borrower[6]}'): ").strip()
            if new_aadhaar and validate_aadhaar(new_aadhaar):
                updates['aadhaar'] = new_aadhaar
            elif new_aadhaar:
                print("Invalid Aadhaar number! Keeping the existing Aadhaar.")

        elif field == '7':  # Update Associated Account IDs
            print("\nAccount ID Update Options:")
            print("1. Remove all linked accounts and add new ones")
            print("2. Modify the existing linked accounts (add or remove specific accounts)")
            print("3. Clear all linked accounts (set to null)")
            account_update_choice = input("Choose an option (1, 2, or 3): ").strip()

            if account_update_choice == '1':  # Remove all linked accounts and add new ones
                new_account_ids = input("Enter new account IDs (comma-separated, or type 'null' to clear all): ").strip()
                if new_account_ids.lower() == 'null':
                    updates['account_id'] = None
                else:
                    new_account_ids = new_account_ids.split(',')
                    valid_account_ids = []

                    for account_id in new_account_ids:
                        account_id = account_id.strip()
                        cursor.execute("SELECT id FROM Account WHERE id = ?", (account_id,))
                        account = cursor.fetchone()
                        if account is None:
                            print(f"No account found with ID {account_id}. Skipping...")
                        elif is_account_linked(cursor, account_id, exclude_borrower_id=borrower_id):
                            print(f"Account ID {account_id} is already linked to another entity. Skipping...")
                        else:
                            valid_account_ids.append(account_id)

                    if not valid_account_ids:
                        print("No valid account IDs were provided. Skipping account ID update.")
                    else:
                        updates['account_id'] = ','.join(valid_account_ids)

            elif account_update_choice == '2':  # Modify existing linked accounts
                current_account_ids = borrower[7]
                if isinstance(current_account_ids, int):  # Single account ID
                    current_account_ids = [str(current_account_ids)]
                elif current_account_ids:  # Comma-separated string
                    current_account_ids = current_account_ids.split(',')
                else:
                    current_account_ids = []

                print(f"Current linked account IDs: {current_account_ids}")
                add_remove_choice = input("Would you like to (a)dd or (r)emove account IDs? (a/r): ").strip().lower()

                if add_remove_choice == 'a':
                    additional_account_ids = input("Enter additional account IDs to add (comma-separated): ").split(',')
                    for account_id in additional_account_ids:
                        account_id = account_id.strip()
                        if account_id not in current_account_ids:
                            cursor.execute("SELECT id FROM Account WHERE id = ?", (account_id,))
                            account = cursor.fetchone()
                            if account is None:
                                print(f"No account found with ID {account_id}. Skipping...")
                            elif is_account_linked(cursor, account_id, exclude_borrower_id=borrower_id):
                                print(f"Account ID {account_id} is already linked to another entity. Skipping...")
                            else:
                                current_account_ids.append(account_id)
                        else:
                            print(f"Account ID {account_id} is already linked to this borrower. Skipping...")

                elif add_remove_choice == 'r':
                    remove_account_ids = input("Enter account IDs to remove (comma-separated): ").split(',')
                    for account_id in remove_account_ids:
                        account_id = account_id.strip()
                        if account_id in current_account_ids:
                            current_account_ids.remove(account_id)
                        else:
                            print(f"Account ID {account_id} is not linked. Skipping...")

                if current_account_ids:
                    updates['account_id'] = ','.join(current_account_ids)
                else:
                    updates['account_id'] = None  # If no accounts left, set to null

            elif account_update_choice == '3':  # Clear all linked accounts (set to null)
                updates['account_id'] = None

        else:
            print(f"Invalid field number: {field}. Skipping...")

    # Apply updates if any changes were made
    if updates:
        set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values())
        values.append(borrower_id)

        cursor.execute(f'''
        UPDATE Borrower
        SET {set_clause}
        WHERE id = ?
        ''', values)

        conn.commit()

        # Fetch updated borrower details
        cursor.execute('''
        SELECT 
            id, name, mobile, email, address, pan, aadhaar, account_id
        FROM 
            Borrower
        WHERE 
            id = ?
        ''', (borrower_id,))

        updated_borrower = cursor.fetchone()

        # Display updated borrower details in horizontal table format
        updated_borrower_details = [[
            updated_borrower[0], updated_borrower[1], updated_borrower[2], updated_borrower[3], 
            updated_borrower[4], updated_borrower[5], updated_borrower[6],
            updated_borrower[7] if updated_borrower[7] else "None"
        ]]

        print("\nBorrower successfully updated:")
        print(tabulate(updated_borrower_details, headers=headers, tablefmt="grid"))

    else:
        print("No updates were made.")

    conn.close()

def is_account_linked(cursor, account_id):
    """
    Check if the account ID is linked with any other entity.
    """
    # Check in the Borrower table
    cursor.execute("SELECT id FROM Borrower WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check in the Investor table
    cursor.execute("SELECT id FROM Investor WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check in the Partner table
    cursor.execute("SELECT id FROM Partner WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check in the Facilitator table
    cursor.execute("SELECT id FROM Facilitator WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    return False

def insert_Facilitator():
    conn = create_connection()
    cursor = conn.cursor()

    # Input facilitator details
    print("Enter Facilitator Details:")
    name = input("Name: ").strip()

    mobile = input("Mobile: ").strip()
    while not validate_mobile(mobile):
        print("Invalid mobile number! Must be a 10-digit number.")
        mobile = input("Mobile: ").strip()

    email = input("Email: ").strip()
    while not validate_email(email):
        print("Invalid email address!")
        email = input("Email: ").strip()

    address = input("Address: ").strip()

    pan = input("PAN: ").strip()
    while not validate_pan(pan):
        print("Invalid PAN number! Must be a 10-character alphanumeric string in the format ABCDE1234F.")
        pan = input("PAN: ").strip()

    aadhaar = input("Aadhaar: ").strip()
    while not validate_aadhaar(aadhaar):
        print("Invalid Aadhaar number! Must be a 12-digit number.")
        aadhaar = input("Aadhaar: ").strip()

    # Input and validate multiple account IDs as an optional comma-separated list
    account_ids_input = input("Enter account IDs to link (comma-separated, or leave blank to skip): ").strip()
    valid_account_ids = []

    if account_ids_input:
        account_ids = account_ids_input.split(',')

        for account_id in account_ids:
            account_id = account_id.strip()
            cursor.execute("SELECT id FROM Account WHERE id = ?", (account_id,))
            account = cursor.fetchone()
            if account is None:
                print(f"No account found with ID {account_id}. Skipping...")
            elif is_account_linked(cursor, account_id):
                print(f"Account ID {account_id} is already linked to another entity. Skipping...")
            else:
                valid_account_ids.append(account_id)

        if not valid_account_ids:
            print("No valid account IDs were provided. Facilitator will not be linked to any accounts.")

    # Use a default value if no account IDs are provided
    account_ids_str = ','.join(valid_account_ids) if valid_account_ids else "None"

    # Insert the facilitator details into the Facilitator table
    cursor.execute('''
    INSERT INTO Facilitator (name, mobile, email, address, pan, aadhaar, account_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, mobile, email, address, pan, aadhaar, account_ids_str))

    print(f"Facilitator successfully inserted with linked Account IDs {account_ids_str if account_ids_str != 'None' else 'None'}.")

    # Fetch and display the inserted facilitator details in a horizontal format
    cursor.execute('''
    SELECT 
        id, name, mobile, email, address, pan, aadhaar, account_id
    FROM 
        Facilitator
    WHERE 
        mobile = ? AND email = ?
    ''', (mobile, email))

    facilitator = cursor.fetchone()

    # Display the inserted facilitator details in a horizontal table format
    headers = ["ID", "Name", "Mobile", "Email", "Address", "PAN", "Aadhaar", "Account IDs"]
    facilitator_details = [[
        facilitator[0],
        facilitator[1],
        facilitator[2],
        facilitator[3],
        facilitator[4],
        facilitator[5],
        facilitator[6],
        facilitator[7] if facilitator[7] else "None"
    ]]

    print("\nFacilitator Details:")
    print(tabulate(facilitator_details, headers=headers, tablefmt="grid"))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

def view_Facilitator():
    conn = create_connection()
    cursor = conn.cursor()

    print("Choose an option:")
    print("1. View a single facilitator by ID")
    print("2. View all facilitators")
    choice = input("Enter the number corresponding to your choice: ").strip()

    if choice == '1':
        # View a single facilitator
        facilitator_id_input = input("Enter Facilitator ID to view details: ").strip()

        if not facilitator_id_input.isdigit():
            print("Invalid input. Facilitator ID must be an integer.")
            conn.close()
            return

        facilitator_id = int(facilitator_id_input)

        # Fetch facilitator details from the Facilitator table
        cursor.execute('''
        SELECT 
            id, name, mobile, email, address, pan, aadhaar, account_id
        FROM 
            Facilitator
        WHERE 
            id = ?
        ''', (facilitator_id,))

        facilitator = cursor.fetchone()

        if not facilitator:
            print(f"No facilitator found with the ID {facilitator_id}.")
            conn.close()
            return

        # Handle account IDs: display as a comma-separated string or "None" if blank
        account_ids = facilitator[7].split(',') if facilitator[7] else ["None"]

        # Display facilitator details in a horizontal table format
        facilitator_details = [[
            facilitator[0], facilitator[1], facilitator[2], facilitator[3], 
            facilitator[4], facilitator[5], facilitator[6],
            ', '.join(account_ids) if account_ids else "None"
        ]]
        headers = [
            "Facilitator ID", "Name", "Mobile", "Email", "Address", "PAN", "Aadhaar", "Associated Account IDs"
        ]

        print("\nFacilitator Details:")
        print(tabulate(facilitator_details, headers=headers, tablefmt="grid"))

    elif choice == '2':
        # View all facilitators
        cursor.execute('''
        SELECT 
            id, name, mobile, email, address, pan, aadhaar, account_id
        FROM 
            Facilitator
        ''')

        facilitators = cursor.fetchall()

        if not facilitators:
            print("No facilitators found.")
            conn.close()
            return

        # Display all facilitator details in a horizontal table format
        facilitator_details = []
        for facilitator in facilitators:
            # Handle account IDs: display as a comma-separated string or "None" if blank
            account_ids = facilitator[7].split(',') if facilitator[7] else ["None"]
            facilitator_details.append([
                facilitator[0], facilitator[1], facilitator[2], facilitator[3], 
                facilitator[4], facilitator[5], facilitator[6],
                ', '.join(account_ids) if account_ids else "None"
            ])

        headers = [
            "Facilitator ID", "Name", "Mobile", "Email", "Address", "PAN", "Aadhaar", "Associated Account IDs"
        ]

        print("\nAll Facilitators:")
        print(tabulate(facilitator_details, headers=headers, tablefmt="grid"))

    else:
        print("Invalid choice. Please enter 1 or 2.")

    conn.close()

def is_account_linked(cursor, account_id, exclude_facilitator_id=None):
    """
    Check if the account ID is linked with any other entity, excluding the current facilitator.
    """
    # Check in the Borrower table
    cursor.execute("SELECT id FROM Borrower WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check in the Investor table
    cursor.execute("SELECT id FROM Investor WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check in the Partner table
    cursor.execute("SELECT id FROM Partner WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check in the Facilitator table, excluding the current facilitator if provided
    cursor.execute("SELECT id FROM Facilitator WHERE account_id LIKE ? AND id != ?", ('%' + str(account_id) + '%', exclude_facilitator_id))
    if cursor.fetchone():
        return True

    return False

def update_Facilitator():
    conn = create_connection()
    cursor = conn.cursor()

    facilitator_id_input = input("Enter Facilitator ID to update details: ").strip()
    if not facilitator_id_input.isdigit():
        print("Invalid input. Facilitator ID must be an integer.")
        conn.close()
        return

    facilitator_id = int(facilitator_id_input)

    # Fetch current facilitator details
    cursor.execute('''
    SELECT 
        id, name, mobile, email, address, pan, aadhaar, account_id
    FROM 
        Facilitator
    WHERE 
        id = ?
    ''', (facilitator_id,))

    facilitator = cursor.fetchone()

    if not facilitator:
        print(f"No facilitator found with the ID {facilitator_id}.")
        conn.close()
        return

    # Display current facilitator details in a horizontal table format
    facilitator_details = [[
        facilitator[0], facilitator[1], facilitator[2], facilitator[3], facilitator[4], facilitator[5], facilitator[6],
        facilitator[7] if facilitator[7] else "None"
    ]]
    headers = [
        "Facilitator ID", "Name", "Mobile", "Email", "Address", "PAN", "Aadhaar", "Associated Account IDs"
    ]

    print("\nCurrent Facilitator Details:")
    print(tabulate(facilitator_details, headers=headers, tablefmt="grid"))

    # Display the available fields to update by number
    print("\nWhich fields would you like to update? Enter the numbers (comma-separated):")
    print("1. Name")
    print("2. Mobile")
    print("3. Email")
    print("4. Address")
    print("5. PAN")
    print("6. Aadhaar")
    print("7. Associated Account IDs")
    
    # Ask user for input on which fields they want to update
    fields_to_update = input("\nEnter the numbers of the fields you want to update (e.g., 1,3,5): ").strip().split(',')
    fields_to_update = [field.strip() for field in fields_to_update]

    updates = {}

    # Loop through the selected fields and ask for new values
    for field in fields_to_update:
        if field == '1':  # Update Name
            new_name = input(f"Enter new Name (leave blank to keep '{facilitator[1]}'): ").strip()
            if new_name:
                updates['name'] = new_name

        elif field == '2':  # Update Mobile
            new_mobile = input(f"Enter new Mobile (leave blank to keep '{facilitator[2]}'): ").strip()
            if new_mobile and validate_mobile(new_mobile):
                updates['mobile'] = new_mobile
            elif new_mobile:
                print("Invalid mobile number! Keeping the existing mobile.")

        elif field == '3':  # Update Email
            new_email = input(f"Enter new Email (leave blank to keep '{facilitator[3]}'): ").strip()
            if new_email and validate_email(new_email):
                updates['email'] = new_email
            elif new_email:
                print("Invalid email address! Keeping the existing email.")

        elif field == '4':  # Update Address
            new_address = input(f"Enter new Address (leave blank to keep '{facilitator[4]}'): ").strip()
            if new_address:
                updates['address'] = new_address

        elif field == '5':  # Update PAN
            new_pan = input(f"Enter new PAN (leave blank to keep '{facilitator[5]}'): ").strip()
            if new_pan and validate_pan(new_pan):
                updates['pan'] = new_pan
            elif new_pan:
                print("Invalid PAN number! Keeping the existing PAN.")

        elif field == '6':  # Update Aadhaar
            new_aadhaar = input(f"Enter new Aadhaar (leave blank to keep '{facilitator[6]}'): ").strip()
            if new_aadhaar and validate_aadhaar(new_aadhaar):
                updates['aadhaar'] = new_aadhaar
            elif new_aadhaar:
                print("Invalid Aadhaar number! Keeping the existing Aadhaar.")

        elif field == '7':  # Update Associated Account IDs
            print("\nAccount ID Update Options:")
            print("1. Remove all linked accounts and add new ones")
            print("2. Modify the existing linked accounts (add or remove specific accounts)")
            print("3. Clear all linked accounts (set to null)")
            account_update_choice = input("Choose an option (1, 2, or 3): ").strip()

            if account_update_choice == '1':  # Remove all linked accounts and add new ones
                new_account_ids = input("Enter new account IDs (comma-separated, or type 'null' to clear all): ").strip()
                if new_account_ids.lower() == 'null':
                    updates['account_id'] = None
                else:
                    new_account_ids = new_account_ids.split(',')
                    valid_account_ids = []

                    for account_id in new_account_ids:
                        account_id = account_id.strip()
                        cursor.execute("SELECT id FROM Account WHERE id = ?", (account_id,))
                        account = cursor.fetchone()
                        if account is None:
                            print(f"No account found with ID {account_id}. Skipping...")
                        elif is_account_linked(cursor, account_id, exclude_facilitator_id=facilitator_id):
                            print(f"Account ID {account_id} is already linked to another entity. Skipping...")
                        else:
                            valid_account_ids.append(account_id)

                    if not valid_account_ids:
                        print("No valid account IDs were provided. Skipping account ID update.")
                    else:
                        updates['account_id'] = ','.join(valid_account_ids)

            elif account_update_choice == '2':  # Modify existing linked accounts
                current_account_ids = facilitator[7]
                if isinstance(current_account_ids, int):  # Single account ID
                    current_account_ids = [str(current_account_ids)]
                elif current_account_ids:  # Comma-separated string
                    current_account_ids = current_account_ids.split(',')
                else:
                    current_account_ids = []

                print(f"Current linked account IDs: {current_account_ids}")
                add_remove_choice = input("Would you like to (a)dd or (r)emove account IDs? (a/r): ").strip().lower()

                if add_remove_choice == 'a':
                    additional_account_ids = input("Enter additional account IDs to add (comma-separated): ").split(',')
                    for account_id in additional_account_ids:
                        account_id = account_id.strip()
                        if account_id not in current_account_ids:
                            cursor.execute("SELECT id FROM Account WHERE id = ?", (account_id,))
                            account = cursor.fetchone()
                            if account is None:
                                print(f"No account found with ID {account_id}. Skipping...")
                            elif is_account_linked(cursor, account_id, exclude_facilitator_id=facilitator_id):
                                print(f"Account ID {account_id} is already linked to another entity. Skipping...")
                            else:
                                current_account_ids.append(account_id)
                        else:
                            print(f"Account ID {account_id} is already linked to this facilitator. Skipping...")

                elif add_remove_choice == 'r':
                    remove_account_ids = input("Enter account IDs to remove (comma-separated): ").split(',')
                    for account_id in remove_account_ids:
                        account_id = account_id.strip()
                        if account_id in current_account_ids:
                            current_account_ids.remove(account_id)
                        else:
                            print(f"Account ID {account_id} is not linked. Skipping...")

                if current_account_ids:
                    updates['account_id'] = ','.join(current_account_ids)
                else:
                    updates['account_id'] = None  # If no accounts left, set to null

            elif account_update_choice == '3':  # Clear all linked accounts (set to null)
                updates['account_id'] = None

        else:
            print(f"Invalid field number: {field}. Skipping...")

    # Apply updates if any changes were made
    if updates:
        set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values())
        values.append(facilitator_id)

        cursor.execute(f'''
        UPDATE Facilitator
        SET {set_clause}
        WHERE id = ?
        ''', values)

        conn.commit()

        # Fetch updated facilitator details
        cursor.execute('''
        SELECT 
            id, name, mobile, email, address, pan, aadhaar, account_id
        FROM 
            Facilitator
        WHERE 
            id = ?
        ''', (facilitator_id,))

        updated_facilitator = cursor.fetchone()

        # Display updated facilitator details in horizontal table format
        updated_facilitator_details = [[
            updated_facilitator[0], updated_facilitator[1], updated_facilitator[2], updated_facilitator[3], 
            updated_facilitator[4], updated_facilitator[5], updated_facilitator[6],
            updated_facilitator[7] if updated_facilitator[7] else "None"
        ]]

        print("\nFacilitator successfully updated:")
        print(tabulate(updated_facilitator_details, headers=headers, tablefmt="grid"))

    else:
        print("No updates were made.")

    conn.close()

def is_account_linked(cursor, account_id):
    """
    Check if the account ID is linked with any other entity.
    """
    # Check in the Borrower table
    cursor.execute("SELECT id FROM Borrower WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check in the Partner table
    cursor.execute("SELECT id FROM Partner WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check in the Facilitator table
    cursor.execute("SELECT id FROM Facilitator WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check in the Investor table
    cursor.execute("SELECT id FROM Investor WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    return False

def insert_Investor():
    conn = create_connection()
    cursor = conn.cursor()

    # Input investor details
    print("Enter Investor Details:")
    name = input("Name: ").strip()

    mobile = input("Mobile: ").strip()
    while not validate_mobile(mobile):
        print("Invalid mobile number! Must be a 10-digit number.")
        mobile = input("Mobile: ").strip()

    email = input("Email: ").strip()
    while not validate_email(email):
        print("Invalid email address!")
        email = input("Email: ").strip()

    address = input("Address: ").strip()

    pan = input("PAN: ").strip()
    while not validate_pan(pan):
        print("Invalid PAN number! Must be a 10-character alphanumeric string in the format ABCDE1234F.")
        pan = input("PAN: ").strip()

    aadhaar = input("Aadhaar: ").strip()
    while not validate_aadhaar(aadhaar):
        print("Invalid Aadhaar number! Must be a 12-digit number.")
        aadhaar = input("Aadhaar: ").strip()

    # Input and validate multiple account IDs as an optional comma-separated list
    account_ids_input = input("Enter account IDs to link (comma-separated, or leave blank to skip): ").strip()
    valid_account_ids = []

    if account_ids_input:
        account_ids = account_ids_input.split(',')

        for account_id in account_ids:
            account_id = account_id.strip()
            cursor.execute("SELECT id FROM Account WHERE id = ?", (account_id,))
            account = cursor.fetchone()
            if account is None:
                print(f"No account found with ID {account_id}. Skipping...")
            elif is_account_linked(cursor, account_id):
                print(f"Account ID {account_id} is already linked to another entity. Skipping...")
            else:
                valid_account_ids.append(account_id)

        if not valid_account_ids:
            print("No valid account IDs were provided. Investor will not be linked to any accounts.")

    # Use a default value if no account IDs are provided
    account_ids_str = ','.join(valid_account_ids) if valid_account_ids else "None"

    # Insert the investor details into the Investor table
    cursor.execute('''
    INSERT INTO Investor (name, mobile, email, address, pan, aadhaar, account_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, mobile, email, address, pan, aadhaar, account_ids_str))

    print(f"Investor successfully inserted with linked Account IDs {account_ids_str if account_ids_str != 'None' else 'None'}.")

    # Fetch and display the inserted investor details in a horizontal format
    cursor.execute('''
    SELECT 
        id, name, mobile, email, address, pan, aadhaar, account_id
    FROM 
        Investor
    WHERE 
        mobile = ? AND email = ?
    ''', (mobile, email))

    investor = cursor.fetchone()

    # Display the inserted investor details in a horizontal table format
    headers = ["ID", "Name", "Mobile", "Email", "Address", "PAN", "Aadhaar", "Account IDs"]
    investor_details = [[
        investor[0],
        investor[1],
        investor[2],
        investor[3],
        investor[4],
        investor[5],
        investor[6],
        investor[7] if investor[7] else "None"
    ]]

    print("\nInvestor Details:")
    print(tabulate(investor_details, headers=headers, tablefmt="grid"))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()


def format_account_ids(account_ids):
    """
    Format account IDs into a readable string.
    Handles cases where account IDs might be stored as an integer, string, or None.
    """
    if isinstance(account_ids, int):
        return str(account_ids)  # Single account ID as integer
    elif isinstance(account_ids, str):
        return ', '.join(account_ids.split(','))  # Comma-separated string of account IDs
    elif account_ids is None or account_ids == "":
        return "None"  # No linked accounts
    else:
        return str(account_ids)

def view_Investor():
    conn = create_connection()
    cursor = conn.cursor()

    print("Choose an option:")
    print("1. View a single investor by ID")
    print("2. View all investors")
    choice = input("Enter the number corresponding to your choice: ").strip()

    if choice == '1':
        # View a single investor
        investor_id_input = input("Enter Investor ID to view details: ").strip()

        if not investor_id_input.isdigit():
            print("Invalid input. Investor ID must be an integer.")
            conn.close()
            return

        investor_id = int(investor_id_input)

        # Fetch investor details from the Investor table
        cursor.execute('''
        SELECT 
            id, name, mobile, email, address, pan, aadhaar, account_id
        FROM 
            Investor
        WHERE 
            id = ?
        ''', (investor_id,))

        investor = cursor.fetchone()

        if not investor:
            print(f"No investor found with the ID {investor_id}.")
            conn.close()
            return

        # Format account IDs for display
        formatted_account_ids = format_account_ids(investor[7])

        # Display investor details in a horizontal table format
        investor_details = [[
            investor[0], investor[1], investor[2], investor[3], 
            investor[4], investor[5], investor[6],
            formatted_account_ids
        ]]
        headers = [
            "Investor ID", "Name", "Mobile", "Email", "Address", "PAN", "Aadhaar", "Associated Account IDs"
        ]

        print("\nInvestor Details:")
        print(tabulate(investor_details, headers=headers, tablefmt="grid"))

    elif choice == '2':
        # View all investors
        cursor.execute('''
        SELECT 
            id, name, mobile, email, address, pan, aadhaar, account_id
        FROM 
            Investor
        ''')

        investors = cursor.fetchall()

        if not investors:
            print("No investors found.")
            conn.close()
            return

        # Display all investor details in a horizontal table format
        investor_details = []
        for investor in investors:
            # Format account IDs for display
            formatted_account_ids = format_account_ids(investor[7])
            investor_details.append([
                investor[0], investor[1], investor[2], investor[3], 
                investor[4], investor[5], investor[6],
                formatted_account_ids
            ])

        headers = [
            "Investor ID", "Name", "Mobile", "Email", "Address", "PAN", "Aadhaar", "Associated Account IDs"
        ]

        print("\nAll Investors:")
        print(tabulate(investor_details, headers=headers, tablefmt="grid"))

    else:
        print("Invalid choice. Please enter 1 or 2.")

    conn.close()

def is_account_linked(cursor, account_id, exclude_investor_id=None):
    """
    Check if the account ID is linked with any other entity, excluding the current investor (if provided).
    """
    # Check in the Borrower table
    cursor.execute("SELECT id FROM Borrower WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check in the Partner table
    cursor.execute("SELECT id FROM Partner WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check in the Facilitator table
    cursor.execute("SELECT id FROM Facilitator WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check in the Investor table, excluding the current investor if provided
    cursor.execute("SELECT id FROM Investor WHERE account_id LIKE ? AND id != ?", ('%' + str(account_id) + '%', exclude_investor_id))
    if cursor.fetchone():
        return True

    return False

def update_investor():
    conn = create_connection()
    cursor = conn.cursor()

    investor_id_input = input("Enter Investor ID to update details: ").strip()
    if not investor_id_input.isdigit():
        print("Invalid input. Investor ID must be an integer.")
        conn.close()
        return

    investor_id = int(investor_id_input)

    # Fetch current investor details
    cursor.execute('''
    SELECT 
        id, name, mobile, email, address, pan, aadhaar, account_id
    FROM 
        Investor
    WHERE 
        id = ?
    ''', (investor_id,))

    investor = cursor.fetchone()

    if not investor:
        print(f"No investor found with the ID {investor_id}.")
        conn.close()
        return

    # Display current investor details in a horizontal table format
    investor_details = [[
        investor[0], investor[1], investor[2], investor[3], 
        investor[4], investor[5], investor[6],
        investor[7] if investor[7] else "None"
    ]]
    headers = [
        "Investor ID", "Name", "Mobile", "Email", "Address", "PAN", "Aadhaar", "Associated Account IDs"
    ]

    print("\nCurrent Investor Details:")
    print(tabulate(investor_details, headers=headers, tablefmt="grid"))

    # Display the available fields to update by number
    print("\nWhich fields would you like to update? Enter the numbers (comma-separated):")
    print("1. Name")
    print("2. Mobile")
    print("3. Email")
    print("4. Address")
    print("5. PAN")
    print("6. Aadhaar")
    print("7. Associated Account IDs")
    
    # Ask user for input on which fields they want to update
    fields_to_update = input("\nEnter the numbers of the fields you want to update (e.g., 1,3,5): ").strip().split(',')
    fields_to_update = [field.strip() for field in fields_to_update]

    updates = {}

    # Loop through the selected fields and ask for new values
    for field in fields_to_update:
        if field == '1':  # Update Name
            new_name = input(f"Enter new Name (leave blank to keep '{investor[1]}'): ").strip()
            if new_name:
                updates['name'] = new_name

        elif field == '2':  # Update Mobile
            new_mobile = input(f"Enter new Mobile (leave blank to keep '{investor[2]}'): ").strip()
            if new_mobile and validate_mobile(new_mobile):
                updates['mobile'] = new_mobile
            elif new_mobile:
                print("Invalid mobile number! Keeping the existing mobile.")

        elif field == '3':  # Update Email
            new_email = input(f"Enter new Email (leave blank to keep '{investor[3]}'): ").strip()
            if new_email and validate_email(new_email):
                updates['email'] = new_email
            elif new_email:
                print("Invalid email address! Keeping the existing email.")

        elif field == '4':  # Update Address
            new_address = input(f"Enter new Address (leave blank to keep '{investor[4]}'): ").strip()
            if new_address:
                updates['address'] = new_address

        elif field == '5':  # Update PAN
            new_pan = input(f"Enter new PAN (leave blank to keep '{investor[5]}'): ").strip()
            if new_pan and validate_pan(new_pan):
                updates['pan'] = new_pan
            elif new_pan:
                print("Invalid PAN number! Keeping the existing PAN.")

        elif field == '6':  # Update Aadhaar
            new_aadhaar = input(f"Enter new Aadhaar (leave blank to keep '{investor[6]}'): ").strip()
            if new_aadhaar and validate_aadhaar(new_aadhaar):
                updates['aadhaar'] = new_aadhaar
            elif new_aadhaar:
                print("Invalid Aadhaar number! Keeping the existing Aadhaar.")

        elif field == '7':  # Update Associated Account IDs
            print("\nAccount ID Update Options:")
            print("1. Remove all linked accounts and add new ones")
            print("2. Modify the existing linked accounts (add or remove specific accounts)")
            print("3. Clear all linked accounts (set to null)")
            account_update_choice = input("Choose an option (1, 2, or 3): ").strip()

            if account_update_choice == '1':  # Remove all linked accounts and add new ones
                new_account_ids = input("Enter new account IDs (comma-separated, or type 'null' to clear all): ").strip()
                if new_account_ids.lower() == 'null':
                    updates['account_id'] = None
                else:
                    new_account_ids = new_account_ids.split(',')
                    valid_account_ids = []

                    for account_id in new_account_ids:
                        account_id = account_id.strip()
                        cursor.execute("SELECT id FROM Account WHERE id = ?", (account_id,))
                        account = cursor.fetchone()
                        if account is None:
                            print(f"No account found with ID {account_id}. Skipping...")
                        elif is_account_linked(cursor, account_id, exclude_investor_id=investor_id):
                            print(f"Account ID {account_id} is already linked to another entity. Skipping...")
                        else:
                            valid_account_ids.append(account_id)

                    if not valid_account_ids:
                        print("No valid account IDs were provided. Skipping account ID update.")
                    else:
                        updates['account_id'] = ','.join(valid_account_ids)

            elif account_update_choice == '2':  # Modify existing linked accounts
                current_account_ids = investor[7]
                if isinstance(current_account_ids, int):  # Single account ID
                    current_account_ids = [str(current_account_ids)]
                elif current_account_ids:  # Comma-separated string
                    current_account_ids = current_account_ids.split(',')
                else:
                    current_account_ids = []

                print(f"Current linked account IDs: {current_account_ids}")
                add_remove_choice = input("Would you like to (a)dd or (r)emove account IDs? (a/r): ").strip().lower()

                if add_remove_choice == 'a':
                    additional_account_ids = input("Enter additional account IDs to add (comma-separated): ").split(',')
                    for account_id in additional_account_ids:
                        account_id = account_id.strip()
                        if account_id not in current_account_ids:
                            cursor.execute("SELECT id FROM Account WHERE id = ?", (account_id,))
                            account = cursor.fetchone()
                            if account is None:
                                print(f"No account found with ID {account_id}. Skipping...")
                            elif is_account_linked(cursor, account_id, exclude_investor_id=investor_id):
                                print(f"Account ID {account_id} is already linked to another entity. Skipping...")
                            else:
                                current_account_ids.append(account_id)
                        else:
                            print(f"Account ID {account_id} is already linked to this investor. Skipping...")

                elif add_remove_choice == 'r':
                    remove_account_ids = input("Enter account IDs to remove (comma-separated): ").split(',')
                    for account_id in remove_account_ids:
                        account_id = account_id.strip()
                        if account_id in current_account_ids:
                            current_account_ids.remove(account_id)
                        else:
                            print(f"Account ID {account_id} is not linked. Skipping...")

                if current_account_ids:
                    updates['account_id'] = ','.join(current_account_ids)
                else:
                    updates['account_id'] = None  # If no accounts left, set to null

            elif account_update_choice == '3':  # Clear all linked accounts (set to null)
                updates['account_id'] = None

        else:
            print(f"Invalid field number: {field}. Skipping...")

    # Apply updates if any changes were made
    if updates:
        set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values())
        values.append(investor_id)

        cursor.execute(f'''
        UPDATE Investor
        SET {set_clause}
        WHERE id = ?
        ''', values)

        conn.commit()

        # Fetch updated investor details
        cursor.execute('''
        SELECT 
            id, name, mobile, email, address, pan, aadhaar, account_id
        FROM 
            Investor
        WHERE 
            id = ?
        ''', (investor_id,))

        updated_investor = cursor.fetchone()

        # Display updated investor details in horizontal table format
        updated_investor_details = [[
            updated_investor[0], updated_investor[1], updated_investor[2], updated_investor[3], 
            updated_investor[4], updated_investor[5], updated_investor[6],
            updated_investor[7] if updated_investor[7] else "None"
        ]]

        print("\nInvestor successfully updated:")
        print(tabulate(updated_investor_details, headers=headers, tablefmt="grid"))

    else:
        print("No updates were made.")

    conn.close()

def is_account_linked(cursor, account_id):
    """
    Check if the account ID is linked with any other entity (Borrower, Investor, Facilitator).
    """
    # Check in the Borrower table
    cursor.execute("SELECT id FROM Borrower WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check in the Investor table
    cursor.execute("SELECT id FROM Investor WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check in the Facilitator table
    cursor.execute("SELECT id FROM Facilitator WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check in the Partner table
    cursor.execute("SELECT id FROM Partner WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    return False

def insert_partner():
    conn = create_connection()
    cursor = conn.cursor()

    # Input partner details
    print("Enter Partner Details:")
    name = input("Name: ").strip()

    mobile = input("Mobile: ").strip()
    while not validate_mobile(mobile):
        print("Invalid mobile number! Must be a 10-digit number.")
        mobile = input("Mobile: ").strip()

    email = input("Email: ").strip()
    while not validate_email(email):
        print("Invalid email address!")
        email = input("Email: ").strip()

    address = input("Address: ").strip()

    pan = input("PAN: ").strip()
    while not validate_pan(pan):
        print("Invalid PAN number! Must be a 10-character alphanumeric string in the format ABCDE1234F.")
        pan = input("PAN: ").strip()

    aadhaar = input("Aadhaar: ").strip()
    while not validate_aadhaar(aadhaar):
        print("Invalid Aadhaar number! Must be a 12-digit number.")
        aadhaar = input("Aadhaar: ").strip()

    # Input and validate multiple account IDs as an optional comma-separated list
    account_ids_input = input("Enter account IDs to link (comma-separated, or leave blank to skip): ").strip()
    valid_account_ids = []

    if account_ids_input:
        account_ids = account_ids_input.split(',')

        for account_id in account_ids:
            account_id = account_id.strip()
            cursor.execute("SELECT id FROM Account WHERE id = ?", (account_id,))
            account = cursor.fetchone()
            if account is None:
                print(f"No account found with ID {account_id}. Skipping...")
            elif is_account_linked(cursor, account_id):
                print(f"Account ID {account_id} is already linked to another entity. Skipping...")
            else:
                valid_account_ids.append(account_id)

        if not valid_account_ids:
            print("No valid account IDs were provided. Partner will not be linked to any accounts.")

    # Use a default value if no account IDs are provided
    account_ids_str = ','.join(valid_account_ids) if valid_account_ids else "None"

    # Insert the partner details into the Partner table
    cursor.execute('''
    INSERT INTO Partner (name, mobile, email, address, pan, aadhaar, account_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, mobile, email, address, pan, aadhaar, account_ids_str))

    print(f"Partner successfully inserted with linked Account IDs {account_ids_str if account_ids_str != 'None' else 'None'}.")

    # Fetch and display the inserted partner details in a horizontal format
    cursor.execute('''
    SELECT 
        id, name, mobile, email, address, pan, aadhaar, account_id
    FROM 
        Partner
    WHERE 
        mobile = ? AND email = ?
    ''', (mobile, email))

    partner = cursor.fetchone()

    # Display the inserted partner details in a horizontal table format
    headers = ["ID", "Name", "Mobile", "Email", "Address", "PAN", "Aadhaar", "Account IDs"]
    partner_details = [[
        partner[0],
        partner[1],
        partner[2],
        partner[3],
        partner[4],
        partner[5],
        partner[6],
        partner[7] if partner[7] else "None"
    ]]

    print("\nPartner Details:")
    print(tabulate(partner_details, headers=headers, tablefmt="grid"))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

def view_Partner():
    conn = create_connection()  # Assuming a function that creates a DB connection
    cursor = conn.cursor()

    print("Choose an option:")
    print("1. View a single partner by ID")
    print("2. View all partners")
    choice = input("Enter the number corresponding to your choice: ").strip()

    if choice == '1':
        # View a single partner
        partner_id_input = input("Enter Partner ID to view details: ").strip()

        if not partner_id_input.isdigit():
            print("Invalid input. Partner ID must be an integer.")
            conn.close()
            return

        partner_id = int(partner_id_input)

        # Fetch partner details from the Partner table
        cursor.execute('''
        SELECT 
            id, name, mobile, email, address, pan, aadhaar, account_id
        FROM 
            Partner
        WHERE 
            id = ?
        ''', (partner_id,))

        partner = cursor.fetchone()

        if not partner:
            print(f"No partner found with the ID {partner_id}.")
            conn.close()
            return

        # Display partner details in a horizontal table format
        partner_details = [[
            partner[0], partner[1], partner[2], partner[3], partner[4], partner[5], partner[6],
            partner[7] if partner[7] else "None"
        ]]
        headers = [
            "Partner ID", "Name", "Mobile", "Email", "Address", "PAN", "Aadhaar", "Associated Account IDs"
        ]

        print("\nPartner Details:")
        print(tabulate(partner_details, headers=headers, tablefmt="grid"))

    elif choice == '2':
        # View all partners
        cursor.execute('''
        SELECT 
            id, name, mobile, email, address, pan, aadhaar, account_id
        FROM 
            Partner
        ''')

        partners = cursor.fetchall()

        if not partners:
            print("No partners found.")
            conn.close()
            return

        # Display all partner details in a horizontal table format
        partner_details = []
        for partner in partners:
            partner_details.append([
                partner[0], partner[1], partner[2], partner[3], partner[4], partner[5], partner[6],
                partner[7] if partner[7] else "None"
            ])

        headers = [
            "Partner ID", "Name", "Mobile", "Email", "Address", "PAN", "Aadhaar", "Associated Account IDs"
        ]

        print("\nAll Partners:")
        print(tabulate(partner_details, headers=headers, tablefmt="grid"))

    else:
        print("Invalid choice. Please enter 1 or 2.")

    conn.close()

def is_account_linked(cursor, account_id, exclude_partner_id=None):
    """
    Check if the account ID is linked with any other entity (Borrower, Investor, Partner).
    Optionally exclude the current partner being updated.
    """
    # Check if account is linked to another borrower
    cursor.execute("SELECT id FROM Borrower WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check if account is linked to another investor
    cursor.execute("SELECT id FROM Investor WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check if account is linked to another partner, excluding the current partner being updated
    cursor.execute("SELECT id FROM Partner WHERE account_id LIKE ? AND id != ?", ('%' + str(account_id) + '%', exclude_partner_id))
    if cursor.fetchone():
        return True

    return False

def update_partner():
    conn = create_connection()  # Assuming a function that creates a DB connection
    cursor = conn.cursor()

    partner_id_input = input("Enter Partner ID to update details: ").strip()
    if not partner_id_input.isdigit():
        print("Invalid input. Partner ID must be an integer.")
        conn.close()
        return

    partner_id = int(partner_id_input)

    # Fetch current partner details
    cursor.execute('''
    SELECT 
        id, name, mobile, email, address, pan, aadhaar, account_id
    FROM 
        Partner
    WHERE 
        id = ?
    ''', (partner_id,))

    partner = cursor.fetchone()

    if not partner:
        print(f"No partner found with the ID {partner_id}.")
        conn.close()
        return

    # Display current partner details in a horizontal table format
    partner_details = [[
        partner[0], partner[1], partner[2], partner[3], partner[4], partner[5], partner[6],
        partner[7] if partner[7] else "None"
    ]]
    headers = [
        "Partner ID", "Name", "Mobile", "Email", "Address", "PAN", "Aadhaar", "Associated Account IDs"
    ]

    print("\nCurrent Partner Details:")
    print(tabulate(partner_details, headers=headers, tablefmt="grid"))

    # Display the available fields to update by number
    print("\nWhich fields would you like to update? Enter the numbers (comma-separated):")
    print("1. Name")
    print("2. Mobile")
    print("3. Email")
    print("4. Address")
    print("5. PAN")
    print("6. Aadhaar")
    print("7. Associated Account IDs")

    # Ask user for input on which fields they want to update
    fields_to_update = input("\nEnter the numbers of the fields you want to update (e.g., 1,3,5): ").strip().split(',')
    fields_to_update = [field.strip() for field in fields_to_update]

    updates = {}

    # Loop through the selected fields and ask for new values
    for field in fields_to_update:
        if field == '1':  # Update Name
            new_name = input(f"Enter new Name (leave blank to keep '{partner[1]}'): ").strip()
            if new_name:
                updates['name'] = new_name

        elif field == '2':  # Update Mobile
            new_mobile = input(f"Enter new Mobile (leave blank to keep '{partner[2]}'): ").strip()
            if new_mobile and validate_mobile(new_mobile):
                updates['mobile'] = new_mobile
            elif new_mobile:
                print("Invalid mobile number! Keeping the existing mobile.")

        elif field == '3':  # Update Email
            new_email = input(f"Enter new Email (leave blank to keep '{partner[3]}'): ").strip()
            if new_email and validate_email(new_email):
                updates['email'] = new_email
            elif new_email:
                print("Invalid email address! Keeping the existing email.")

        elif field == '4':  # Update Address
            new_address = input(f"Enter new Address (leave blank to keep '{partner[4]}'): ").strip()
            if new_address:
                updates['address'] = new_address

        elif field == '5':  # Update PAN
            new_pan = input(f"Enter new PAN (leave blank to keep '{partner[5]}'): ").strip()
            if new_pan and validate_pan(new_pan):
                updates['pan'] = new_pan
            elif new_pan:
                print("Invalid PAN number! Keeping the existing PAN.")

        elif field == '6':  # Update Aadhaar
            new_aadhaar = input(f"Enter new Aadhaar (leave blank to keep '{partner[6]}'): ").strip()
            if new_aadhaar and validate_aadhaar(new_aadhaar):
                updates['aadhaar'] = new_aadhaar
            elif new_aadhaar:
                print("Invalid Aadhaar number! Keeping the existing Aadhaar.")

        elif field == '7':  # Update Associated Account IDs
            new_account_ids = input(f"Enter new Account IDs (comma-separated, leave blank to keep '{partner[7]}'): ").strip()
            if new_account_ids:
                account_ids = new_account_ids.split(',')
                valid_account_ids = []

                for account_id in account_ids:
                    account_id = account_id.strip()

                    # Check if the account ID is linked with another entity
                    if is_account_linked(cursor, account_id, exclude_partner_id=partner_id):
                        print(f"Account ID {account_id} is already linked with another entity. Skipping...")
                    else:
                        # Ensure the account exists
                        cursor.execute("SELECT id FROM Account WHERE id = ?", (account_id,))
                        if cursor.fetchone():
                            valid_account_ids.append(account_id)
                        else:
                            print(f"Account ID {account_id} is invalid. Skipping...")

                if valid_account_ids:
                    updates['account_id'] = ','.join(valid_account_ids)
                else:
                    print("No valid account IDs provided. Keeping the existing associated accounts.")

        else:
            print(f"Invalid field number: {field}. Skipping...")

    # Apply updates if any changes were made
    if updates:
        set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values())
        values.append(partner_id)

        cursor.execute(f'''
        UPDATE Partner
        SET {set_clause}
        WHERE id = ?
        ''', values)

        conn.commit()

        # Fetch updated partner details
        cursor.execute('''
        SELECT 
            id, name, mobile, email, address, pan, aadhaar, account_id
        FROM 
            Partner
        WHERE 
            id = ?
        ''', (partner_id,))

        updated_partner = cursor.fetchone()

        # Display updated partner details in horizontal table format
        updated_partner_details = [[
            updated_partner[0], updated_partner[1], updated_partner[2], updated_partner[3], 
            updated_partner[4], updated_partner[5], updated_partner[6], 
            updated_partner[7] if updated_partner[7] else "None"
        ]]

        print("\nPartner successfully updated:")
        print(tabulate(updated_partner_details, headers=headers, tablefmt="grid"))

    else:
        print("No updates were made.")

    conn.close()

def is_account_linked(cursor, account_id):
    """
    Check if the account ID is linked with any other entity (Borrower, Investor, Facilitator, Partner).
    """
    # Check in the Borrower table
    cursor.execute("SELECT id FROM Borrower WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check in the Investor table
    cursor.execute("SELECT id FROM Investor WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check in the Facilitator table
    cursor.execute("SELECT id FROM Facilitator WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Check in the Partner table
    cursor.execute("SELECT id FROM Partner WHERE account_id LIKE ?", ('%' + str(account_id) + '%',))
    if cursor.fetchone():
        return True

    # Additional check for Firm if required

    return False

def insert_firm():
    conn = create_connection()
    cursor = conn.cursor()

    # Input firm details
    print("Enter Firm Details:")
    name = input("Firm Name: ").strip()

    mobile = input("Mobile: ").strip()
    while not validate_mobile(mobile):
        print("Invalid mobile number! Must be a 10-digit number.")
        mobile = input("Mobile: ").strip()

    email = input("Email: ").strip()
    while not validate_email(email):
        print("Invalid email address!")
        email = input("Email: ").strip()

    address = input("Address: ").strip()

    pan = input("PAN: ").strip()
    while not validate_pan(pan):
        print("Invalid PAN number! Must be a 10-character alphanumeric string in the format ABCDE1234F.")
        pan = input("PAN: ").strip()

    aadhaar = input("Aadhaar: ").strip()
    while not validate_aadhaar(aadhaar):
        print("Invalid Aadhaar number! Must be a 12-digit number.")
        aadhaar = input("Aadhaar: ").strip()

    # Input and validate multiple account IDs as an optional comma-separated list
    account_ids_input = input("Enter account IDs to link (comma-separated, or leave blank to skip): ").strip()
    valid_account_ids = []

    if account_ids_input:
        account_ids = account_ids_input.split(',')

        for account_id in account_ids:
            account_id = account_id.strip()
            cursor.execute("SELECT id FROM Account WHERE id = ?", (account_id,))
            account = cursor.fetchone()
            if account is None:
                print(f"No account found with ID {account_id}. Skipping...")
            elif is_account_linked(cursor, account_id):
                print(f"Account ID {account_id} is already linked to another entity. Skipping...")
            else:
                valid_account_ids.append(account_id)

        if not valid_account_ids:
            print("No valid account IDs were provided. Firm will not be linked to any accounts.")

    # Use a default value if no account IDs are provided
    account_ids_str = ','.join(valid_account_ids) if valid_account_ids else "None"

    # Insert the firm details into the Firm table
    cursor.execute('''
    INSERT INTO Firm (name, mobile, email, address, pan, aadhaar, account_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, mobile, email, address, pan, aadhaar, account_ids_str))

    print(f"Firm successfully inserted with linked Account IDs {account_ids_str if account_ids_str != 'None' else 'None'}.")

    # Fetch and display the inserted firm details in a horizontal format
    cursor.execute('''
    SELECT 
        id, name, mobile, email, address, pan, aadhaar, account_id
    FROM 
        Firm
    WHERE 
        mobile = ? AND email = ?
    ''', (mobile, email))

    firm = cursor.fetchone()

    # Display the inserted firm details in a horizontal table format
    headers = ["ID", "Firm Name", "Mobile", "Email", "Address", "PAN", "Aadhaar", "Account IDs"]
    firm_details = [[
        firm[0],
        firm[1],
        firm[2],
        firm[3],
        firm[4],
        firm[5],
        firm[6],
        firm[7] if firm[7] else "None"
    ]]

    print("\nFirm Details:")
    print(tabulate(firm_details, headers=headers, tablefmt="grid"))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

def view_Firm():
    conn = create_connection()  # Assuming a function that creates a DB connection
    cursor = conn.cursor()

    print("Choose an option:")
    print("1. View a single firm by ID")
    print("2. View all firms")
    choice = input("Enter the number corresponding to your choice: ").strip()

    if choice == '1':
        # View a single firm
        firm_id_input = input("Enter Firm ID to view details: ").strip()

        if not firm_id_input.isdigit():
            print("Invalid input. Firm ID must be an integer.")
            conn.close()
            return

        firm_id = int(firm_id_input)

        # Fetch firm details from the Firm table
        cursor.execute('''
        SELECT 
            id, name, mobile, email, address, pan, account_id, 
             registered_date, members, percent_owned, firm_state
        FROM 
            Firm
        WHERE 
            id = ?
        ''', (firm_id,))

        firm = cursor.fetchone()

        if not firm:
            print(f"No firm found with the ID {firm_id}.")
            conn.close()
            return

        # Display firm details in a horizontal table format
        firm_details = [[
            firm[0], firm[1], firm[2], firm[3], firm[4], firm[5],
            firm[6] if firm[6] else "None", firm[7], firm[8], firm[9], firm[10]
        ]]
        headers = [
            "Firm ID", "Name", "Mobile", "Email", "Address", "PAN", "Associated Account IDs", 
             "Registered Date", "Members", "Percent Owned (%)", "Firm State"
        ]

        print("\nFirm Details:")
        print(tabulate(firm_details, headers=headers, tablefmt="grid"))

    elif choice == '2':
        # View all firms
        cursor.execute('''
        SELECT 
            id, name, mobile, email, address, pan, account_id, 
         registered_date, members, percent_owned, firm_state
        FROM 
            Firm
        ''')

        firms = cursor.fetchall()

        if not firms:
            print("No firms found.")
            conn.close()
            return

        # Display all firm details in a horizontal table format
        firm_details = []
        for firm in firms:
            firm_details.append([
                firm[0], firm[1], firm[2], firm[3], firm[4], firm[5],
                firm[6] if firm[6] else "None", firm[7], firm[8], firm[9], firm[10]
            ])

        headers = [
            "Firm ID", "Name", "Mobile", "Email", "Address", "PAN", "Associated Account IDs", 
             "Registered Date", "Members", "Percent Owned (%)", "Firm State"
        ]

        print("\nAll Firms:")
        print(tabulate(firm_details, headers=headers, tablefmt="grid"))

    else:
        print("Invalid choice. Please enter 1 or 2.")

    conn.close()


def is_account_linked(cursor, account_id, exclude_firm_id=None):
    """
    Check if the account ID is already linked with other entities (Borrower, Investor, Partner),
    excluding the current firm being updated.
    """
    # Check if the account ID is linked to a borrower
    cursor.execute("SELECT id FROM Borrower WHERE account_id LIKE ? AND id != ?", ('%' + str(account_id) + '%', exclude_firm_id))
    if cursor.fetchone():
        return True

    # Check if the account ID is linked to an investor
    cursor.execute("SELECT id FROM Investor WHERE account_id LIKE ? AND id != ?", ('%' + str(account_id) + '%', exclude_firm_id))
    if cursor.fetchone():
        return True

    # Check if the account ID is linked to a partner
    cursor.execute("SELECT id FROM Partner WHERE account_id LIKE ? AND id != ?", ('%' + str(account_id) + '%', exclude_firm_id))
    if cursor.fetchone():
        return True

    return False

def update_Firm():
    conn = create_connection()  # Assuming a function that creates a DB connection
    cursor = conn.cursor()

    firm_id_input = input("Enter Firm ID to update details: ").strip()
    if not firm_id_input.isdigit():
        print("Invalid input. Firm ID must be an integer.")
        conn.close()
        return

    firm_id = int(firm_id_input)

    # Fetch current firm details
    cursor.execute('''
    SELECT 
        id, name, mobile, email, address, pan, account_id, 
     registered_date, members, percent_owned, firm_state
    FROM 
        Firm
    WHERE 
        id = ?
    ''', (firm_id,))

    firm = cursor.fetchone()

    if not firm:
        print(f"No firm found with the ID {firm_id}.")
        conn.close()
        return

    # Display current firm details in a horizontal table format
    firm_details = [[
        firm[0], firm[1], firm[2], firm[3], firm[4], firm[5],
        firm[6] if firm[6] else "None", firm[7], firm[8], firm[9], firm[10]
    ]]
    headers = [
        "Firm ID", "Name", "Mobile", "Email", "Address", "PAN", "Associated Account IDs", 
         "Registered Date", "Members", "Percent Owned (%)", "Firm State"
    ]

    print("\nCurrent Firm Details:")
    print(tabulate(firm_details, headers=headers, tablefmt="grid"))

    # Display the available fields to update by number
    print("\nWhich fields would you like to update? Enter the numbers (comma-separated):")
    print("1. Name")
    print("2. Mobile")
    print("3. Email")
    print("4. Address")
    print("5. PAN")
    print("6. Associated Account IDs")
    print("7. Registered Date")
    print("8. Members")
    print("9. Percent Owned (%)")
    print("10. Firm State")

    # Ask user for input on which fields they want to update
    fields_to_update = input("\nEnter the numbers of the fields you want to update (e.g., 1,3,5): ").strip().split(',')
    fields_to_update = [field.strip() for field in fields_to_update]

    updates = {}

    # Loop through the selected fields and ask for new values
    for field in fields_to_update:
        if field == '1':  # Update Name
            new_name = input(f"Enter new Name (leave blank to keep '{firm[1]}'): ").strip()
            if new_name:
                updates['name'] = new_name

        elif field == '2':  # Update Mobile
            new_mobile = input(f"Enter new Mobile (leave blank to keep '{firm[2]}'): ").strip()
            if new_mobile and validate_mobile(new_mobile):
                updates['mobile'] = new_mobile
            elif new_mobile:
                print("Invalid mobile number! Keeping the existing mobile.")

        elif field == '3':  # Update Email
            new_email = input(f"Enter new Email (leave blank to keep '{firm[3]}'): ").strip()
            if new_email and validate_email(new_email):
                updates['email'] = new_email
            elif new_email:
                print("Invalid email address! Keeping the existing email.")

        elif field == '4':  # Update Address
            new_address = input(f"Enter new Address (leave blank to keep '{firm[4]}'): ").strip()
            if new_address:
                updates['address'] = new_address

        elif field == '5':  # Update PAN
            new_pan = input(f"Enter new PAN (leave blank to keep '{firm[5]}'): ").strip()
            if new_pan and validate_pan(new_pan):
                updates['pan'] = new_pan
            elif new_pan:
                print("Invalid PAN number! Keeping the existing PAN.")

        elif field == '6':  # Update Associated Account IDs
            new_account_ids = input(f"Enter new Account IDs (comma-separated, leave blank to keep '{firm[6]}'): ").strip()
            valid_account_ids = []

            if new_account_ids:
                account_ids = new_account_ids.split(',')
                for account_id in account_ids:
                    account_id = account_id.strip()

                    cursor.execute("SELECT id FROM Account WHERE id = ?", (account_id,))
                    account = cursor.fetchone()

                    if account is None:
                        print(f"No account found with ID {account_id}. Skipping...")
                    elif is_account_linked(cursor, account_id, exclude_firm_id=firm_id):
                        print(f"Account ID {account_id} is already linked with another entity. Skipping...")
                    else:
                        valid_account_ids.append(account_id)

                if valid_account_ids:
                    updates['account_id'] = ','.join(valid_account_ids)

        elif field == '7':  # Update Registered Date
            new_registered_date = input(f"Enter new Registered Date (leave blank to keep '{firm[8]}'): ").strip()
            if new_registered_date:
                updates['registered_date'] = new_registered_date

        elif field == '8':  # Update Members
            new_members = input(f"Enter new Members count (leave blank to keep '{firm[9]}'): ").strip()
            if new_members.isdigit():
                updates['members'] = int(new_members)

        elif field == '9':  # Update Percent Owned (%)
            new_percent_owned = input(f"Enter new Percent Owned (%) (leave blank to keep '{firm[10]}'): ").strip()
            if new_percent_owned.replace('.', '', 1).isdigit():
                updates['percent_owned'] = float(new_percent_owned)

        elif field == '10':  # Update Firm State
            new_firm_state = input(f"Enter new Firm State (ACTIVE, INACTIVE, CLOSED) (leave blank to keep '{firm[11]}'): ").strip().upper()
            if new_firm_state and validate_firm_state(new_firm_state):
                updates['firm_state'] = new_firm_state
            elif new_firm_state:
                print("Invalid firm state! Keeping the existing state.")

        else:
            print(f"Invalid field number: {field}. Skipping...")

    # Apply updates if any changes were made
    if updates:
        set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values())
        values.append(firm_id)

        cursor.execute(f'''
        UPDATE Firm
        SET {set_clause}
        WHERE id = ?
        ''', values)

        conn.commit()

        # Fetch updated firm details
        cursor.execute('''
        SELECT 
            id, name, mobile, email, address, pan, account_id, 
         registered_date, members, percent_owned, firm_state
        FROM 
            Firm
        WHERE 
            id = ?
        ''', (firm_id,))

        updated_firm = cursor.fetchone()

        # Display updated firm details in horizontal table format
        updated_firm_details = [[
            updated_firm[0], updated_firm[1], updated_firm[2], updated_firm[3], 
            updated_firm[4], updated_firm[5], updated_firm[6] if updated_firm[6] else "None",
            updated_firm[7], updated_firm[8], updated_firm[9], updated_firm[10]
        ]]

        print("\nFirm successfully updated:")
        print(tabulate(updated_firm_details, headers=headers, tablefmt="grid"))

    else:
        print("No updates were made.")

    conn.close()

def insert_Asset():
    conn = create_connection()
    cursor = conn.cursor()

    # Allowed values for ASSETTYPE, ASSETMODE, and UNITS
    allowed_asset_types = ['LAND', 'PLOT', 'FLAT', 'VILLA', 'CASH_BALANCE', 'ONLINE_BALANCE']
    allowed_asset_modes = ['COLLATERAL_REGISTERED', 'COLLATERAL_MORTGAGE', 'COLLATERAL_TO_INVESTOR', 'SELF_OWNED', 'RETURNED']
    allowed_units = ['ACRES', 'HECTARES', 'SQ_YARDS', 'SQ_FEET', 'RUPEES', 'DOLLARS']

    # Function to present options and return the selected value
    def select_option(prompt, options):
        print(prompt)
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        while True:
            try:
                choice = int(input("Enter the number corresponding to your choice: "))
                if 1 <= choice <= len(options):
                    return options[choice - 1]
                else:
                    print(f"Invalid choice. Please select a number between 1 and {len(options)}.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    # Get user input for the asset details using the select_option function
    asset_type = select_option("Select Asset Type:", allowed_asset_types)
    asset_mode = select_option("Select Asset Mode:", allowed_asset_modes)
    holder_name = input("Enter Holder Name: ").strip()
    deed_id = input("Enter Deed ID: ").strip()

    # Input and validate size
    while True:
        try:
            size = float(input("Enter Size: ").strip())
            break
        except ValueError:
            print("Invalid input. Size must be a number.")

    units = select_option("Select Units:", allowed_units)

    # Insert the asset details into the Asset table
    cursor.execute('''
    INSERT INTO Asset (asset_type, asset_mode, holder_name, deed_id, size, units)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (asset_type, asset_mode, holder_name, deed_id, size, units))

    # Fetch the last inserted asset ID for display
    asset_id = cursor.lastrowid

    # Confirmation message with horizontal table format
    asset_details = [[
        asset_id, asset_type, asset_mode, holder_name, deed_id, size, units
    ]]
    
    headers = [
        "Asset ID", "Asset Type", "Asset Mode", "Holder Name", "Deed ID", "Size", "Units"
    ]

    print("\nAsset successfully inserted:")
    print(tabulate(asset_details, headers=headers, tablefmt="grid"))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

def view_Asset():
    conn = create_connection()
    cursor = conn.cursor()

    # Prompt the user for their choice
    print("Choose an option:")
    print("1. View a specific asset by ID")
    print("2. View all assets")
    choice = input("Enter the number corresponding to your choice: ").strip()

    if choice == '1':
        # Input: Asset ID for viewing details
        asset_id = int(input("Enter Asset ID to view details: "))

        # Fetch asset details from the Asset table
        cursor.execute('''
        SELECT 
            id, asset_type, asset_mode, holder_name, deed_id, size, units
        FROM 
            Asset
        WHERE 
            id = ?
        ''', (asset_id,))

        asset = cursor.fetchone()

        if not asset:
            print("No asset found with the given ID.")
            conn.close()
            return

        # Display asset details in horizontal format
        headers = [
            "Asset ID", "Asset Type", "Asset Mode", "Holder Name", "Deed ID", "Size", "Units"
        ]

        asset_details = [[
            asset[0], asset[1], asset[2], asset[3], asset[4], asset[5], asset[6]
        ]]

        print("\nAsset Details:")
        print(tabulate(asset_details, headers=headers, tablefmt="grid"))

    elif choice == '2':
        # Fetch all assets from the Asset table
        cursor.execute('''
        SELECT 
            id, asset_type, asset_mode, holder_name, deed_id, size, units
        FROM 
            Asset
        ''')

        assets = cursor.fetchall()

        if not assets:
            print("No assets found in the database.")
            conn.close()
            return

        # Display all assets in a horizontal table format
        headers = [
            "Asset ID", "Asset Type", "Asset Mode", "Holder Name", "Deed ID", "Size", "Units"
        ]

        asset_details = []

        for asset in assets:
            asset_details.append([
                asset[0], asset[1], asset[2], asset[3], asset[4], asset[5], asset[6]
            ])

        print("\nAll Assets:")
        print(tabulate(asset_details, headers=headers, tablefmt="grid"))

    else:
        print("Invalid choice. Please enter 1 or 2.")

    conn.close()

def update_Asset():
    conn = create_connection()
    cursor = conn.cursor()

    # Input: Asset ID for updating details
    asset_id_input = input("Enter Asset ID to update details: ").strip()
    if not asset_id_input.isdigit():
        print("Invalid input. Asset ID must be an integer.")
        conn.close()
        return
    asset_id = int(asset_id_input)

    # Fetch current asset details
    cursor.execute('''
    SELECT 
        id, asset_type, asset_mode, holder_name, deed_id, size, units
    FROM 
        Asset
    WHERE 
        id = ?
    ''', (asset_id,))

    asset = cursor.fetchone()

    if not asset:
        print("No asset found with the given ID.")
        conn.close()
        return

    # Display current asset details in horizontal format
    headers = [
        "Asset ID", "Asset Type", "Asset Mode", "Holder Name", "Deed ID", "Size", "Units"
    ]

    asset_details = [[
        asset[0], asset[1], asset[2], asset[3], asset[4], asset[5], asset[6]
    ]]

    print("\nCurrent Asset Details:")
    print(tabulate(asset_details, headers=headers, tablefmt="grid"))

    # Allowed values for ASSETTYPE, ASSETMODE, and UNITS
    allowed_asset_types = ['LAND', 'PLOT', 'FLAT', 'VILLA', 'CASH_BALANCE', 'ONLINE_BALANCE']
    allowed_asset_modes = ['COLLATERAL_REGISTERED', 'COLLATERAL_MORTGAGE', 'COLLATERAL_TO_INVESTOR', 'SELF_OWNED', 'RETURNED']
    allowed_units = ['ACRES', 'HECTARES', 'SQ_YARDS', 'SQ_FEET', 'RUPEES', 'DOLLARS']

    # Dictionary to store updates
    updates = {}

    # Function to handle updates
    def ask_for_update(field_name, current_value, allowed_options=None):
        """Helper function to ask the user if they want to update a specific field."""
        choice = input(f"\nDo you want to update {field_name}? (y/n): ").strip().lower()
        if choice == 'y':
            if allowed_options:
                # Display allowed options if present (for asset type, mode, and units)
                print(f"Select new {field_name}:")
                for i, option in enumerate(allowed_options, 1):
                    print(f"{i}. {option}")
                choice_input = input("Enter the number corresponding to your choice: ").strip()
                if choice_input.isdigit() and 1 <= int(choice_input) <= len(allowed_options):
                    return allowed_options[int(choice_input) - 1]
                else:
                    print(f"Invalid choice for {field_name}. Keeping original value.")
                    return current_value
            else:
                # For text fields, ask for new value
                new_value = input(f"Enter new {field_name} (leave blank to keep '{current_value}'): ").strip()
                if new_value:
                    return new_value
                else:
                    return current_value
        else:
            return current_value

    # Ask the user for each field if they want to update it
    updates['asset_type'] = ask_for_update("Asset Type", asset[1], allowed_asset_types)
    updates['asset_mode'] = ask_for_update("Asset Mode", asset[2], allowed_asset_modes)
    updates['holder_name'] = ask_for_update("Holder Name", asset[3])
    updates['deed_id'] = ask_for_update("Deed ID", asset[4])
    
    # Handle size separately because it requires numeric input validation
    new_size_input = ask_for_update("Size", str(asset[5]))
    if new_size_input.replace('.', '', 1).isdigit():  # Check if it's a valid float or int
        updates['size'] = float(new_size_input)
    else:
        print("Invalid size. Keeping original value.")
        updates['size'] = asset[5]

    updates['units'] = ask_for_update("Units", asset[6], allowed_units)

    # Apply updates if any
    set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
    values = list(updates.values())
    values.append(asset_id)

    cursor.execute(f'''
    UPDATE Asset
    SET {set_clause}
    WHERE id = ?
    ''', values)

    conn.commit()

    # Fetch and display updated asset details
    cursor.execute('''
    SELECT 
        id, asset_type, asset_mode, holder_name, deed_id, size, units
    FROM 
        Asset
    WHERE 
        id = ?
    ''', (asset_id,))

    updated_asset = cursor.fetchone()

    updated_asset_details = [[
        updated_asset[0], updated_asset[1], updated_asset[2], updated_asset[3], updated_asset[4],
        updated_asset[5], updated_asset[6]
    ]]

    print("\nAsset successfully updated:")
    print(tabulate(updated_asset_details, headers=headers, tablefmt="grid"))

    conn.close()

def get_next_id():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT MAX(id) FROM Loan')
    max_id = cursor.fetchone()[0]

    if max_id is None:
        next_id = 9
    else:
        next_id = max_id + 9

    conn.close()
    return next_id

def check_pan_exists(cursor, pan):
    cursor.execute('SELECT name FROM Borrower WHERE pan = ?', (pan,))
    return cursor.fetchone()


def insert_Loan():
    conn = create_connection()
    cursor = conn.cursor()

    id = get_next_id()

    name = input("Enter Loan Name: ")

    # Validate Recipient using PAN
    while True:
        pan = input("Enter Recipient PAN: ")
        recipient_row = check_pan_exists(cursor, pan)
        if recipient_row:
            recipient = recipient_row[0]
            print(f"Recipient found: {recipient}")
            break
        else:
            print("Invalid PAN. Please enter a valid PAN associated with a borrower.")

    principal = float(input("Enter Principal: "))
    interest_rate = float(input("Enter Interest Rate: "))

    # Choose Interest Frequency
    interest_frequencies = ["Monthly", "Quarterly", "Yearly", "3Yearly"]
    print("Select Interest Frequency:")
    for i, freq in enumerate(interest_frequencies, 1):
        print(f"{i}. {freq}")

    while True:
        try:
            freq_choice = int(input("Enter the number corresponding to the Interest Frequency: "))
            if 1 <= freq_choice <= len(interest_frequencies):
                interest_frequency = interest_frequencies[freq_choice - 1]
                break
            else:
                print("Invalid choice. Please select a valid number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Interest expected is now optional
    interest_expected_input = input("Enter Interest Expected (leave blank if none): ")
    interest_expected = float(interest_expected_input) if interest_expected_input else None

    interest_realized = float(input("Enter Interest Realized: "))
    interest_paid_up = float(input("Enter Interest Paid Up: "))
    loan_state = input("Enter Loan State(Active, Inactive, Closed): ")

    asset_id_input = input("Enter Asset ID (leave blank if none): ")
    asset_id = int(asset_id_input) if asset_id_input else None

    cursor.execute('''
    INSERT INTO Loan (
        name, recipient, principal, interest_rate, interest_frequency, 
        interest_expected, interest_realized, interest_paid_up, expenses, 
        loan_state, asset_id, id
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?)
    ''', (name, recipient, principal, interest_rate, interest_frequency, 
          interest_expected, interest_realized, interest_paid_up, 
          loan_state, asset_id, id))

    conn.commit()
    conn.close()

def view_Loan():
    conn = create_connection()
    cursor = conn.cursor()

    print("Choose an option:")
    print("1. View a specific loan")
    print("2. View all loans")

    try:
        choice = int(input("Enter the number corresponding to your choice: "))
        if choice == 1:
            loan_id = input("Enter Loan ID to view: ")

            cursor.execute('''
            SELECT * FROM Loan WHERE id = ?
            ''', (loan_id,))

            loan = cursor.fetchone()

            if loan:
                print("\nLoan Details:")
                print(f"ID: {loan[0]}")
                print(f"Name: {loan[1]}")
                print(f"Recipient: {loan[2]}")
                print(f"Principal: {loan[3]}")
                print(f"Interest Rate: {loan[4]}")
                print(f"Interest Frequency: {loan[5]}")
                print(f"Interest Expected: {loan[6]}")
                print(f"Interest Realized: {loan[7]}")
                print(f"Interest Paid Up: {loan[8]}")
                print(f"Expenses: {loan[9]}")
                print(f"Loan State: {loan[10]}")
                print(f"Asset ID: {loan[11]}")
            else:
                print("Loan not found.")

        elif choice == 2:
            cursor.execute('''
            SELECT * FROM Loan
            ''')

            loans = cursor.fetchall()

            if loans:
                print("\nAll Loans:")
                for loan in loans:
                    print(f"\nLoan ID: {loan[0]}")
                    print(f"Name: {loan[1]}")
                    print(f"Recipient: {loan[2]}")
                    print(f"Principal: {loan[3]}")
                    print(f"Interest Rate: {loan[4]}")
                    print(f"Interest Frequency: {loan[5]}")
                    print(f"Interest Expected: {loan[6]}")
                    print(f"Interest Realized: {loan[7]}")
                    print(f"Interest Paid Up: {loan[8]}")
                    print(f"Expenses: {loan[9]}")
                    print(f"Loan State: {loan[10]}")
                    print(f"Asset ID: {loan[11]}")
                    print("-" * 30)
            else:
                print("No loans found.")
        else:
            print("Invalid choice. Please select either 1 or 2.")

    except ValueError:
        print("Invalid input. Please enter a number.")

    conn.close()

def update_Loan():
    conn = create_connection()
    cursor = conn.cursor()

    id = int(input("Enter ID to update: "))

    # Fetch the current loan details
    cursor.execute('SELECT * FROM LOAN WHERE ID = ?', (id,))
    loan = cursor.fetchone()

    if loan:
        print("Leave blank to keep the current value.")
        name = input(f"New Loan Name ({loan[1]}): ") or loan[1]
        recipient = input(f"New Recipient ({loan[2]}): ") or loan[2]
        principal = input(f"New Principal ({loan[3]}): ") or loan[3]
        interest_rate = input(f"New Interest Rate ({loan[4]}): ") or loan[4]
        interest_frequency = input(f"New Interest Frequency ({loan[5]}): ") or loan[5]
        interest_expected = input(f"New Expected Interest ({loan[6]}): ") or loan[6]
        interest_realized = input(f"New Realized Interest ({loan[7]}): ") or loan[7]
        interest_paid_up = input(f"New Paid-Up Interest ({loan[8]}): ") or loan[8]
        expenses = input(f"New Expenses ({loan[9]}): ") or loan[9]
        loan_state = input(f"New Loan State ({loan[10]}): ") or loan[10]
        asset_id = input(f"New Asset ID ({loan[11]}): ") or loan[11]

        # Update the loan
        cursor.execute('''
        UPDATE LOAN
        SET 
            NAME = ?, 
            RECIPIENT = ?, 
            PRINCIPAL = ?, 
            INTEREST_RATE = ?, 
            INTEREST_FREQUENCY = ?, 
            INTEREST_EXPECTED = ?, 
            INTEREST_REALIZED = ?, 
            INTEREST_PAID_UP = ?, 
            EXPENSES = ?, 
            LOAN_STATE = ?, 
            ASSET_ID = ?
        WHERE 
            ID = ?
        ''', (name, recipient, principal, interest_rate, interest_frequency, interest_expected,
              interest_realized, interest_paid_up, expenses, loan_state, asset_id, id))

        conn.commit()
        print("Loan updated successfully.")
    else:
        print("Loan not found.")

    conn.close()

def insert_Transaction():
    conn = create_connection()
    cursor = conn.cursor()

    # Provide a list of transaction types for the user to select from
    transaction_types = [
        "BUSINESS EXPENSES",
        "PRINCIPAL FROM INVESTOR",
        "PRINCIPAL TO INVESTOR",
        "PRINCIPAL TO BORROWER",
        "PRINCIPAL FROM BORROWER",
        "INTEREST FROM BORROWER",
        "INTEREST TOINVESTOR"
    ]

    print("Select Transaction Type:")
    for i, t_type in enumerate(transaction_types, 1):
        print(f"{i}. {t_type}")

    try:
        choice = int(input("Enter the number corresponding to the Transaction Type: "))
        if 1 <= choice <= len(transaction_types):
            transaction_type = transaction_types[choice - 1]
        else:
            print("Invalid choice. Please select a valid number from the list.")
            conn.close()
            return
    except ValueError:
        print("Invalid input. Please enter a number corresponding to the Transaction Type.")
        conn.close()
        return

    business_expense_subtype = None
    if transaction_type == 'BUSINESS EXPENSES':
        # Provide a list of business expense subtypes for the user to select from
        expense_subtypes = ["Legal", "Travel", "Registration", "Brokerage", "Other"]

        print("Select Business Expense Subtype:")
        for i, subtype in enumerate(expense_subtypes, 1):
            print(f"{i}. {subtype}")

        try:
            subtype_choice = int(input("Enter the number corresponding to the Business Expense Subtype: "))
            if 1 <= subtype_choice <= len(expense_subtypes):
                business_expense_subtype = expense_subtypes[subtype_choice - 1]
            else:
                print("Invalid choice. Please select a valid number from the list.")
                conn.close()
                return
        except ValueError:
            print("Invalid input. Please enter a number corresponding to the Business Expense Subtype.")
            conn.close()
            return

    amount = float(input("Enter Transaction Amount: "))
    mode = input("Enter Transaction Mode (CASH, ONLINE): ")
    date = input("Enter Date (YYYY-MM-DD): ")  # Adjust date format for SQLite
    from_account = input("Enter From Account ID: ")
    to_account = input("Enter To Account ID: ")
    loan_id = input("Enter Loan ID: ")
    via = input("Enter Via: ")
    notes = input("Enter Notes: ")

    # Convert IDs to integers if provided
    from_account = int(from_account) if from_account else None
    to_account = int(to_account) if to_account else None
    loan_id = int(loan_id) if loan_id else None

    # Insert the transaction into the Transactions table
    cursor.execute('''
    INSERT INTO Transactions (
        transaction_type, business_expense_subtype, amount, mode, date, from_account, to_account, loan_id, via, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (transaction_type, business_expense_subtype, amount, mode, date, from_account, to_account, loan_id, via, notes))

    # Manually update the corresponding Loan record if the transaction type matches specific criteria
    if transaction_type in ['PRINCIPAL TO BORROWER', 'PRINCIPAL FROM BORROWER', 'BUSINESS EXPENSES'] and loan_id:
        # Adjust principal or expenses based on transaction type
        if transaction_type == 'PRINCIPAL TO BORROWER':
            cursor.execute('''
            UPDATE Loan
            SET principal = principal + ?
            WHERE id = ?
            ''', (amount, loan_id))
        elif transaction_type == 'PRINCIPAL FROM BORROWER':
            cursor.execute('''
            UPDATE Loan
            SET principal = principal - ?
            WHERE id = ?
            ''', (amount, loan_id))
        elif transaction_type == 'BUSINESS EXPENSES':
            cursor.execute('''
            UPDATE Loan
            SET expenses = expenses + ?
            WHERE id = ?
            ''', (amount, loan_id))

    conn.commit()
    conn.close()
    print("Transaction added and Loan updated successfully.")

def view_Transaction():
    conn = create_connection()
    cursor = conn.cursor()

    # Get user choice: view a specific transaction or all transactions
    choice = input("Enter '1' to view a specific transaction or '2' to view all transactions: ")

    if choice == '1':
        try:
            transaction_id = int(input("Enter Transaction ID: "))
        except ValueError:
            print("Invalid input. Please enter a valid integer for Transaction ID.")
            conn.close()
            return

        # Retrieve the specific transaction by ID
        cursor.execute('''
        SELECT 
            id, 
            transaction_type, 
            business_expense_subtype, 
            amount, 
            mode, 
            date, 
            from_account, 
            to_account, 
            loan_id, 
            via, 
            notes 
        FROM 
            Transactions
        WHERE id = ?
        ''', (transaction_id,))
        
        transaction = cursor.fetchone()

        # Check if the transaction was found
        if transaction:
            print("Transaction Details:")
            print("-" * 60)
            print(f"ID: {transaction[0]}")
            print(f"Type: {transaction[1]}")
            print(f"Subtype: {transaction[2] or 'N/A'}")
            print(f"Amount: {transaction[3]}")
            print(f"Mode: {transaction[4]}")
            print(f"Date: {transaction[5]}")
            print(f"From Account: {transaction[6] or 'N/A'}")
            print(f"To Account: {transaction[7] or 'N/A'}")
            print(f"Loan ID: {transaction[8] or 'N/A'}")
            print(f"Via: {transaction[9]}")
            print(f"Notes: {transaction[10]}")
        else:
            print("Transaction not found.")

    elif choice == '2':
        # Retrieve all transactions
        cursor.execute('''
        SELECT 
            id, 
            transaction_type, 
            business_expense_subtype, 
            amount, 
            mode, 
            date, 
            from_account, 
            to_account, 
            loan_id, 
            via, 
            notes 
        FROM 
            Transactions
        ''')
        
        transactions = cursor.fetchall()

        # Check if any transactions were found
        if transactions:
            print("All Transactions:")
            print("-" * 100)
            for transaction in transactions:
                print(f"ID: {transaction[0]}")
                print(f"Type: {transaction[1]}")
                print(f"Subtype: {transaction[2] or 'N/A'}")
                print(f"Amount: {transaction[3]}")
                print(f"Mode: {transaction[4]}")
                print(f"Date: {transaction[5]}")
                print(f"From Account: {transaction[6] or 'N/A'}")
                print(f"To Account: {transaction[7] or 'N/A'}")
                print(f"Loan ID: {transaction[8] or 'N/A'}")
                print(f"Via: {transaction[9]}")
                print(f"Notes: {transaction[10]}")
                print("-" * 100)
        else:
            print("No transactions found.")

    else:
        print("Invalid choice. Please enter '1' or '2'.")

    conn.close()

def update_Transaction():
    conn = create_connection()
    cursor = conn.cursor()

    try:
        # Get the transaction ID to update
        transaction_id = int(input("Enter Transaction ID to update: "))
    except ValueError:
        print("Invalid input. Please enter a valid integer for Transaction ID.")
        return

    # Check if the transaction exists
    cursor.execute('SELECT * FROM Transactions WHERE id = ?', (transaction_id,))
    transaction = cursor.fetchone()

    if not transaction:
        print("Transaction not found.")
        return

    # Display current transaction details
    print("Current Transaction Details:")
    print("-" * 60)
    print(f"ID: {transaction[0]}")
    print(f"Type: {transaction[1]}")
    print(f"Subtype: {transaction[2] or 'N/A'}")
    print(f"Amount: {transaction[3]}")
    print(f"Mode: {transaction[4]}")
    print(f"Date: {transaction[5]}")
    print(f"From Account: {transaction[6] or 'N/A'}")
    print(f"To Account: {transaction[7] or 'N/A'}")
    print(f"Loan ID: {transaction[8] or 'N/A'}")
    print(f"Via: {transaction[9]}")
    print(f"Notes: {transaction[10]}")
    print("-" * 60)

    # Get updated values from the user
    transaction_type = input(f"Enter new Transaction Type (current: {transaction[1]}): ") or transaction[1]
    business_expense_subtype = input(f"Enter new Business Expense Subtype (current: {transaction[2] or 'N/A'}): ") or transaction[2]
    amount = input(f"Enter new Amount (current: {transaction[3]}): ") or transaction[3]
    mode = input(f"Enter new Transaction Mode (current: {transaction[4]}): ") or transaction[4]
    date = input(f"Enter new Date (current: {transaction[5]}): ") or transaction[5]
    from_account = input(f"Enter new From Account ID (current: {transaction[6] or 'N/A'}): ") or transaction[6]
    to_account = input(f"Enter new To Account ID (current: {transaction[7] or 'N/A'}): ") or transaction[7]
    loan_id = input(f"Enter new Loan ID (current: {transaction[8] or 'N/A'}): ") or transaction[8]
    via = input(f"Enter new Via (current: {transaction[9]}): ") or transaction[9]
    notes = input(f"Enter new Notes (current: {transaction[10]}): ") or transaction[10]

    # Convert numeric inputs back to the correct type
    amount = float(amount)
    from_account = int(from_account) if from_account else None
    to_account = int(to_account) if to_account else None
    loan_id = int(loan_id) if loan_id else None

    # Update the transaction in the database
    cursor.execute('''
    UPDATE Transactions
    SET transaction_type = ?, 
        business_expense_subtype = ?, 
        amount = ?, 
        mode = ?, 
        date = ?, 
        from_account = ?, 
        to_account = ?, 
        loan_id = ?, 
        via = ?, 
        notes = ?
    WHERE id = ?
    ''', (transaction_type, business_expense_subtype, amount, mode, date, from_account, to_account, loan_id, via, notes, transaction_id))

    conn.commit()
    conn.close()

# Remaining code including submenus and main menu

def borrower_submenu():
    while True:
        print("\nBorrower Submenu")
        print("1. Add New Borrower")
        print("2. View Borrower")
        print("3. Update Borrower")
        print("0. Back to Main Menu")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            insert_borrower()
        elif choice == '2':
            view_borrower()
        elif choice == '3':
            update_borrower()
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")

def Facilitator_submenu():
    while True:
        print("\nFacilitator Submenu")
        print("1. Add New Facilitator")
        print("2. View Facilitator")
        print("3. Update Facilitator")
        print("0. Back to Main Menu")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            insert_Facilitator()
        elif choice == '2':
            view_Facilitator()
        elif choice == '3':
            update_Facilitator()
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")

def Investor_submenu():
    while True:
        print("\nInvestor Submenu")
        print("1. Add New Investor")
        print("2. View Investor")
        print("3. Update Investor")
        print("0. Back to Main Menu")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            insert_Investor()
        elif choice == '2':
            view_Investor()
        elif choice == '3':
            update_Investor()
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")

def Partner_submenu():
    while True:
        print("\nPartner Submenu")
        print("1. Add New Partner")
        print("2. View Partner")
        print("3. Update Partner")
        print("0. Back to Main Menu")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            insert_Partner()
        elif choice == '2':
            view_Partner()
        elif choice == '3':
            update_Partner()
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")

def Firm_submenu():
    while True:
        print("\nFirm Submenu")
        print("1. Add New Firm")
        print("2. View Firm")
        print("3. Update Firm")
        print("0. Back to Main Menu")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            insert_Firm()
        elif choice == '2':
            view_Firm()
        elif choice == '3':
            update_Firm()
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")

def Asset_submenu():
    while True:
        print("\nAsset Submenu")
        print("1. Add New Asset")
        print("2. View Asset")
        print("3. Update Asset")
        print("0. Back to Main Menu")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            insert_Asset()
        elif choice == '2':
            view_Asset()
        elif choice == '3':
            update_Asset()
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")

def Loan_submenu():
    while True:
        print("\nLoan Submenu")
        print("1. Add New Loan")
        print("2. View Loan")
        print("3. Update Loan")
        print("0. Back to Main Menu")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            insert_Loan()
        elif choice == '2':
            view_Loan()
        elif choice == '3':
            update_Loan()
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")

def Transaction_submenu():
    while True:
        print("\nTransaction Submenu")
        print("1. Add New Transaction")
        print("2. View Transaction")
        print("3. Update Transaction")
        print("0. Back to Main Menu")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            insert_Transaction()
        elif choice == '2':
            view_Transaction()
        elif choice == '3':
            update_Transaction()
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")

def Account_submenu():
    while True:
        print("\nAccount Submenu")
        print("1. Add New Account")
        print("2. View Account")
        print("3. Update Account")
        print("0. Back to Main Menu")
        choice = input("Enter your choice: ")
        
        if choice == '1':
            insert_Account()
        elif choice == '2':
            view_Account()
        elif choice == '3':
            update_Account()
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")



def main_menu():
    create_tables()  # Ensure tables are created
    while True:
        print("\nMain Menu")
        print("1. Borrower")
        print("2. Facilitator")
        print("3. Investor")
        print("4. Partner")
        print("5. Firm")
        print("6. Asset")
        print("7. Loan")
        print("8. Transaction")
        print("9. Account")
        print("0. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            borrower_submenu()
        elif choice == '2':
            Facilitator_submenu()
        elif choice == '3':
            Investor_submenu()
        elif choice == '4':
            Partner_submenu()
        elif choice == '5':
            Firm_submenu()
        elif choice == '6':
            Asset_submenu()
        elif choice == '7':
            Loan_submenu()
        elif choice == '8':
            Transaction_submenu()
        elif choice =='9':
            Account_submenu()    
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()
