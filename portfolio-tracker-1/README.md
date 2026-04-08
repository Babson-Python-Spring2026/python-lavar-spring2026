# Portfolio Tracker

This project is a portfolio tracker that processes raw portfolio prices and calculates stock splits. It outputs the results in a JSON format for easy access and analysis.

## Project Structure

```
portfolio-tracker
├── src
│   ├── main.py               # Entry point of the application
│   ├── portfolio_processor.py  # Processes portfolio prices and splits
│   └── data_handler.py       # Handles data reading and writing
├── data
│   ├── raw_prices.csv        # Raw portfolio prices data
│   └── splits.csv            # Stock splits data
├── output
│   └── results.json          # Output file for processed results
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
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

To run the portfolio tracker, execute the following command:
```
python src/main.py
```

This will process the raw prices and splits, and output the results to `output/results.json`.

## Dependencies

This project requires the following Python packages:
- pandas

Make sure to install all dependencies listed in `requirements.txt` before running the application.

## Contributing

Feel free to submit issues or pull requests if you have suggestions or improvements for the project.