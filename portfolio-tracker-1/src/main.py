# main.py

from portfolio_processor import PortfolioProcessor

def main():
    # Initialize the portfolio processor
    processor = PortfolioProcessor()

    # Load raw prices
    processor.load_prices('data/raw_prices.csv')

    # Process the prices
    processor.process_prices()

    # Calculate stock splits
    processor.calculate_splits('data/splits.csv')

    # Output results to JSON
    processor.output_results('output/results.json')

if __name__ == "__main__":
    main()