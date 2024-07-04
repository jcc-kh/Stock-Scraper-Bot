!pip install pytelegrambotapi
import telebot
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import pandas as pd

API_TOKEN = 'GetTokenFromBotFather'
bot = telebot.TeleBot(API_TOKEN)

stock_ticker_symbols = ['add your own stocks']

@bot.message_handler(commands=['start'])
def initialise(message):
    global stock_list, link, stock_dict
    stock_list = []
    link = "https://query1.finance.yahoo.com/v8/finance/chart/"
    stock_dict = {'Ticker': [],
                  'Traded Price': [],
                  'Traded Volume': []}
    bot.reply_to(message, 'What would you like to do today?')
    show_options(message)

def show_options(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    option1 = types.KeyboardButton('Show Favourites')
    option2 = types.KeyboardButton('Add Stock to Favourites')
    markup.add(option1, option2)
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)
    bot.register_next_step_handler(message, handle_option)

def handle_option(message):
    option = message.text
    if option == 'Show Favourites':
        show_favourites(message)
    elif option == 'Add Stock to Favourites':
        add_stock(message)
    else:
        bot.send_message(message.chat.id, 'Response not understood. Please choose a valid option.')


def show_favourites(message):
    if stock_list:
        bot.reply_to(message, "Here are your favourites:")
        for stock in stock_list:
            bot.register_next_Sstep_handler(message, get_stock_data(stock))

    else:
        bot.reply_to(message, "Sorry! You have no favourites at the moment.")
        show_options(message)
# Example link (base URL)


def get_stock_data(symbol):
    
    agent_list = [
        'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
    ]
    url = link + symbol
    params = {
        'region': 'US',
        'lang': 'en-US',
        'includePrePost': 'false',
        'interval': '1d',
        'range': '1d',
    }
    headers = {
        'User-Agent': random.choice(agent_list),
        'Accept': 'application/json',
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Extracting price and volume data
        if 'chart' in data and 'result' in data['chart'] and len(data['chart']['result']) > 0:
            result = data['chart']['result'][0]
            
            # Extracting price from the result
            if 'indicators' in result and 'quote' in result['indicators'] and \
                    'close' in result['indicators']['quote'][0] and \
                    len(result['indicators']['quote'][0]['close']) > 0:
                price = result['indicators']['quote'][0]['close'][-1]
            else:
                price = 'Not available'

            # Extracting volume from the result
            if 'indicators' in result and 'quote' in result['indicators'] and \
                    'volume' in result['indicators']['quote'][0] and \
                    len(result['indicators']['quote'][0]['volume']) > 0:
                volume = result['indicators']['quote'][0]['volume'][-1]
            else:
                volume = 'Not available'

            # Append the data to the stock_dict
            stock_dict['Ticker'].append(symbol)
            stock_dict['Traded Price'].append(price)
            stock_dict['Traded Volume'].append(volume)
        else:
            print(f"No data available for {symbol}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {symbol}: {e}")

    # After updating the dictionary, call send_dataframe
    send_dataframe(symbol)

def send_dataframe(message):
    # Create a DataFrame from stock_dict
    df = pd.DataFrame(stock_dict)
    
    # Save the DataFrame as an image
    plt.figure(figsize=(10, 4))
    plt.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
    plt.axis('off')
    plt.savefig('dataframe.png')
    # Send a photo
    with open('dataframe.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo)
    handle_option(message)


def add_stock(message):
    # Format the message with a link using HTML
    bot.reply_to(message, "Key in the ticker symbol for the company you would like to add. Check out <a href='https://stockanalysis.com/stocks/'>this link</a> for more information.", parse_mode='HTML')
    bot.register_next_step_handler(message, handle_stock)

def handle_stock(message):
    stock = message.text
    if stock not in stock_ticker_symbols:
        bot.reply_to(message, "Please enter a valid stock ticker symbol.")
        add_stock(message)
    else:
        stock_list.append(stock)
        bot.reply_to(message, f"Added {stock} to favourites.")
        print(stock_list)
        show_favourites(message)
