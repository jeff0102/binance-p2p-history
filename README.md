# Binance P2P History

Binance P2P History is a Python script that enables you to fetch your p2p order history from Binance and export it as a CSV file. It provides a user-friendly graphical interface where you can specify the time period for which you want to retrieve the order history.

## Installation

1. Clone the repository to your local machine.

2. (Optional) Set up a virtual environment to keep dependencies isolated:

3. Install the required packages using pip:

```bash
pip install -r requirements.txt 
```

## Usage

Before running the script, make sure you have your Binance API key and secret key available.

Paste your API key and secret key in the `config.json` file located in the project directory (remember to give read permission only to protect your assets):

```json
{

"api_key": "your-api-key",

"secret_key": "your-secret-key"

}
```

Run the script:

``` python
main.py
```

The graphical interface will appear, prompting you to enter the time period for which you want to retrieve the order history. Valid options are 'today', 'yesterday', 'last 7 days', and 'last 30 days'.

Click the "Execute" button to fetch and display the results.

The script will save the order history as a CSV file named order_history.csv in the project directory.

#### Note: 
If any errors occur during execution, they will be logged in the script.log file in the project directory.

Feel free to explore your Binance P2P trading activity using this convenient Python-based GUI application!