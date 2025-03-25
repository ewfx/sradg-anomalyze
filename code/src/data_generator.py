import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Parameters
start_date = datetime(2024, 1, 31)  # Start of the year
months = 12

# Expanded sample data components
companies = ['0000', '0002', '0003', '0004']
accounts = ['1609102', '1678920', '1988882', '1728391', '1628374']
currencies = ['USD', 'EUR', 'GBP']
primary_accounts = ['ALL OTHER LOANS', 'PERSONAL LOANS']
secondary_accounts = ['DEFERRED COSTS', 'DEFERRED ORIGINATION FEES', 'PRINCIPAL']
comments = ['Validated by reconciler', 'Pending investigation', 'Data source error', 'Currency conversion issue', 'Out of tolerance range']

# Historical Data Generation
history_data = []
for month in range(months):
    as_of_date = start_date + timedelta(days=month * 30)  # Approximate month-end
    for _ in range(50):
        company = random.choice(companies)
        account = random.choice(accounts)
        au_code = random.randint(1000, 9999)
        currency = random.choice(currencies)
        primary_acc = random.choice(primary_accounts)
        secondary_acc = random.choice(secondary_accounts)

        # Generate balances with more controlled variations
        gl_balance = random.randint(10000, 100000)
        ihub_balance = gl_balance + random.randint(-50000, 50000)

        # Control match/break ratio
        if random.random() < 0.5:
            ihub_balance = gl_balance

        balance_diff = gl_balance - ihub_balance

        match_status = 'Break' if balance_diff != 0 else 'Match'
        comment = random.choice(comments) if match_status == 'Break' else 'Validated by reconciler'

        history_data.append([
            as_of_date.strftime('%m/%d/%Y'), company, account, au_code, currency,
            primary_acc, secondary_acc, gl_balance, ihub_balance, balance_diff,
            match_status, comment
        ])

# Create historical data file
history_columns = ['As of Date', 'Company', 'Account', 'AU', 'Currency',
                   'Primary Account', 'Secondary Account', 'GL Balance',
                   'iHub Balance', 'Balance Difference', 'Match Status', 'Comment']
df_history = pd.DataFrame(history_data, columns=history_columns)
df_history.to_csv('historical_reconciliation_data.csv', index=False)

# Current Monthly Recon File (last month)
current_month_data = history_data[-50:]  # Last month data
pattern_breaks = {(row[1], row[2]): 0 for row in history_data[:-50]}  # Check historical data for patterns

for row in current_month_data:
    key = (row[1], row[2])
    if row[10] == 'Break':
        pattern_breaks[key] += 1
    anomaly_status = 'Not an Anomaly' if pattern_breaks.get(key, 0) > 0 else 'Anomaly'
    row.append(anomaly_status)

# Add anomaly status to current data
current_columns = history_columns + ['Anomaly Status']
df_current = pd.DataFrame(current_month_data, columns=current_columns)
df_current.to_csv('current_reconciliation_data.csv', index=False)

print("Historical data saved to 'historical_reconciliation_data.csv'.")
print("Current recon data saved to 'current_reconciliation_data.csv'.")
