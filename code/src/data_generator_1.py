import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Parameters
start_date = datetime(2024, 1, 1)  # Start of the year
days = 365  # Daily reconciliation for a year

# Sample data components
trade_ids = [f'{random.randint(1000000, 9999999)}' for _ in range(200)]
desks = ['RMDS-Agency OMIs', 'RMDS-Corp Bonds', 'RMDS-Govt Bonds']
buy_sell = ['B', 'S']
prices = np.round(np.random.uniform(10, 100, 200), 2)
quantity_tolerance = 1
price_tolerance = 0.01
comments = [
    '[{Factor rounding is causing minor delta in quantity}]',
    '[{Manual adjustment pending validation}]',
    '[{Discrepancy identified, awaiting action}]',
    '[{Data source issue, reconciliation in progress}]',
    '[{Valid trade, discrepancy within tolerance}]'
]

# Historical Data Generation
history_data = []
for day in range(days):
    recon_date = start_date + timedelta(days=day)
    for _ in range(20):  # Simulate 20 transactions per day
        trade_id = random.choice(trade_ids)
        desk = random.choice(desks)
        buy_or_sell = random.choice(buy_sell)

        # Generate trade and settle dates
        trade_date = recon_date - timedelta(days=random.randint(1, 5))
        settle_date = trade_date + timedelta(days=2)

        # Generate prices and quantities with controlled differences
        original_price = random.choice(prices)
        impact_price = original_price + random.uniform(-0.05, 0.05)
        original_quantity = random.randint(1000, 50000)
        impact_quantity = original_quantity + random.randint(-3, 3)

        # Calculate differences
        price_diff = abs(original_price - impact_price)
        quantity_diff = abs(original_quantity - impact_quantity)

        # Determine match status and anomaly
        if price_diff <= price_tolerance and quantity_diff <= quantity_tolerance:
            match_status = 'Match'
            comment = '[{Valid trade, discrepancy within tolerance}]'
            anomaly_status = 'No'
        elif price_diff > price_tolerance and quantity_diff > quantity_tolerance:
            match_status = 'Quantity & Price Break'
            comment = random.choice(comments)
            anomaly_status = 'Yes' if random.random() < 0.4 else 'No'
        elif price_diff > price_tolerance:
            match_status = 'Price Break'
            comment = '[{Price discrepancy beyond tolerance}]'
            anomaly_status = 'Yes' if random.random() < 0.4 else 'No'
        elif quantity_diff > quantity_tolerance:
            match_status = 'Quantity Break'
            comment = '[{Quantity discrepancy beyond tolerance}]'
            anomaly_status = 'Yes' if random.random() < 0.4 else 'No'
        else:
            match_status = 'Impact Only'
            comment = '[{Impact data available without source}]'
            anomaly_status = 'No'

        history_data.append([
            match_status, recon_date.strftime('%m/%d/%Y'), comment, quantity_diff, trade_id,
            desk, recon_date.strftime('%m/%d/%Y'), buy_or_sell, trade_date.strftime('%m/%d/%Y'),
            settle_date.strftime('%m/%d/%Y'), original_quantity, original_price, impact_price,
            price_tolerance, impact_quantity, quantity_tolerance, anomaly_status
        ])

# Create historical data file
history_columns = ['MatchStatus', 'ReconDate', 'Comment', 'QuantityDifference', 'TradeID',
                   'DeskName', 'ReconDate', 'Buy_Sell', 'Trade_Date', 'Settle_Date',
                   'Original_Quantity', 'Original_Price', 'Impact_Price', 'Price_Tolerance',
                   'Impact_Quantity', 'Quantity_Tolerance', 'Anomaly']
df_history = pd.DataFrame(history_data, columns=history_columns)
df_history.to_csv('catalyst_daily_reconciliation_new1.csv', index=False)

print("Catalyst daily reconciliation data saved to 'catalyst_daily_reconciliation_new1.csv'.")
