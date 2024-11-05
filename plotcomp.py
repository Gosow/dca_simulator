import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
import logging

# Setup logging
logging.basicConfig(filename='dca_scenarios.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def load_data(gold_file: str, snp500_file: str) -> (pd.DataFrame, pd.DataFrame):
    """Load the CSV files and parse dates."""
    try:
        # Load the CSV files and immediately strip whitespace from columns
        gold_df = pd.read_csv(gold_file, sep=",")
        snp500_df = pd.read_csv(snp500_file, sep=",")

        # Strip whitespace from column names
        gold_df.columns = gold_df.columns.str.strip()
        snp500_df.columns = snp500_df.columns.str.strip()

        # Log the loaded DataFrame's columns and first few rows for inspection
        logging.info(f"Loaded gold_df with columns: {gold_df.columns.tolist()}")
        logging.info(f"First few rows of gold_df:\n{gold_df.head()}")

        logging.info(f"Loaded snp500_df with columns: {snp500_df.columns.tolist()}")
        logging.info(f"First few rows of snp500_df:\n{snp500_df.head()}")

    except Exception as e:
        logging.error(f"Error loading CSV files: {e}")
        raise

    return gold_df, snp500_df



def clean_data(gold_df: pd.DataFrame, snp500_df: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame):
    """Clean the data by removing duplicates and ensuring proper indexing."""

    # Check for the Date column
    date_column = 'Date'  # This should match the header in your CSV
    if date_column in gold_df.columns:
        gold_df = gold_df.drop_duplicates(subset=date_column)
        gold_df.set_index(date_column, inplace=True)
        # Ensure the index is datetime
        gold_df.index = pd.to_datetime(gold_df.index)
    else:
        logging.error(f"Column '{date_column}' not found in gold_df.")
        raise KeyError(f"Column '{date_column}' not found in gold_df.")

    if date_column in snp500_df.columns:
        snp500_df = snp500_df.drop_duplicates(subset=date_column)
        snp500_df.set_index(date_column, inplace=True)
        # Ensure the index is datetime
        snp500_df.index = pd.to_datetime(snp500_df.index)
    else:
        logging.error(f"Column '{date_column}' not found in snp500_df.")
        raise KeyError(f"Column '{date_column}' not found in snp500_df.")

    return gold_df, snp500_df


def get_starting_date(gold_df: pd.DataFrame, snp500_df: pd.DataFrame) -> pd.Timestamp:
    """Get a valid starting date from user input."""
    starting_year = int(input("Enter the starting year for the plots (YYYY): "))
    starting_month = int(input("Enter the starting month for the plots (1-12): "))
    starting_date = pd.to_datetime(f"{starting_year}-{starting_month:02d}-01")

    # Check and adjust the starting date for both DataFrames
    for df, name in zip([gold_df, snp500_df], ["gold_df", "snp500_df"]):
        if starting_date not in df.index:
            logging.warning(f"Starting date {starting_date} not found in {name}. Adjusting to the next available date.")
            next_available_date = df.index[df.index > starting_date]
            if not next_available_date.empty:
                starting_date = next_available_date.min()
            else:
                logging.error(f"No available dates in {name} after the specified starting date.")
                raise ValueError(f"No available dates in {name} after the specified starting date.")

    logging.info(f"Using starting date: {starting_date}")
    return starting_date


def filter_data(gold_df: pd.DataFrame, snp500_df: pd.DataFrame, starting_date: pd.Timestamp) -> (pd.DataFrame, pd.DataFrame):
    """Filter the DataFrames to the relevant date range."""
    gold_df = gold_df.loc[starting_date:]
    snp500_df = snp500_df.loc[starting_date:]

    # Ensure both datasets cover the same date range
    start_date = max(gold_df.index.min(), snp500_df.index.min())
    end_date = min(gold_df.index.max(), snp500_df.index.max())
    logging.info(f"Filtered date range: {start_date} to {end_date}")

    return gold_df.loc[start_date:end_date], snp500_df.loc[start_date:end_date]


def resample_data(gold_df: pd.DataFrame, snp500_df: pd.DataFrame) -> (pd.DataFrame, pd.Series):
    """Resample data to monthly averages."""
    gold_monthly = gold_df.resample('ME').mean()
    snp500_monthly = snp500_df['SP500'].resample('ME').mean()
    return gold_monthly, snp500_monthly


def calculate_dca(gold_monthly: pd.DataFrame, snp500_monthly: pd.Series, total_invest: float, gold_percentage: float, snp_percentage: float, start_date: pd.Timestamp, rebalance_frequency: str = None) -> pd.Series:
    """Calculate the DCA values over time."""
    gold_monthly = gold_monthly.loc[start_date:]
    snp500_monthly = snp500_monthly.loc[start_date:]

    total_gold_value = 0
    total_snp500_value = 0
    total_invested = 0
    total_portfolio_values = []

    # Track the number of shares
    gold_shares = 0
    snp500_shares = 0

    # Create a list to track cumulative investments over time
    cumulative_invested = []

    for date in gold_monthly.index:
        if date in gold_monthly.index and date in snp500_monthly.index:
            gold_invest = total_invest * (gold_percentage / 100)
            snp_invest = total_invest * (snp_percentage / 100)

            # Buy shares if the prices are above zero
            if gold_monthly.loc[date]['Price'] > 0:
                gold_shares += gold_invest / gold_monthly.loc[date]['Price']
            if snp500_monthly.loc[date] > 0:
                snp500_shares += snp_invest / snp500_monthly.loc[date]

            # Calculate the current total values based on the number of shares
            total_gold_value = gold_shares * gold_monthly.loc[date]['Price']
            total_snp500_value = snp500_shares * snp500_monthly.loc[date]
            total_invested += total_invest

            # Update cumulative investment list
            cumulative_invested.append(total_invested)

            # Calculate total portfolio value
            total_portfolio_value = total_gold_value + total_snp500_value
            total_portfolio_values.append(total_portfolio_value)

            logging.info(f"Date: {date}, Total Gold Value: {total_gold_value:.2f}, "
                         f"Total S&P Value: {total_snp500_value:.2f}, "
                         f"Total Invested: ${total_invested:.2f}, "
                         f"Total Capitalization: ${total_portfolio_value:.2f}")

    total_portfolio_value_series = pd.Series(total_portfolio_values, index=gold_monthly.index[:len(total_portfolio_values)])
    cumulative_invested_series = pd.Series(cumulative_invested, index=gold_monthly.index[:len(cumulative_invested)])

    if rebalance_frequency:
        rebalance_period = {'monthly': 'M', 'quarterly': 'Q', 'semiannually': '2Q', 'annually': 'A'}
        rebalance_freq = rebalance_period.get(rebalance_frequency)
        total_portfolio_value_series = total_portfolio_value_series.resample(rebalance_freq).last()
        cumulative_invested_series = cumulative_invested_series.resample(rebalance_freq).last()

    logging.info(f"DCA Scenario: Total Invested = ${total_invest}, Gold Allocation = {gold_percentage}%, "
                 f"S&P Allocation = {snp_percentage}%, Total Portfolio Value = {total_portfolio_value_series.iloc[-1]:.2f}")

    return total_portfolio_value_series, cumulative_invested_series

def collect_dca_scenarios(num_scenarios: int, gold_monthly: pd.DataFrame, snp500_monthly: pd.Series) -> list:
    """Collect DCA scenarios from user input."""
    dca_scenarios = []
    for i in range(num_scenarios):
        total_invest = float(input("Total amount to invest each month: "))
        gold_percentage = float(input("Percentage allocation to Gold (e.g., 50 for 50%): "))
        snp_percentage = 100 - gold_percentage

        rebalance = input("Do you want to enable rebalancing? (yes/no): ").strip().lower()
        rebalance_frequency = None
        if rebalance == 'yes':
            rebalance_frequency = input("Choose rebalancing frequency (monthly, quarterly, semiannually, annually): ").strip().lower()

        dca_scenario_values, cumulative_invested_series = calculate_dca(gold_monthly, snp500_monthly, total_invest, gold_percentage, snp_percentage, gold_monthly.index[0], rebalance_frequency)
        dca_scenarios.append((dca_scenario_values, cumulative_invested_series, f"DCA Scenario {i + 1}: Total ${total_invest} invested monthly, Gold: {gold_percentage}%, S&P: {snp_percentage}%, Rebalance: {rebalance_frequency}"))
    return dca_scenarios


def plot_data(gold_monthly: pd.DataFrame, snp500_monthly: pd.Series, dca_scenarios: list):
    """Plot the DCA scenarios along with gold and S&P 500 prices."""
    plt.figure(figsize=(14, 7))

    # Plot Gold Price
    gold_line, = plt.plot(gold_monthly.index, gold_monthly['Price'], label="Gold Price", color='gold')

    # Plot S&P 500 Price
    sp500_line, = plt.plot(snp500_monthly.index, snp500_monthly, label="S&P 500 Price", color='blue')

    # Plot each DCA scenario
    for dca_scenario, cumulative_invested, label in dca_scenarios:
        total_portfolio_value = dca_scenario
        dca_line, = plt.plot(total_portfolio_value.index, total_portfolio_value, label=f"{label} - Total Valuation", color='orange')

        # Plot the cumulative invested amount over time
        plt.plot(cumulative_invested.index, cumulative_invested, label=f"{label} - Total Invested", linestyle='--', color='blue')

    # Set title and labels
    plt.title("Monthly Average Price of Gold and S&P 500 with Custom DCA Scenarios")
    plt.xlabel("Date")
    plt.ylabel("Value (in USD)")

    # Set y-axis to logarithmic scale
    plt.yscale('log')

    # Add legend and grid
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()

    # Enable hover tooltips
    add_hover_tooltips(gold_monthly, snp500_monthly, dca_scenarios, gold_line, sp500_line)

    # Show the plot
    plt.show()


def add_hover_tooltips(gold_monthly, snp500_monthly, dca_scenarios, gold_line, sp500_line):
    """Enable hover tooltips for DCA scenarios."""
    cursor = mplcursors.cursor(hover=True)

    # Hover tooltips for Gold Price
    cursor.connect("add", lambda sel: sel.annotation.set_text(
        f"Gold Price: ${gold_monthly['Price'].iloc[int(sel.target[0])]:,.2f} \nDate: {gold_monthly.index[int(sel.target[0])].date()}"
    ) if int(sel.target[0]) < len(gold_monthly) else "Out of bounds")

    # Hover tooltips for S&P 500 Price
    cursor.connect("add", lambda sel: sel.annotation.set_text(
        f"S&P 500 Price: ${snp500_monthly.iloc[int(sel.target[0])]:,.2f} \nDate: {snp500_monthly.index[int(sel.target[0])].date()}"
    ) if int(sel.target[0]) < len(snp500_monthly) else "Out of bounds")

    # Hover tooltips for DCA scenarios
    for dca_scenario, _, label in dca_scenarios:
        cursor.connect("add", lambda sel, dca_line=dca_scenario: sel.annotation.set_text(
            f"{label}\nTotal Value: ${dca_line.iloc[int(sel.target[0])]:,.2f} \nDate: {dca_line.index[int(sel.target[0])].date()}"
        ) if int(sel.target[0]) < len(dca_line) else "Out of bounds")



def main():
    # Load and clean data
    gold_df, snp500_df = load_data("cleaning/updated_monthly.csv", "cleaning/updated_data.csv")
    gold_df, snp500_df = clean_data(gold_df, snp500_df)

    # Get valid starting date and filter data
    starting_date = get_starting_date(gold_df, snp500_df)
    gold_df, snp500_df = filter_data(gold_df, snp500_df, starting_date)

    # Resample data
    gold_monthly, snp500_monthly = resample_data(gold_df, snp500_df)

    # Collect DCA scenarios from user input
    num_scenarios = int(input("Enter the number of DCA scenarios: "))
    dca_scenarios = collect_dca_scenarios(num_scenarios, gold_monthly, snp500_monthly)

    # Plot data
    plot_data(gold_monthly, snp500_monthly, dca_scenarios)

    # Enable hover tooltips
    add_hover_tooltips(dca_scenarios)


if __name__ == "__main__":
    main()
