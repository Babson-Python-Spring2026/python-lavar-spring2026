"""
Portfolio Transaction Entry System (Enhanced)

Implements all six major functions with STI (State, Transitions, Invariants)
documentation, centralized helpers, separated computation from display,
and full validation against source data files.

Functions:
    1. create_transaction(...)     - Gatekeeper for event quality
    2. list_transactions_for_ticker(ticker) - Reporting for one ticker
    3. build_stocks_by_date()      - Backbone of positions and splits
    4. build_cash_by_date()        - Combines transactions, dividends, stock state
    5. get_cash_by_date()          - Small reporting wrapper
    6. get_portfolio_by_date()     - Final composition layer
"""

import json
import csv
from pathlib import Path


# ============================================================================
# A. CENTRALIZED PATH DEFINITIONS
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Up to lab_03/

# Source data (read-only reference files)
DATA_SOURCE_DIR = BASE_DIR / "data" / "source"
PRICES_DATES_FILE = DATA_SOURCE_DIR / "prices_dates.json"
DIVIDENDS_FILE = DATA_SOURCE_DIR / "portfolio_dividends_20260331b.csv"
SPLITS_FILE = DATA_SOURCE_DIR / "portfolio_splits_true_splits_only_20260331b.csv"

# System data (generated/maintained by the program)
DATA_SYSTEM_DIR = BASE_DIR / "data" / "system"
MKT_DATES_FILE = DATA_SYSTEM_DIR / "mkt_dates.json"
TICKER_UNIVERSE_FILE = DATA_SYSTEM_DIR / "ticker_universe.json"

TRANSACTIONS_DIR = DATA_SYSTEM_DIR / "transactions"
TRANSACTIONS_DIR.mkdir(parents=True, exist_ok=True)
TRANSACTIONS_FILE = TRANSACTIONS_DIR / "transactions.json"

POSITIONS_DIR = DATA_SYSTEM_DIR / "positions_by_date"
POSITIONS_DIR.mkdir(parents=True, exist_ok=True)

STOCKS_BY_DATE_FILE = DATA_SYSTEM_DIR / "stocks_by_date.json"
CASH_BY_DATE_FILE = DATA_SYSTEM_DIR / "cash_by_date.json"


# ============================================================================
# B. CENTRALIZED FILE LOADING / SAVING
# ============================================================================

def load_json(path):
    """
    Load and return JSON data from a file path.
    Returns None if file does not exist.
    """
    p = Path(path)
    if not p.exists():
        print(f"Warning: {p} not found.")
        return None
    with open(p, "r") as f:
        return json.load(f)


def save_json(path, data):
    """Save data to a JSON file with indentation."""
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def load_csv_rows(path):
    """
    Load a CSV file and return a list of dictionaries (one per row).
    Returns empty list if file does not exist.
    """
    p = Path(path)
    if not p.exists():
        print(f"Warning: {p} not found.")
        return []
    with open(p, "r", newline="") as f:
        return list(csv.DictReader(f))


# ============================================================================
# C. CENTRALIZED VALIDATION HELPERS
# ============================================================================

def load_validation_data():
    """
    Load all reference data needed for validation.
    Returns a dictionary with keys: prices, mkt_dates, tickers.
    """
    return {
        "prices": load_json(PRICES_DATES_FILE) or {},
        "mkt_dates": load_json(MKT_DATES_FILE) or [],
        "tickers": load_json(TICKER_UNIVERSE_FILE) or [],
    }


def is_valid_date(date_str, val_data):
    """Check if date exists in mkt_dates.json."""
    if not val_data["mkt_dates"]:
        return True
    return date_str in val_data["mkt_dates"]


def is_valid_ticker(ticker, date_str, val_data):
    """Check if ticker exists in ticker_universe.json and has data for the date."""
    if ticker == "$$$$":
        return True
    if not val_data["tickers"]:
        return True
    if ticker not in val_data["tickers"]:
        return False
    # Also confirm ticker appears in prices_dates for that date
    if date_str in val_data["prices"]:
        return any(rec["ticker"] == ticker for rec in val_data["prices"][date_str])
    return False


def is_valid_price(ticker, date_str, input_price, val_data):
    """
    Check if input price is within ±15% of the actual price in prices_dates.json.
    """
    if ticker == "$$$$":
        return True
    if not val_data["prices"] or date_str not in val_data["prices"]:
        return True  # Can't validate without data
    for rec in val_data["prices"][date_str]:
        if rec["ticker"] == ticker:
            actual = rec["raw_price"]
            return (actual * 0.85) <= input_price <= (actual * 1.15)
    return False


def get_actual_price(ticker, date_str, val_data):
    """Look up the raw_price for a ticker on a given date. Returns None if not found."""
    if date_str not in val_data["prices"]:
        return None
    for rec in val_data["prices"][date_str]:
        if rec["ticker"] == ticker:
            return rec["raw_price"]
    return None


# ============================================================================
# C2. VALIDATED INPUT PROMPTS
# ============================================================================

def get_valid_date(val_data):
    """
    Prompt the user for a valid trading date.

    State read: mkt_dates
    Invariant: returned date is in mkt_dates.json or None
    """
    while True:
        date_str = input("Enter transaction date (YYYY-MM-DD): ").strip()
        if len(date_str) != 10 or date_str[4] != '-' or date_str[7] != '-':
            print("Invalid format. Use YYYY-MM-DD.")
            continue
        if not is_valid_date(date_str, val_data):
            print(f"Error: {date_str} is not a valid trading date.")
            if input("Try again? (y/n): ").strip().lower() != 'y':
                return None
            continue
        return date_str


def get_valid_transaction_type():
    """Prompt for one of the four allowed transaction types."""
    valid = {"contribution", "withdrawal", "buy", "sell"}
    while True:
        t = input("Transaction type (contribution/withdrawal/buy/sell): ").strip().lower()
        if t in valid:
            return t
        print("Invalid type. Choose: contribution, withdrawal, buy, sell.")


def get_valid_ticker(date_str, val_data):
    """
    Prompt for a valid ticker symbol.

    State read: ticker_universe, prices_dates
    Invariant: returned ticker is in the universe and has data for date, or None
    """
    while True:
        ticker = input("Enter ticker: ").strip().upper()
        if not is_valid_ticker(ticker, date_str, val_data):
            print(f"Error: {ticker} is not valid for {date_str}.")
            if input("Try again? (y/n): ").strip().lower() != 'y':
                return None
            continue
        return ticker


def get_valid_price(ticker, date_str, val_data):
    """
    Prompt for a price and validate within ±15% of actual.

    State read: prices_dates
    Invariant: returned price is within ±15% of actual, or None
    """
    while True:
        try:
            price = float(input(f"Price per share for {ticker}: ").strip())
            if price <= 0:
                print("Price must be greater than 0.")
                continue
            if not is_valid_price(ticker, date_str, price, val_data):
                actual = get_actual_price(ticker, date_str, val_data)
                if actual:
                    print(f"Error: ${price:.2f} not within ±15% of actual ${actual:.2f}")
                    print(f"  Valid range: ${actual * 0.85:.2f} - ${actual * 1.15:.2f}")
                else:
                    print(f"Error: No price data for {ticker} on {date_str}")
                if input("Try again? (y/n): ").strip().lower() != 'y':
                    return None
                continue
            return price
        except ValueError:
            print("Please enter a valid number.")


def get_positive_float(prompt):
    """Prompt until the user enters a positive number."""
    while True:
        try:
            val = float(input(prompt).strip())
            if val <= 0:
                print("Must be greater than 0.")
                continue
            return val
        except ValueError:
            print("Please enter a valid number.")


# ============================================================================
# HELPER: RECORD NUMBER GENERATION
# ============================================================================

def next_record_number(transactions):
    """
    Generate the next record number based on existing transactions.
    Returns max existing record_number + 1, or 1 if none exist.
    """
    if not transactions:
        return 1
    existing = [t.get("record_number", 0) for t in transactions]
    return max(existing) + 1


# ============================================================================
# 1. create_transaction(...)
# ============================================================================

def create_transaction(transaction_date, val_data, transactions):
    """
    Create one transaction for the given date.
    This function is the strict gatekeeper for event quality.

    State read:
        val_data (prices, mkt_dates, tickers), existing transactions

    Transitions:
        Creates a new transaction record with validated fields

    Invariant:
        Every returned transaction has: date, type, record_number,
        ticker, shares, price. All fields are validated.
        Cash uses ticker '$$$$' with price 1.00.
    """
    txn_type = get_valid_transaction_type()
    rec_num = next_record_number(transactions)

    if txn_type in {"contribution", "withdrawal"}:
        amount = get_positive_float("Enter amount: ")
        return {
            "date": transaction_date,
            "type": txn_type,
            "record_number": rec_num,
            "ticker": "$$$$",
            "shares": amount,
            "price": 1.00,
        }

    # buy or sell
    ticker = get_valid_ticker(transaction_date, val_data)
    if ticker is None:
        print("Transaction cancelled.")
        return None

    shares = get_positive_float("Number of shares: ")

    price = get_valid_price(ticker, transaction_date, val_data)
    if price is None:
        print("Transaction cancelled.")
        return None

    return {
        "date": transaction_date,
        "type": txn_type,
        "record_number": rec_num,
        "ticker": ticker,
        "shares": shares,
        "price": price,
    }


# ============================================================================
# 2. list_transactions_for_ticker(...)
# ============================================================================

def get_transactions_for_ticker(ticker, transactions):
    """
    Retrieve all transactions for a given ticker (data only, no printing).

    State read: transactions list
    Invariant: returns only transactions matching the ticker
    """
    return [t for t in transactions if t["ticker"] == ticker.upper()]


def format_shares(shares):
    """Format shares for display: integer if whole, otherwise 2 decimals."""
    if shares == int(shares):
        return str(int(shares))
    return f"{shares:,.2f}"


def print_transactions_header(ticker):
    """Print a formatted header for a ticker's transaction history."""
    print(f"\n{'=' * 60}")
    print(f"  Transaction History for {ticker}")
    print(f"{'=' * 60}")
    print(f"  {'Date':<12} {'Type':<14} {'Shares':>10} {'Price':>10}")
    print(f"  {'-' * 12} {'-' * 14} {'-' * 10} {'-' * 10}")


def print_transactions_table(ticker_txns):
    """Print formatted rows for a list of transactions."""
    for t in ticker_txns:
        print(f"  {t['date']:<12} {t['type']:<14} "
              f"{format_shares(t['shares']):>10} ${t['price']:>9.2f}")


def list_transactions_for_ticker(ticker, transactions=None):
    """
    Show the dated transaction history for one ticker.
    Separates data retrieval from display.

    State read: transactions (from file or passed in)
    Invariant: displays only transactions for the requested ticker
    """
    if transactions is None:
        transactions = load_json(TRANSACTIONS_FILE) or []

    ticker = ticker.upper()
    ticker_txns = get_transactions_for_ticker(ticker, transactions)

    if not ticker_txns:
        print(f"\nNo transactions found for {ticker}.")
        return

    print_transactions_header(ticker)
    print_transactions_table(ticker_txns)
    print(f"  {'=' * 56}")
    print(f"  Total transactions: {len(ticker_txns)}")


# ============================================================================
# HELPER: GROUP TRANSACTIONS BY DATE
# ============================================================================

def group_transactions_by_date(transactions):
    """
    Group transactions into a dict keyed by date.
    Returns {date_str: [list of transactions on that date]}
    """
    grouped = {}
    for t in transactions:
        d = t["date"]
        if d not in grouped:
            grouped[d] = []
        grouped[d].append(t)
    return grouped


# ============================================================================
# HELPER: SPLIT LOOKUP
# ============================================================================

def build_split_lookup():
    """
    Load splits CSV and return {date: {ticker: split_ratio}}.

    State read: SPLITS_FILE
    Invariant: each date+ticker pair maps to exactly one split ratio
    """
    rows = load_csv_rows(SPLITS_FILE)
    lookup = {}
    for row in rows:
        d = row["Date"]
        ticker = row["Ticker"]
        ratio = float(row["Split Ratio"])
        if d not in lookup:
            lookup[d] = {}
        lookup[d][ticker] = ratio
    return lookup


def apply_split(position_shares, split_ratio):
    """
    Apply a stock split to a position.
    Returns the new share count after the split.
    """
    return position_shares * split_ratio


def apply_transaction(current_shares, txn):
    """
    Apply a single buy or sell transaction to a position.
    Returns the updated share count.
    """
    if txn["type"] == "buy":
        return current_shares + txn["shares"]
    elif txn["type"] == "sell":
        return current_shares - txn["shares"]
    return current_shares


# ============================================================================
# 3. build_stocks_by_date(...)
# ============================================================================

def build_stocks_by_date():
    """
    Reconstruct stock positions for every market date from transaction history.
    This is the backbone of splits, positions, and later valuation.

    State read:
        transactions, mkt_dates, splits

    Transition logic:
        For each market date:
        1. Carry forward prior positions
        2. Apply splits for that date
        3. Apply stock transactions for that date
        4. Store snapshot

    Invariant:
        stocks_by_date[d] reflects cumulative positions through date d,
        with all splits applied on their effective dates.

    Returns:
        {date: {ticker: shares}} and saves to stocks_by_date.json
    """
    transactions = load_json(TRANSACTIONS_FILE) or []
    mkt_dates = load_json(MKT_DATES_FILE) or []
    split_lookup = build_split_lookup()

    # Only stock transactions (not cash)
    stock_txns = [t for t in transactions if t["ticker"] != "$$$$"]
    txns_by_date = group_transactions_by_date(stock_txns)

    stocks_by_date = {}
    positions = {}  # ticker -> shares (running state)

    for date in sorted(mkt_dates):
        # 1. Carry forward prior positions (already in 'positions' dict)

        # 2. Apply splits for this date
        if date in split_lookup:
            for ticker, ratio in split_lookup[date].items():
                if ticker in positions and positions[ticker] > 0:
                    positions[ticker] = apply_split(positions[ticker], ratio)

        # 3. Apply stock transactions for this date
        if date in txns_by_date:
            for txn in txns_by_date[date]:
                ticker = txn["ticker"]
                if ticker not in positions:
                    positions[ticker] = 0.0
                positions[ticker] = apply_transaction(positions[ticker], txn)

        # 4. Store snapshot (only non-zero positions)
        snapshot = {k: v for k, v in positions.items() if v > 0}
        if snapshot:
            stocks_by_date[date] = snapshot

    save_json(STOCKS_BY_DATE_FILE, stocks_by_date)
    print(f"Built stock positions for {len(stocks_by_date)} dates.")
    return stocks_by_date


# ============================================================================
# HELPER: DIVIDEND LOOKUP
# ============================================================================

def build_dividend_lookup():
    """
    Load dividends CSV and return {date: {ticker: dividend_per_share}}.

    State read: DIVIDENDS_FILE
    Invariant: each date+ticker pair maps to one dividend amount
    """
    rows = load_csv_rows(DIVIDENDS_FILE)
    lookup = {}
    for row in rows:
        d = row["Date"]
        ticker = row["Ticker"]
        div = float(row["Dividend"])
        if d not in lookup:
            lookup[d] = {}
        lookup[d][ticker] = div
    return lookup


# ============================================================================
# HELPER: DAILY CASH FLOW COMPUTATION
# ============================================================================

def get_transaction_cash_flow(txns_for_date):
    """
    Compute the net cash flow from transactions on a single date.

    Contributions add cash. Withdrawals subtract cash.
    Buys subtract cash (shares * price). Sells add cash (shares * price).

    Returns: float (net cash change)
    """
    flow = 0.0
    for t in txns_for_date:
        if t["ticker"] == "$$$$":
            if t["type"] == "contribution":
                flow += t["shares"] * t["price"]
            elif t["type"] == "withdrawal":
                flow -= t["shares"] * t["price"]
        elif t["type"] == "buy":
            flow -= t["shares"] * t["price"]
        elif t["type"] == "sell":
            flow += t["shares"] * t["price"]
    return flow


def get_dividend_cash_flow(date, positions, dividend_lookup):
    """
    Compute cash received from dividends on a given date,
    based on positions held on that date.

    Dividend cash = shares_held * dividend_per_share

    Returns: float (total dividend cash for the date)
    """
    if date not in dividend_lookup:
        return 0.0
    flow = 0.0
    for ticker, div_per_share in dividend_lookup[date].items():
        shares_held = positions.get(ticker, 0.0)
        if shares_held > 0:
            flow += shares_held * div_per_share
    return flow


# ============================================================================
# 4. build_cash_by_date(...)
# ============================================================================

def build_cash_by_date():
    """
    Reconstruct the cash balance for every market date.

    State read:
        transactions, mkt_dates, stocks_by_date, dividends

    Transition logic:
        For each market date:
            cash = prior_cash
            cash += transaction_cash_flow
            cash += dividend_cash_flow

    Invariant:
        cash_by_date[d] equals cumulative cash through date d,
        including all contributions, withdrawals, trades, and dividends.

    Returns:
        {date: cash_balance} and saves to cash_by_date.json
    """
    transactions = load_json(TRANSACTIONS_FILE) or []
    mkt_dates = load_json(MKT_DATES_FILE) or []
    stocks_by_date = load_json(STOCKS_BY_DATE_FILE)
    if stocks_by_date is None:
        print("stocks_by_date.json not found. Run build_stocks_by_date() first.")
        stocks_by_date = build_stocks_by_date()

    txns_by_date = group_transactions_by_date(transactions)
    dividend_lookup = build_dividend_lookup()

    cash_by_date = {}
    cash = 0.0

    for date in sorted(mkt_dates):
        # Transaction cash flow for this date
        day_txns = txns_by_date.get(date, [])
        cash += get_transaction_cash_flow(day_txns)

        # Dividend cash flow based on positions held
        positions = stocks_by_date.get(date, {})
        cash += get_dividend_cash_flow(date, positions, dividend_lookup)

        cash_by_date[date] = round(cash, 2)

    save_json(CASH_BY_DATE_FILE, cash_by_date)
    print(f"Built cash balances for {len(cash_by_date)} dates.")
    return cash_by_date


# ============================================================================
# 5. get_cash_by_date(...)
# ============================================================================

def print_cash(date, cash_value):
    """Format and print a single cash balance."""
    print(f"\n{'=' * 40}")
    print(f"  Cash balance as of {date}: ${cash_value:,.2f}")
    print(f"{'=' * 40}")


def get_cash_by_date(val_data=None):
    """
    User-facing reporting function for cash balance on a chosen date.
    Rebuilds cash fresh, then reads and displays.

    State read:
        transactions, mkt_dates, stocks_by_date, dividends

    Transitions:
        Rebuilds cash_by_date.json

    Invariant:
        Displayed cash equals cumulative cash through the requested date.
    """
    if val_data:
        date = get_valid_date(val_data)
    else:
        date = input("Enter date (YYYY-MM-DD): ").strip()

    if date is None:
        return

    # Rebuild fresh
    build_stocks_by_date()
    cash_by_date = build_cash_by_date()

    if date in cash_by_date:
        print_cash(date, cash_by_date[date])
    else:
        # Find the most recent date on or before the requested date
        available = [d for d in sorted(cash_by_date.keys()) if d <= date]
        if available:
            nearest = available[-1]
            print_cash(date, cash_by_date[nearest])
            print(f"  (Using nearest prior date: {nearest})")
        else:
            print(f"\nNo cash data available on or before {date}.")


# ============================================================================
# 6. get_portfolio_by_date(...)
# ============================================================================

def build_price_lookup_for_date(date, val_data):
    """
    Get a {ticker: price} dict for a given date from prices_dates.json.
    """
    if date not in val_data["prices"]:
        return {}
    return {rec["ticker"]: rec["raw_price"] for rec in val_data["prices"][date]}


def make_cash_portfolio_row(cash_value):
    """Create a portfolio row for the cash position."""
    return {
        "ticker": "$$$$",
        "shares": cash_value,
        "price": 1.00,
        "market_value": cash_value,
    }


def make_stock_portfolio_rows(positions, price_lookup):
    """
    Enrich stock positions with market prices to create portfolio rows.
    Returns a list of dicts with ticker, shares, price, market_value.
    """
    rows = []
    for ticker in sorted(positions.keys()):
        shares = positions[ticker]
        price = price_lookup.get(ticker, 0.0)
        rows.append({
            "ticker": ticker,
            "shares": shares,
            "price": price,
            "market_value": shares * price,
        })
    return rows


def print_portfolio_table(date, cash_row, stock_rows):
    """Print a formatted portfolio table."""
    print(f"\n{'=' * 65}")
    print(f"  Portfolio as of {date}")
    print(f"{'=' * 65}")
    print(f"  {'Ticker':<8} {'Shares':>12} {'Price':>12} {'Market Value':>14}")
    print(f"  {'-' * 8} {'-' * 12} {'-' * 12} {'-' * 14}")

    # Cash row
    print(f"  {'$$$$':<8} {'':>12} {'$1.00':>12} ${cash_row['market_value']:>13,.2f}")

    # Stock rows
    total = cash_row["market_value"]
    for row in stock_rows:
        print(f"  {row['ticker']:<8} {format_shares(row['shares']):>12} "
              f"${row['price']:>11.2f} ${row['market_value']:>13,.2f}")
        total += row["market_value"]

    print(f"  {'-' * 8} {'-' * 12} {'-' * 12} {'-' * 14}")
    print(f"  {'TOTAL':<8} {'':>12} {'':>12} ${total:>13,.2f}")
    print(f"{'=' * 65}")

    return total


def save_portfolio_for_date(date, cash_row, stock_rows, total):
    """Save portfolio snapshot to a JSON file for the given date."""
    portfolio = {
        "date": date,
        "total_value": total,
        "cash": cash_row,
        "positions": stock_rows,
    }
    out_file = POSITIONS_DIR / f"portfolio_{date}.json"
    save_json(out_file, portfolio)
    print(f"  Portfolio saved to {out_file}")


def get_portfolio_by_date(val_data=None):
    """
    Final composition layer: assembles and displays the full portfolio
    for a chosen date.

    State read:
        transactions, mkt_dates, prices_dates, stocks_by_date, cash_by_date

    Transitions:
        Rebuilds stocks and cash, then assembles portfolio

    Invariant:
        Portfolio shows all positions and cash as of the requested date,
        valued at market prices for that date.
    """
    if val_data:
        date = get_valid_date(val_data)
    else:
        date = input("Enter date (YYYY-MM-DD): ").strip()

    if date is None:
        return

    if val_data is None:
        val_data = load_validation_data()

    # Rebuild everything fresh
    stocks_by_date = build_stocks_by_date()
    cash_by_date = build_cash_by_date()

    # Get positions and cash for date
    positions = stocks_by_date.get(date, {})
    cash_value = cash_by_date.get(date, 0.0)

    # If exact date not found, use nearest prior
    if date not in cash_by_date:
        available = [d for d in sorted(cash_by_date.keys()) if d <= date]
        if available:
            nearest = available[-1]
            positions = stocks_by_date.get(nearest, {})
            cash_value = cash_by_date.get(nearest, 0.0)
            print(f"  (Using nearest prior date: {nearest})")

    # Build display
    price_lookup = build_price_lookup_for_date(date, val_data)
    cash_row = make_cash_portfolio_row(cash_value)
    stock_rows = make_stock_portfolio_rows(positions, price_lookup)

    total = print_portfolio_table(date, cash_row, stock_rows)
    save_portfolio_for_date(date, cash_row, stock_rows, total)


# ============================================================================
# E. VERIFICATION HELPERS
# ============================================================================

def print_ticker_path(ticker, start_date=None, end_date=None):
    """
    Trace one ticker's position across dates for debugging.
    Shows how splits and transactions change the share count.

    State read: stocks_by_date
    """
    stocks_by_date = load_json(STOCKS_BY_DATE_FILE)
    if stocks_by_date is None:
        print("Run build_stocks_by_date() first.")
        return

    ticker = ticker.upper()
    print(f"\n{'=' * 50}")
    print(f"  Position path for {ticker}")
    print(f"{'=' * 50}")
    print(f"  {'Date':<12} {'Shares':>12}")
    print(f"  {'-' * 12} {'-' * 12}")

    for date in sorted(stocks_by_date.keys()):
        if start_date and date < start_date:
            continue
        if end_date and date > end_date:
            break
        positions = stocks_by_date[date]
        if ticker in positions:
            print(f"  {date:<12} {format_shares(positions[ticker]):>12}")

    print(f"  {'=' * 26}")


def check_portfolio_date(date, val_data=None):
    """
    Quick verification of portfolio state on a specific date.
    Shows positions, cash, and total without full rebuild.

    State read: stocks_by_date, cash_by_date
    """
    stocks_by_date = load_json(STOCKS_BY_DATE_FILE)
    cash_by_date = load_json(CASH_BY_DATE_FILE)

    if stocks_by_date is None or cash_by_date is None:
        print("Run build_stocks_by_date() and build_cash_by_date() first.")
        return

    positions = stocks_by_date.get(date, {})
    cash = cash_by_date.get(date, 0.0)

    print(f"\n  Quick check for {date}:")
    print(f"  Cash: ${cash:,.2f}")
    print(f"  Positions: {len(positions)} tickers")
    for t in sorted(positions.keys()):
        print(f"    {t}: {format_shares(positions[t])} shares")


# ============================================================================
# MAIN TRANSACTION ENTRY SESSION
# ============================================================================

def transaction_entry_session():
    """
    Main interactive workflow:
    - Load validation data and prior transactions
    - Set a working date (validated)
    - Enter multiple transactions for that date
    - Save after each transaction
    - Access all six major functions from the menu
    """
    val_data = load_validation_data()
    if not val_data["prices"]:
        print("\nWARNING: Running without price validation!")

    transactions = load_json(TRANSACTIONS_FILE) or []
    print(f"\nLoaded {len(transactions)} existing transaction(s).")

    current_date = get_valid_date(val_data)
    if current_date is None:
        print("Exiting.")
        return

    while True:
        print(f"\n{'=' * 55}")
        print("  TRANSACTION MENU")
        print(f"{'=' * 55}")
        print(f"  Working Date: {current_date}")
        print()
        print("  1.  Add transaction")
        print("  2.  Change working date")
        print("  3.  Show all transactions")
        print("  4.  Show ticker history")
        print("  ─── Build & Report ───")
        print("  5.  Build stock positions (all dates)")
        print("  6.  Build cash balances (all dates)")
        print("  7.  Get cash balance for a date")
        print("  8.  Get full portfolio for a date")
        print("  ─── Debug ───")
        print("  9.  Trace ticker position path")
        print("  10. Quick portfolio check")
        print("  ─── Exit ───")
        print("  0.  Save and exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            txn = create_transaction(current_date, val_data, transactions)
            if txn:
                transactions.append(txn)
                # Sort by date then record_number after each append
                transactions.sort(key=lambda t: (t["date"], t.get("record_number", 0)))
                save_json(TRANSACTIONS_FILE, transactions)
                print(f"\n  Transaction #{txn['record_number']} added and saved.")
                print(f"  {txn}")

        elif choice == "2":
            new_date = get_valid_date(val_data)
            if new_date:
                current_date = new_date
                print(f"\n  Working date changed to {current_date}")

        elif choice == "3":
            if not transactions:
                print("\n  No transactions recorded.")
            else:
                print(f"\n  All Transactions ({len(transactions)} total):")
                for i, t in enumerate(transactions, 1):
                    print(f"    {i:>4}. [{t['date']}] {t['type']:<14} "
                          f"{t['ticker']:<6} {format_shares(t['shares']):>8} "
                          f"@ ${t['price']:.2f}")

        elif choice == "4":
            ticker = input("Enter ticker: ").strip()
            list_transactions_for_ticker(ticker, transactions)

        elif choice == "5":
            build_stocks_by_date()

        elif choice == "6":
            build_cash_by_date()

        elif choice == "7":
            get_cash_by_date(val_data)

        elif choice == "8":
            get_portfolio_by_date(val_data)

        elif choice == "9":
            ticker = input("Enter ticker: ").strip()
            start = input("Start date (or Enter for all): ").strip() or None
            end = input("End date (or Enter for all): ").strip() or None
            print_ticker_path(ticker, start, end)

        elif choice == "10":
            date = input("Enter date (YYYY-MM-DD): ").strip()
            check_portfolio_date(date, val_data)

        elif choice == "0":
            save_json(TRANSACTIONS_FILE, transactions)
            print("\n  Transactions saved. Exiting.")
            break

        else:
            print("\n  Invalid choice.")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print(f"\n{'=' * 55}")
    print("  PORTFOLIO TRANSACTION ENTRY SYSTEM (Enhanced)")
    print(f"{'=' * 55}")
    transaction_entry_session()
