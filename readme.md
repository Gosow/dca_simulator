Data Filling and Plotting Analysis
This repository contains two main scripts for handling financial time series data. The first script fills missing date entries in the dataset using interpolation, while the second script analyzes and visualizes the performance of investment scenarios in Gold and S&P 500.

Table of Contents
Installation
Usage
Data Filling and Interpolation
Plotting and Investment Scenario Analysis
Code Explanation
Contributing
License
Installation
Clone this repository:

bash
Copy code
git clone https://github.com/yourusername/repo-name.git
cd repo-name
Install the required libraries:

bash
Copy code
pip install pandas matplotlib mplcursors
Usage
Data Filling and Interpolation
To fill missing timestamps in your dataset and replace them with interpolated values, run the following command:

bash
Copy code
python interpolation_filling.py
Ensure that the CSV file containing your financial data is located in the same directory and is named data.csv.

Plotting and Investment Scenario Analysis
To run the investment analysis and visualize the results, execute:

bash
Copy code
python plotter.py
Data Filling and Interpolation
The interpolation_filling.py script processes a CSV file containing time series data, checks for missing dates, and fills them using interpolation.

Features:
Identifies gaps in the date column.
Interpolates missing values for all columns based on surrounding data.
Outputs a cleaned dataset to a new CSV file.
Plotting and Investment Scenario Analysis
The plotter.py script analyzes investment scenarios involving Gold and S&P 500 by calculating Dollar-Cost Averaging (DCA) values over specified periods.

Features:
Allows users to define investment amounts and rebalancing preferences.
Visualizes the performance of different investment scenarios on a plot.
Displays average prices and portfolio values over time.
Code Explanation
Interpolation Filling Script (interpolation_filling.py)
Import Libraries: The script begins by importing necessary libraries such as pandas for data manipulation.

Function Definition: The fill_missing_dates_with_interpolation function is defined to handle the data filling process.

Read CSV: The function reads the dataset from a specified file path.
Convert Date Column: Converts the 'Date' column to a datetime format.
Set Date as Index: Sets the date column as the index for easier manipulation.
Generate Complete Date Range: Creates a complete date range from the minimum to maximum dates in the dataset.
Reindex the DataFrame: Reindexes the DataFrame to include all dates, introducing NaN for missing dates.
Fill Missing Values: Fills missing values using interpolation, which estimates values based on available data.
Output the Updated Data: Saves the updated DataFrame to a new CSV file.
Plotter Script (plotter.py)
Import Libraries: Similar to the first script, necessary libraries are imported.

Load Data: The script loads Gold and S&P 500 price data from CSV files.

User Input for Investment Scenarios:

Asks the user for the amount to invest monthly and percentage allocation between Gold and S&P 500.
Determines whether to enable rebalancing and how frequently to do it.
DCA Calculation:

The calculate_dca function is defined to compute the investment value over time.
Based on user input, it calculates how many shares can be bought with the investment amount and tracks the total value of investments.
Rebalancing Logic:

If rebalancing is enabled, the portfolio is adjusted periodically to maintain the specified asset allocation.
Portfolio values are recalculated based on these weights.
Plotting:

The script plots the price movements of Gold and S&P 500 along with DCA scenario values.
An interactive cursor is added to display values on hover.
Contributing
Contributions to improve this project are welcome! Please feel free to open an issue or submit a pull request.

License
This project is licensed under the MIT License. See the LICENSE file for details.

