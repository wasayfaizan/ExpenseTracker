import csv
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time

# Define the CSV file to store expense data
CSV_FILE = 'expenses.csv'

def initialize_csv():
    """Initialize the CSV file with headers if it does not exist."""
    try:
        with open(CSV_FILE, mode='x', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Category', 'Description', 'Amount', 'Reminder', 'Email'])
    except FileExistsError:
        pass

def send_email(to_email, subject, body):
    """Send an email notification."""
    from_email = "your_email@example.com"
    password = "your_email_password"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")

def log_expense():
    """Log a new expense."""
    date = input("Enter the date (YYYY-MM-DD): ").strip()
    category = input("Enter the category: ").strip()
    description = input("Enter the description: ").strip()
    amount = float(input("Enter the amount: ").strip())
    reminder = input("Does this expense need a reminder? (yes/no): ").strip().lower()
    email = ""
    
    if reminder == 'yes':
        email = input("Enter your email address for the reminder: ").strip()
        reminder_date = datetime.strptime(date, '%Y-%m-%d') - timedelta(days=10)
        send_email(email, "Expense Reminder Set", f"You will be reminded about the expense '{description}' on {reminder_date.date()}.")
        print(f"Reminder set for {reminder_date.date()}.")

    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date, category, description, amount, reminder, email])
    
    print("Expense logged successfully.")

def read_expenses():
    """Read expenses from the CSV file, handling any parsing errors."""
    valid_rows = []
    try:
        with open(CSV_FILE, mode='r', newline='') as file:
            reader = csv.reader(file)
            headers = next(reader)
            for row in reader:
                if len(row) == 6:  # Ensure the row has the correct number of columns
                    valid_rows.append(row)
                else:
                    print(f"Skipping malformed row: {row}")
    except FileNotFoundError:
        print("No expenses logged yet.")
    return pd.DataFrame(valid_rows, columns=['Date', 'Category', 'Description', 'Amount', 'Reminder', 'Email'])

def view_expenses():
    """View all logged expenses."""
    df = read_expenses()
    if not df.empty:
        print(df)
    else:
        print("No expenses logged yet.")

def view_report():
    """View a report of spending over time."""
    df = read_expenses()
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date'])
        df['Amount'] = df['Amount'].astype(float)
        df.set_index('Date', inplace=True)
        report = df.groupby([df.index.year, df.index.month, 'Category'])['Amount'].sum().unstack().fillna(0)
        print(report)
    else:
        print("No expenses logged yet.")

def delete_expense():
    """Delete an expense by row number."""
    df = read_expenses()
    if not df.empty:
        print(df)
        row_number = int(input("Enter the row number of the expense to delete: "))
        if 0 <= row_number < len(df):
            df.drop(index=row_number, inplace=True)
            df.to_csv(CSV_FILE, index=False)
            print("Expense deleted successfully.")
        else:
            print("Invalid row number.")
    else:
        print("No expenses logged yet.")

def check_reminders():
    """Check for reminders and send email if needed."""
    df = read_expenses()
    if not df.empty:
        today = datetime.now().date()
        for index, row in df.iterrows():
            if row['Reminder'] == 'yes':
                expense_date = datetime.strptime(row['Date'], '%Y-%m-%d').date()
                reminder_date = expense_date - timedelta(days=10)
                if reminder_date == today:
                    send_email(row['Email'], "Expense Reminder", f"Reminder: You have an upcoming expense on {expense_date} for {row['Description']} amounting to {row['Amount']}.")
    else:
        print("No expenses to check for reminders.")

def main():
    initialize_csv()

    # Schedule the reminder checker to run daily
    schedule.every().day.at("09:00").do(check_reminders)

    while True:
        print("\nExpense Tracker Menu")
        print("1. Log an expense")
        print("2. View all expenses")
        print("3. View spending report")
        print("4. Delete an expense")
        print("5. Exit")
        
        choice = input("Enter your choice: ").strip()
        
        if choice == '1':
            log_expense()
        elif choice == '2':
            view_expenses()
        elif choice == '3':
            view_report()
        elif choice == '4':
            delete_expense()
        elif choice == '5':
            print("Exiting Expense Tracker. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

        # Run pending scheduled tasks
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
