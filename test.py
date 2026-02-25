import yfinance as yf
import matplotlib.pyplot as plt

ticker = "GOOG"

data = yf.download(ticker, period='1y')

print(data.head())

plt.figure(figsize=(12, 6))
plt.plot(data.index, data['Close'], label='GOOG Close Price', color='blue')

plt.title(f'{ticker} Stock Price - Last 1 Year', fontsize=16)
plt.xlabel('Date', fontsize=12)
plt.ylabel('Price (USD)', fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()