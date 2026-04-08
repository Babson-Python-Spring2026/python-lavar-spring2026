class PortfolioTracker:
    def __init__(self, ticker, split_ratio):
        self.ticker = ticker
        self.split_ratio = split_ratio
        self.raw_data = []
        self.processed_data = []

    def load_data(self, file_path):
        import pandas as pd
        self.raw_data = pd.read_csv(file_path)

    def apply_split(self):
        for index, row in self.raw_data.iterrows():
            if row['Ticker'] == self.ticker:
                adjusted_price = row['Price'] / self.split_ratio
                self.processed_data.append({
                    'Date': row['Date'],
                    'Ticker': row['Ticker'],
                    'Adjusted Price': adjusted_price
                })

    def export_to_json(self, output_path):
        import json
        with open(output_path, 'w') as json_file:
            json.dump(self.processed_data, json_file)