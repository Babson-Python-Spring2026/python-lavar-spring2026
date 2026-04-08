# Portfolio Tracker

## Overview
The Portfolio Tracker project is designed to track portfolio splits from raw portfolio prices and splits data. It specifically focuses on the NFLX ticker with a 10.0 split ratio. The project processes the splits data and outputs the results in JSON format.

## Project Structure
```
portfolio-tracker
├── src
│   ├── portfolio_tracker.py   # Main logic for tracking portfolio splits
│   └── data
│       └── portfolio_splits.csv # Raw portfolio splits data
├── output
│   └── portfolio_splits.json   # Processed portfolio splits data in JSON format
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation
```

## Setup Instructions
1. Clone the repository:
   ```
   git clone <repository-url>
   cd portfolio-tracker
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
1. Ensure that the `portfolio_splits.csv` file is populated with the necessary splits data.
2. Run the `portfolio_tracker.py` script to process the splits:
   ```
   python src/portfolio_tracker.py
   ```

3. The processed data will be saved in `output/portfolio_splits.json`.

## Functionality
- The `PortfolioTracker` class reads raw portfolio prices and splits data.
- It applies the split ratios to the relevant ticker symbols.
- The processed data is exported to a JSON file for easy access and further analysis.

## License
This project is licensed under the MIT License.