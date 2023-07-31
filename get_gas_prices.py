# -*- coding: utf-8 -*-
"""
code to scrape local gas prices online, save them to a spreadsheet, and plot the last 30 days

Created on Sat Jul 29 09:57:55 2023

@author: Daniel
"""

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
import datetime

###############################################################
# AUTOMATICALLY DOWNLOAD WEBDRIVER #
# https://stackoverflow.com/questions/62017043/automatic-download-of-appropriate-chromedriver-for-selenium-in-python

import requests, wget, zipfile, os
def scrape_prices():
    # get lastest chrome driver version number
    url = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE'
    response = requests.get(url)
    version_number = response.text
    
    # build the download url
    download_url = "https://chromedriver.storage.googleapis.com/" + version_number +"/chromedriver_win32.zip"
    
    driver_location = os.path.join(os.getcwd(), 'chromedriver.exe')
    
    if os.path.isfile(driver_location) == False:
        # download the zip file using the url built above
        latest_driver_zip = wget.download(download_url,'chromedriver.zip')
        print('Downloaded web driver')
        # extract the zip file only if file exists
        with zipfile.ZipFile(latest_driver_zip, 'r') as zip_ref:
            zip_ref.extractall() # you can specify the destination folder path here
        # delete the zip file downloaded above
        os.remove(latest_driver_zip)
    
    ###############################################################
    
    # OPEN WEBPAGE AND GET THE HISTORIC GAS PRICES
    
    driver = webdriver.Chrome(executable_path=os.path.join(os.getcwd(), 'chromedriver.exe'))
    driver.implicitly_wait(0.5)
    
    gas_url = r'https://toronto.citynews.ca/toronto-gta-gas-prices/'
    
    driver.get(gas_url)
    
    prices_table = driver.find_elements(By.CLASS_NAME, 'page-table-body')

    prices = prices_table[0].text.split('\n')
    for i in range(len(prices)):
        prices[i] = prices[i].split()
    
    driver.close()
    
    return prices

prices = scrape_prices()

def add_new_price_data(prices):
    # SAVE PRICE HISTORY TO A SPREADSHEET
    #todays_price = prices[1].split()
    
    prices_df = pd.DataFrame(data=prices[1:], columns=['month', 'day', 'year', 'Price Change (cents)', 'filler column', 'Price (cents/L)', 'filler2 column'])
    # convert month names to month numbers
    def monthToNum(monthName):
        return {
                'January':1,
                'February':2,
                'March':3,
                'April':4,
                'May':5,
                'June':6,
                'July':7,
                'August':8,
                'September':9,
                'October':10,
                'November':11,
                'December':12
            }[monthName]
    
    prices_df = prices_df.drop(['filler column', 'filler2 column'], axis=1)
    prices_df['month'] = prices_df['month'].map(monthToNum)
    
    for col in prices_df.columns:
        prices_df[col] = prices_df[col].astype('float', errors='ignore')
        
    for i in range(len(prices_df)):
        prices_df['day'][i] = prices_df['day'][i].replace(',', '')
    
    prices_df['datetime'] = pd.to_datetime(prices_df[['year', 'month', 'day']])
    prices_df = prices_df.drop(['year', 'month', 'day'], axis=1)
    
    
    if os.path.isfile(os.path.join(os.getcwd(), 'gas_prices.csv')) == False: #file does not exist
        # create dataframe    
        prices_sheet = pd.DataFrame(data=None, columns=['Price Change (cents)', 'Price (cents/L)', 'datetime'])
        prices_sheet.to_csv(os.path.join(os.getcwd(), 'gas_prices.csv'), index=False)
        print('Created new spreadsheet and saved to hard drive')
        
            # add price for date if not in the spreadsheet
        for i in range(len(prices_df)):
            value_to_find = prices_df['datetime'][i].strftime('%Y-%m-%d')
            result = prices_sheet[prices_sheet['datetime'] == value_to_find]
            if result.empty is True: #date is not in the historical gas data
                prices_sheet = prices_sheet.append(prices_df.loc[i])
                print('Added data from {}'.format(prices_df['datetime'][i].strftime('%Y-%m-%d')))
        prices_sheet['datetime'] = pd.to_datetime(prices_sheet['datetime'])
        prices_sheet = prices_sheet.sort_values(by='datetime') #arrange oldest date at the top
        prices_sheet.to_csv(os.path.join(os.getcwd(), 'gas_prices.csv'), index=False)
        
    elif os.path.isfile(os.path.join(os.getcwd(), 'gas_prices.csv')) == True: #file does exist
        # load dataframe
        prices_sheet = pd.read_csv(os.path.join(os.getcwd(), 'gas_prices.csv'))
        print('Loaded spreadsheet from hard drive')
        
        # add price for date if not in the spreadsheet
        for i in range(len(prices_df)):
            value_to_find = prices_df['datetime'][i].strftime('%Y-%m-%d')
            result = prices_sheet[prices_sheet['datetime'] == value_to_find]
            if result.empty is True: #date is not in the historical gas data
                prices_sheet = prices_sheet.append(prices_df.loc[i])
                print(prices_df.loc[i])
                print('Added data from {}'.format(prices_df['datetime'][i].strftime('%Y-%m-%d')))
        prices_sheet['datetime'] = pd.to_datetime(prices_sheet['datetime'])
        #prices_sheet = prices_sheet.sort_values(by='datetime') #arrange oldest date at the top
        prices_sheet.to_csv(os.path.join(os.getcwd(), 'gas_prices.csv'), index=False)
        return prices_sheet
    
prices_sheet = add_new_price_data(prices)
# PLOT GAS PRICES OVER TIME

# title: date, price change (coloured), price
# x axis: time (date)
# y axis: price

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

plt.figure(figsize=(6.0, 4.8))
plt.plot(prices_sheet['datetime'][-30:], prices_sheet['Price (cents/L)'][-30:])
plt.ylabel('Price (\xa2 / L)')
plt.xlabel('Last 30 Days')
plt.xticks(rotation=90)

title_text = str(prices_sheet['Price Change (cents)'].tail(1).iloc[0])

plt.title('Change In Gas Price Today: ' + title_text + ' \xa2')
my_dpi = 96
plt.savefig('prices_plot.jpg', figsize=(600/my_dpi, 480/my_dpi), dpi=my_dpi)

# TODO: save plot as image and display it on e-ink display on Pi


