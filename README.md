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
