import hashlib
import hmac
import requests
import json
import csv
from datetime import datetime, timedelta
from tkinter import Tk, Button, Label, Entry, Text, messagebox
import logging

BASE_URL = "https://api.binance.com"

logging.basicConfig(filename="script.log", level=logging.ERROR)

def calculate_signature(query_string, secret_key):
    signature = hmac.new(secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    return signature

def list_user_order_history(api_key, secret_key, start_timestamp=None, end_timestamp=None, page=1):
    try:
        timestamp = int(datetime.now().timestamp() * 1000)
        query_string = f"timestamp={timestamp}&page={page}"
        if start_timestamp:
            query_string += f"&startTimestamp={start_timestamp}"
        if end_timestamp:
            query_string += f"&endTimestamp={end_timestamp}"

        signature = calculate_signature(query_string, secret_key)
        query_string += f"&signature={signature}"

        url = f"{BASE_URL}/sapi/v1/c2c/orderMatch/listUserOrderHistory?{query_string}"
        response = requests.get(url, headers={"X-MBX-APIKEY": api_key})
        response_data = response.json()

        return response_data
    except Exception as e:
        logging.error(f"API request failed: {e}")

def load_api_keys():
    try:
        with open("config.json") as config_file:
            config_data = json.load(config_file)
        api_key = config_data["api_key"]
        secret_key = config_data["secret_key"]
        return api_key, secret_key
    except Exception as e:
        logging.error(f"Error occurred during loading API keys: {e}")

def save_csv_file(data_array, path):
    try:
        with open(path, "w", newline="") as csv_file:
            fieldnames = ["orderNumber", "advNo", "tradeType", "asset", "fiat", "fiatSymbol",
                          "amount", "totalPrice", "unitPrice", "orderStatus", "createTime",
                          "commission", "counterPartNickName", "advertisementRole"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for order in data_array:
                writer.writerow(order)
    except Exception as e:
        logging.error(f"Error occurred during saving CSV file: {e}")

def execute_code():
    try:
        api_key, secret_key = load_api_keys()
        period = period_entry.get()

        if period == "":
            messagebox.showerror("Error", "Please enter the period of time.")
            return

        if period not in ["today", "yesterday", "last 7 days", "last 30 days"]:
            messagebox.showerror("Error", "Invalid period of time entered.")
            return

        start_timestamp, end_timestamp = calculate_timestamps(period)
        all_orders = []

        page = 1
        while True:
            response = list_user_order_history(api_key, secret_key, start_timestamp, end_timestamp, page)
            if response is None:
                messagebox.showerror("Error", "An error occurred while fetching trades. Please check the log file for details.")
                return

            orders = response.get("data", [])
            all_orders.extend(orders)

            if len(orders) < 100:
                break  # Reached the last page

            page += 1

        save_csv_file(all_orders, "order_history.csv")
        display_results(all_orders)
    except Exception as e:
        logging.error(f"An error occurred during execution: {e}")
        messagebox.showerror("Error", "An error occurred. Please check the log file for details.")

def display_results(data_array):
    try:
        totals = {}
        total_fiat = {"BUY": 0, "SELL": 0}

        for order in data_array:
            cryptocurrency = order['asset']
            trade_type = order['tradeType']
            order_status = order['orderStatus']

            if order_status in ['CANCELLED_BY_SYSTEM', 'CANCELLED']:
                continue

            if cryptocurrency not in totals:
                totals[cryptocurrency] = {"BUY": 0, "SELL": 0}

            if trade_type == 'BUY':
                totals[cryptocurrency]["BUY"] += float(order['amount'])
                total_fiat["BUY"] += float(order['totalPrice'])
            elif trade_type == 'SELL':
                totals[cryptocurrency]["SELL"] += float(order['amount'])
                total_fiat["SELL"] += float(order['totalPrice'])

        results_text.delete(1.0, "end")

        results = ""
        for cryptocurrency, trade_totals in totals.items():
            results += f"Total {cryptocurrency} (BUY): {trade_totals['BUY']} \n"
            results += f"Total {cryptocurrency} (SELL): {trade_totals['SELL']} \n"

        results += f"Total Fiat (BUY): {total_fiat['BUY']}\n"
        results += f"Total Fiat (SELL): {total_fiat['SELL']}\n"

        results_text.insert("end", results)
    except Exception as e:
        logging.error(f"An error occurred during displaying results: {e}")
        messagebox.showerror("Error", "An error occurred while displaying results. Please check the log file for details.")

def calculate_timestamps(period):
    now = datetime.now()
    if period == "today":
        start_timestamp = int(datetime(now.year, now.month, now.day).timestamp() * 1000)
        end_timestamp = int(now.timestamp() * 1000)
    elif period == "yesterday":
        yesterday = now - timedelta(days=1)
        start_timestamp = int(datetime(yesterday.year, yesterday.month, yesterday.day).timestamp() * 1000)
        end_timestamp = int(datetime(now.year, now.month, now.day).timestamp() * 1000)
    elif period == "last 7 days":
        start_timestamp = int((now - timedelta(days=7)).timestamp() * 1000)
        end_timestamp = int(now.timestamp() * 1000)
    elif period == "last 30 days":
        start_timestamp = int((now - timedelta(days=30)).timestamp() * 1000)
        end_timestamp = int(now.timestamp() * 1000)
    else:
        start_timestamp, end_timestamp = None, None

    return start_timestamp, end_timestamp

if __name__ == "__main__":
    root = Tk()
    root.title("Order History")
    root.geometry("400x400")

    period_label = Label(root, text="Enter the period of time: \n('today', 'yesterday', 'last 7 days', 'last 30 days')")
    period_label.pack()

    period_entry = Entry(root)
    period_entry.pack()

    execute_button = Button(root, text="Execute", command=execute_code)
    execute_button.pack()

    results_text = Text(root)
    results_text.pack()

    root.mainloop()
