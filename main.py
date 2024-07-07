import pandas as pd
import logging
import requests
from bs4 import BeautifulSoup
from io import StringIO
import mysql.connector
import matplotlib.pyplot as plt

# Setup logging
def setup_logging():
    logging.basicConfig(filename='progress.log', level=logging.INFO, 
                        format='%(asctime)s:%(levelname)s:%(message)s')

setup_logging()
def log_message(message, level='info'):
    if level == 'info':
        logging.info(message)
    elif level == 'warning':
        logging.warning(message)
    elif level == 'error':
        logging.error(message)

def fetchAndSaveToFile(url, path):
    r = requests.get(url)
    with open(path, "w", encoding="utf-8") as f:
        f.write(r.text)

url = "https://web.archive.org/web/20230908091635/https:/en.wikipedia.org/wiki/List_of_largest_banks"
fetchAndSaveToFile(url, "dataFiles/info.html")

with open("dataFiles/info.html", "r", encoding="utf-8") as f:
    htmlDoc = f.read()

soup = BeautifulSoup(htmlDoc, "html.parser")
tables = soup.find_all('table', {'class': 'wikitable'})

def extract_content(url, child):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    tables = soup.find_all('table', {'class': 'wikitable'})
    
    if tables:
        first_table = tables[child]
        html_string = str(first_table)
        df = pd.read_html(StringIO(html_string))[0]
        log_message("First table extracted successfully")
        return df
    else:
        log_message("No tables found", "warning")
        return pd.DataFrame()
    
df = extract_content(url, 0)
# print(df)

def transform_data(bank_data, exchange_rate_file):
    exchange_rate_df = pd.read_csv(exchange_rate_file)
    
    print("Exchange Rate DataFrame (Initial Read):")
    print(exchange_rate_df)
    
  
    
    # Display bank DataFrame
    print("\nBank DataFrame:")
    print(bank_data)

    # Add columns for market cap in different currencies
    for _, row in exchange_rate_df.iterrows():
        currency = row['Currency']
        rate = row['Rate']
        column_name = f'Market cap ({currency} billion)'
        bank_data[column_name] = bank_data['Market cap (US$ billion)'] * rate

    print("\nTransformed DataFrame:")
    print(bank_data)
    log_message("The Scraped Data has been transformed")

    return bank_data

def create_visualizations(df):
    plt.figure(figsize=(10, 8))
    df.sort_values(by='Market cap (INR billion)', ascending=False, inplace=True)
    plt.barh(df['Bank name'], df['Market cap (INR billion)'], color='skyblue')
    plt.xlabel('Market cap (INR billion)')
    plt.ylabel('Bank name')
    plt.title('Market Cap of Largest Banks in INR')
    plt.tight_layout()
    plt.savefig("dataFiles/market_cap_inr.png")
    plt.show()

def load_to_database(df, db_config):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS largest_banks")
    
    cursor.execute("""
        CREATE TABLE largest_banks (
            Rank INT,
            Bank_name VARCHAR(255),
            Market_cap_USD_billion FLOAT,
            Market_cap_EUR_billion FLOAT,
            Market_cap_GBP_billion FLOAT,
            Market_cap_INR_billion FLOAT
        )
    """)
    
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO largest_banks (
                Rank, Bank_name, Market_cap_USD_billion,
                Market_cap_EUR_billion, Market_cap_GBP_billion, Market_cap_INR_billion
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            row['Rank'], row['Bank name'], row['Market cap (US$ billion)'],
            row.get('Market cap (EUR billion)', None), 
            row.get('Market cap (GBP billion)', None), 
            row.get('Market cap (INR billion)', None)
        ))
    
    conn.commit()
    log_message("Data loaded into database successfully")
    cursor.close()
    conn.close()

db_config = {
    'user': 'u481156254_hamzakhan',
    'password': 'RvFINj7?',
    'host': '156.67.73.151',
    'database': 'u481156254_BankData'
}


exchange_rate_file = 'dataFiles/exchange_rate.csv'

transformed_data = transform_data(df, exchange_rate_file)
load_to_database(transformed_data, db_config)
transformed_data.to_csv("dataFiles/transformed_data.csv", index=False)
create_visualizations(transformed_data)
print("\nTransformed Data:")
print(transformed_data)
