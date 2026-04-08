class PortfolioProcessor:
    def __init__(self, data_handler):
        self.data_handler = data_handler
        self.prices = None
        self.splits = None

    def load_prices(self, file_path):
        self.prices = self.data_handler.read_csv(file_path)

    def process_prices(self):
        if self.prices is not None:
            # Example processing: Convert prices to float and handle missing values
            self.prices['Price'] = self.prices['Price'].astype(float).fillna(0)

    def calculate_splits(self, splits_file_path):
        self.splits = self.data_handler.read_csv(splits_file_path)
        # Example logic for calculating adjusted prices based on splits
        for index, row in self.splits.iterrows():
            split_ratio = row['Split Ratio']
            self.prices.loc[self.prices['Stock'] == row['Stock'], 'Price'] /= split_ratio

    def get_processed_data(self):
        return self.prices