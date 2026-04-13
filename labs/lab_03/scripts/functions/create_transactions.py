"""
Portfolio Transaction Entry System
Answers all lab queries with:
- Simple transaction entry (Query 1)
- Correct file paths (Query 2)
- Uniform structure with all required functions (Query 3)
- Full validation against prices_dates.json (Query 6)
"""

import json
from pathlib import Path

# ============================================================================
# FILE PATH SETUP (Query 2)
# ============================================================================

# Navigate from script location to data directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Up to lab_03/
TRANSACTIONS_DIR = BASE_DIR / "data" / "system" / "transactions"
TRANSACTIONS_DIR.mkdir(parents=True, exist_ok=True)
TRANSACTIONS_FILE = TRANSACTIONS_DIR / "transactions.json"

# Validation data file paths
DATA_SOURCE_DIR = BASE_DIR / "data" / "source"
PRICES_DATES_FILE = DATA_SOURCE_DIR / "prices_dates.json"


# ============================================================================
# VALIDATION FUNCTIONS (Query 6)
# ============================================================================

def load_prices_dates():
    """Load the prices_dates.json file for validation."""
    if not PRICES_DATES_FILE.exists():
        print(f"Warning: {PRICES_DATES_FILE} not found. Validation disabled.")
        return {}
    
    with open(PRICES_DATES_FILE, 'r') as f:
        return json.load(f)


def is_valid_date(date_str, prices_data):
    """Check if date exists in prices_dates.json."""
    if not prices_data:
        return True  # Skip validation if file not available
    
    # Check if any ticker has this date
    for ticker_data in prices_data.values():
        if date_str in ticker_data:
            return True
    return False


def is_valid_ticker(ticker, date_str, prices_data):
    """Check if ticker exists for the given date."""
    if not prices_data or ticker == "$$$$":
        return True
    
    return ticker in prices_data and date_str in prices_data.get(ticker, {})


def is_valid_price(ticker, date_str, input_price, prices_data):
    """
    Check if input price is within ±15% of the actual price.
    Returns True if valid, False otherwise.
    """
    if not prices_data or ticker == "$$$$":
        return True
    
    if ticker not in prices_data:
        return False
    
    if date_str not in prices_data[ticker]:
        return False
    
    actual_price = prices_data[ticker][date_str]
    lower_bound = actual_price * 0.85
    upper_bound = actual_price * 1.15
    
    return lower_bound <= input_price <= upper_bound


def get_validated_date(prices_data):
    """Get a valid date from user with validation."""
    while True:
        date_str = input("Enter transaction date (YYYY-MM-DD): ").strip()
        
        # Basic format check
        if len(date_str) != 10 or date_str[4] != '-' or date_str[7] != '-':
            print("Invalid format. Use YYYY-MM-DD.")
            continue
        
        # Check against prices_dates.json
        if not is_valid_date(date_str, prices_data):
            print(f"Error: {date_str} is not a valid trading date.")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry != 'y':
                return None
            continue
        
        return date_str


def get_validated_ticker(date_str, prices_data):
    """Get a valid ticker from user with validation."""
    while True:
        ticker = input("Enter ticker: ").strip().upper()
        
        if not is_valid_ticker(ticker, date_str, prices_data):
            print(f"Error: {ticker} is not valid for {date_str}.")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry != 'y':
                return None
            continue
        
        return ticker


def get_validated_price(ticker, date_str, prices_data):
    """Get a valid price from user with ±15% validation."""
    while True:
        try:
            price = float(input(f"Enter price per share for {ticker}: ").strip())
            
            if price <= 0:
                print("Price must be greater than 0.")
                continue
            
            if not is_valid_price(ticker, date_str, price, prices_data):
                if ticker in prices_data and date_str in prices_data[ticker]:
                    actual = prices_data[ticker][date_str]
                    print(f"Error: Price ${price:.2f} is not within ±15% of actual ${actual:.2f}")
                    print(f"  Valid range: ${actual * 0.85:.2f} - ${actual * 1.15:.2f}")
                else:
                    print(f"Error: No price data available for {ticker} on {date_str}")
                
                retry = input("Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    return None
                continue
            
            return price
            
        except ValueError:
            print("Please enter a valid number.")


# ============================================================================
# FILE I/O
# ============================================================================

def load_transactions(file_path=TRANSACTIONS_FILE):
    """Load transactions from JSON if the file exists."""
    if not file_path.exists():
        return []
    
    with open(file_path, "r") as f:
        return json.load(f)


def save_transactions(transactions, file_path=TRANSACTIONS_FILE):
    """Save the full transactions list back to JSON."""
    with open(file_path, "w") as f:
        json.dump(transactions, f, indent=4)


# ============================================================================
# INPUT HELPERS
# ============================================================================

def get_positive_float(prompt):
    """Repeatedly ask until the user enters a positive number."""
    while True:
        try:
            value = float(input(prompt).strip())
            if value <= 0:
                print("Value must be greater than 0.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number.")


def get_transaction_type():
    """Ask for one of the four allowed transaction types."""
    valid_types = {"contribution", "withdrawal", "buy", "sell"}
    
    while True:
        txn_type = input(
            "Enter transaction type (contribution, withdrawal, buy, sell): "
        ).strip().lower()
        
        if txn_type in valid_types:
            return txn_type
        
        print("Invalid transaction type.")


# ============================================================================
# TRANSACTION CREATION (Query 3 - Uniform Structure)
# ============================================================================

def create_transaction(transaction_date, prices_data):
    """
    Create one transaction for the given date.
    
    All transactions have the same 4 fields:
    - type
    - ticker
    - shares
    - price
    
    Cash is represented as ticker $$$$ with price 1.00
    """
    txn_type = get_transaction_type()

    if txn_type in {"contribution", "withdrawal"}:
        amount = get_positive_float("Enter amount: ")
        
        # Cash transaction - uniform structure
        transaction = {
            "date": transaction_date,
            "type": txn_type,
            "ticker": "$$$$",
            "shares": amount,  # For cash, shares = dollar amount
            "price": 1.00
        }

    elif txn_type in {"buy", "sell"}:
        ticker = get_validated_ticker(transaction_date, prices_data)
        if ticker is None:
            print("Transaction cancelled.")
            return None
        
        shares = get_positive_float("Enter number of shares: ")
        
        price = get_validated_price(ticker, transaction_date, prices_data)
        if price is None:
            print("Transaction cancelled.")
            return None

        transaction = {
            "date": transaction_date,
            "type": txn_type,
            "ticker": ticker,
            "shares": shares,
            "price": price
        }

    return transaction


# ============================================================================
# REQUIRED PORTFOLIO FUNCTIONS (Query 3)
# ============================================================================

def get_cash_balance(as_of_date):
    """
    Reconstruct the cash balance on a chosen day.
    
    Cash increases with:
    - contributions
    - sells (receive cash)
    
    Cash decreases with:
    - withdrawals
    - buys (spend cash)
    """
    transactions = load_transactions()
    balance = 0.0
    
    for txn in transactions:
        if txn["date"] > as_of_date:
            continue
            
        if txn["ticker"] == "$$$$":
            if txn["type"] == "contribution":
                balance += txn["shares"] * txn["price"]
            elif txn["type"] == "withdrawal":
                balance -= txn["shares"] * txn["price"]
        elif txn["type"] == "buy":
            balance -= txn["shares"] * txn["price"]
        elif txn["type"] == "sell":
            balance += txn["shares"] * txn["price"]
    
    return balance


def build_portfolio(as_of_date):
    """
    Reconstruct the portfolio on a chosen day from transaction history.
    
    Returns a dictionary of {ticker: shares} for all non-zero positions.
    """
    transactions = load_transactions()
    holdings = {}  # ticker -> shares
    
    for txn in transactions:
        if txn["date"] > as_of_date:
            continue
            
        ticker = txn["ticker"]
        
        if ticker == "$$$$":
            continue  # Cash handled separately by get_cash_balance()
            
        if ticker not in holdings:
            holdings[ticker] = 0.0
            
        if txn["type"] == "buy":
            holdings[ticker] += txn["shares"]
        elif txn["type"] == "sell":
            holdings[ticker] -= txn["shares"]
    
    # Remove positions that went to zero
    holdings = {k: v for k, v in holdings.items() if v > 0}
    
    return holdings


def list_transactions_for_ticker(ticker):
    """Show the dated transaction history for one ticker."""
    transactions = load_transactions()
    ticker_txns = [txn for txn in transactions if txn["ticker"] == ticker.upper()]
    
    if not ticker_txns:
        print(f"\nNo transactions found for {ticker}")
        return
    
    print(f"\nTransactions for {ticker}:")
    for txn in ticker_txns:
        print(f"  {txn['date']} - {txn['type']}: {txn['shares']} shares @ ${txn['price']:.2f}")


# ============================================================================
# MAIN TRANSACTION ENTRY SESSION (Query 1)
# ============================================================================

def transaction_entry_session():
    """
    Main workflow:
    - Load prior transactions
    - Set a working date
    - Enter multiple transactions for that date
    - Save after each new transaction
    """
    # Load validation data
    prices_data = load_prices_dates()
    if not prices_data:
        print("\nWARNING: Running without price validation!")
        print("prices_dates.json not found - all prices will be accepted.\n")
    
    transactions = load_transactions()
    print(f"\nLoaded {len(transactions)} existing transaction(s).")

    # Get initial working date with validation
    current_date = get_validated_date(prices_data)
    if current_date is None:
        print("Exiting.")
        return

    while True:
        print("\n" + "=" * 50)
        print("TRANSACTION MENU")
        print("=" * 50)
        print(f"Working Date: {current_date}")
        print()
        print("1. Add transaction")
        print("2. Change working date")
        print("3. Show all transactions")
        print("4. Show cash balance")
        print("5. Show portfolio")
        print("6. Show ticker history")
        print("7. Save and exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            transaction = create_transaction(current_date, prices_data)
            if transaction:
                transactions.append(transaction)
                save_transactions(transactions)
                print("\nTransaction added and saved:")
                print(f"  {transaction}")

        elif choice == "2":
            new_date = get_validated_date(prices_data)
            if new_date:
                current_date = new_date
                print(f"\nWorking date changed to {current_date}")

        elif choice == "3":
            if not transactions:
                print("\nNo transactions recorded.")
            else:
                print(f"\nAll Transactions ({len(transactions)} total):")
                for i, txn in enumerate(transactions, 1):
                    print(f"  {i}. {txn}")

        elif choice == "4":
            date = input("Enter date (YYYY-MM-DD): ").strip()
            balance = get_cash_balance(date)
            print(f"\n{'=' * 40}")
            print(f"Cash balance as of {date}: ${balance:,.2f}")
            print('=' * 40)

        elif choice == "5":
            date = input("Enter date (YYYY-MM-DD): ").strip()
            portfolio = build_portfolio(date)
            cash = get_cash_balance(date)
            
            print(f"\n{'=' * 40}")
            print(f"Portfolio as of {date}:")
            print('=' * 40)
            print(f"  Cash: ${cash:,.2f}")
            if portfolio:
                for ticker, shares in sorted(portfolio.items()):
                    print(f"  {ticker}: {shares:,.2f} shares")
            else:
                print("  (no stock positions)")
            print('=' * 40)

        elif choice == "6":
            ticker = input("Enter ticker: ").strip()
            list_transactions_for_ticker(ticker)

        elif choice == "7":
            save_transactions(transactions)
            print("\nTransactions saved. Exiting.")
            break

        else:
            print("\nInvalid choice. Please select 1-7.")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("PORTFOLIO TRANSACTION ENTRY SYSTEM")
    print("=" * 50)
    transaction_entry_session()
    