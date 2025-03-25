"""
Sean Adams 
10/04/2024

Schwab_API_Diagonal_Spread_Scanner:

This script is designed to loop through a list of stock tickers from the SEC's website,
compare the prices of two call option contracts far apart in expiration dates to be considered a diagonal spread,
and return the sorted ratios of these prices in an excel sheet.

The purpose is to get a list of the highest ratio of short-term call price to long-term call price
in order to sell a short-term call and buy a long term call to capture volatility and theta. This script is simply to scan
the stock market for high levels of short term volatility to sell a short-term OTM call and hedge by buying a long-term ITM call.

This kind of trading strategy lends itself to somewhat longer-term consistent profits, with short-term spikes of moderate losses, 
resulting in a strategy that is a less expensive method of buying a covered call, with potentially more limited potential for losses,
due to similar delta and a less expensive hedge with the long-term ITM call than one might have with stock in a covered call. 
However, short-term spikes in volatility of the underlying stock can increase losses due to the sold short-term OTM call
increasing in value faster than the price of the bought long-term ITM call.

"""

import requests
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta
from tqdm import tqdm

# Get today's date
today_date = datetime.today().strftime('%Y-%m-%d')

# Calculate the date 7 days in the future
one_week_date = (datetime.today() + timedelta(days=6)).strftime('%Y-%m-%d')

# Calculate the date 11 days in the future
one_week_date2 = (datetime.today() + timedelta(days=11)).strftime('%Y-%m-%d')

# Calculate the date 330 days in the future
one_year_date = (datetime.today() + timedelta(days=330)).strftime('%Y-%m-%d')

# Calculate the date 400 days in the future
one_year_date2 = (datetime.today() + timedelta(days=600)).strftime('%Y-%m-%d')

# Function to fetch all tickers from the SEC website
def fetch_all_tickers():
    tickers_url = 'https://www.sec.gov/include/ticker.txt'
    headers = {
        'User-Agent': 'Sample Company Name AdminContact@samplecompany.com',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.sec.gov'
    }
    response = requests.get(tickers_url, headers=headers)
    if response.status_code == 200:
        tickers = pd.read_csv(StringIO(response.text), delimiter='\t', header=None)
        tickers.columns = ['Ticker', 'CIK']
        return tickers['Ticker'].tolist()
    else:
        print("Failed to fetch data:", response.status_code)
        return []

headers = {
    'Authorization': 'Bearer I0.XXXXXXX',
    'Accept': 'application/json'
}

tickers = fetch_all_tickers()

# Limit the number of tickers
tickers = tickers[:3000]

# Initialize an empty DataFrame to store the results
results_df = pd.DataFrame(columns=['Ticker', 'Week_Last_Price', 'Year_Last_Price', 'Spread_Ratio'])

# Iterate through the tickers with a progress bar
for ticker in tqdm(tickers, desc="Processing tickers"):

    if not isinstance(ticker, str):
        continue  # Skip if the ticker is not a string

    ticker = ticker.upper()  # Convert the ticker to uppercase
    
    # Construct the URLs for the short-term and long-term data
    short_term_URL = f"https://api.schwabapi.com/marketdata/v1/chains?symbol={ticker}&contractType=CALL&strikeCount=1&fromDate={one_week_date}&toDate={one_week_date2}"
    long_term_URL = f"https://api.schwabapi.com/marketdata/v1/chains?symbol={ticker}&contractType=CALL&strikeCount=1&fromDate={one_year_date}&toDate={one_year_date2}"
    
    # Make the GET request for short-term data
    response = requests.get(url=short_term_URL, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
    else:
        print(f"Short-term request failed for {ticker} with status code {response.status_code}")
        continue
    
    # Extract the week_last_price
    week_last_price = None
    call_exp_date_map = response_data.get("callExpDateMap", {})
    for exp_date_key, strikes in call_exp_date_map.items():
        for strike_key, options_list in strikes.items():
            for option in options_list:
                if "last" in option:
                    week_last_price = option["last"]
                    break
        if week_last_price is not None:
            break
    
    # Make the GET request for long-term data
    response = requests.get(url=long_term_URL, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
    else:
        print(f"Long-term request failed for {ticker} with status code {response.status_code}")
        continue
    
    # Extract the year_last_price
    year_last_price = None
    call_exp_date_map = response_data.get("callExpDateMap", {})
    for exp_date_key, strikes in call_exp_date_map.items():
        for strike_key, options_list in strikes.items():
            for option in options_list:
                if "last" in option:
                    year_last_price = option["last"]
                    break
        if year_last_price is not None:
            break
    
    # Calculate the spread ratio if both prices are available
    if week_last_price and year_last_price:
        spread_ratio = year_last_price / week_last_price
        # Create a DataFrame for the current ticker
        temp_df = pd.DataFrame([{
            'Ticker': ticker,
            'Week_Last_Price': week_last_price,
            'Year_Last_Price': year_last_price,
            'Spread_Ratio': spread_ratio
        }])
        # Concatenate the current row to the results DataFrame
        results_df = pd.concat([results_df, temp_df], ignore_index=True)
    else:
        print(f"Could not calculate spread ratio for {ticker} due to missing data")

# Sort the DataFrame by spread ratio in descending order
sorted_results_df = results_df.sort_values(by='Spread_Ratio', ascending=True)

print(sorted_results_df)

# Save the sorted DataFrame to a CSV file
sorted_results_df.to_csv('C:/My/Path/Here', index=False)

print("Data saved to sorted_spread_ratios.csv")
