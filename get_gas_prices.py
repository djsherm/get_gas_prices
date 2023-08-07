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
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

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
    
    driver = Service('/usr/lib/chromium-browser/chromedriver')
    #driver.implicitly_wait(0.5)
    page_to_scrape = webdriver.Chrome(service=driver)
    
    gas_url = r'https://toronto.citynews.ca/toronto-gta-gas-prices/'
    
    page_to_scrape.get(gas_url)
    
    prices_table = page_to_scrape.find_elements(By.CLASS_NAME, 'page-table-body')

    prices = prices_table[0].text.split('\n')
    for i in range(len(prices)):
        prices[i] = prices[i].split()
    
    page_to_scrape.close()
    
    return prices


#print(prices)

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

def parse_prices_make_sheet(prices):
    prices_df = pd.DataFrame(data=prices[1:], columns=['month', 'day', 'year', 'Price Change (cents)', 'filler column', 'Price (cents/L)', 'filler2 column'])
    prices_df = prices_df.drop(['filler column', 'filler2 column'], axis=1)
    
    #change month words to digits
    prices_df['month'] = prices_df['month'].map(monthToNum)
    
    for i in range(len(prices_df)): #remove comma after the day
        prices_df.loc[i, 'day'] = prices_df['day'][i].replace(',', '')
        
    for col in prices_df.columns: #convert to integers
        prices_df[col] = prices_df[col].astype('int', errors='ignore')
        
    prices_df['datetime'] = pd.to_datetime(prices_df[['year', 'month', 'day']])
    
    for i in range(len(prices_df)):
        prices_df.loc[i, 'datetime'] = prices_df['datetime'][i].strftime('%Y-%m-%d')
    
    return prices_df

def save_new_prices_to_drive(prices_df):
    found_sheet = os.path.isfile(os.path.join(os.getcwd(), 'gas_prices.csv'))
    
    if found_sheet == False: #first time running
        prices_df.to_csv(os.path.join(os.getcwd(), 'gas_prices.csv'), index=False)
        print('Created new spreadsheet and saved to hard drive: {}'.format(os.path.join(os.getcwd(), 'gas_prices.csv')))
    elif found_sheet == True: #saved price data already exists on the hard drive
        #load that sheet
        prices_ssd = pd.read_csv(os.path.join(os.getcwd(), 'gas_prices.csv'))
        print('Loaded spreadsheet from hard drive: {}'.format(os.path.join(os.getcwd(), 'gas_prices.csv')))
        
        #add the rows from prices_df that do not already exist in prices_ssd
        
        #loop through prices_df, and if the entry in column 'datetime' exists in the same named column in prices_ssd, delete it from prices_df
        for i in range(len(prices_df)):
            checked_date = prices_df['datetime'][i].strftime('%Y-%m-%d')
            print('looking for data from: ', checked_date)
            
            result_of_search = prices_df[prices_ssd['datetime'] == checked_date]
            print(result_of_search)
            if result_of_search.empty == True: #checked_date does not exist in the saved data
                print('Did not find data from {} in the sheet'.format(checked_date))
                prices_ssd.append(result_of_search)
                print('Added data from {}'.format(checked_date))
            else: #result_of_search is not empty
                print('Found data, no need to add again')
                
        prices_ssd = prices_ssd.to_csv(os.path.join(os.getcwd(), 'gas_prices.csv'), index=False)
        print('Saved new prices data to the ssd')
    return None

# def add_new_price_data(prices):
#     # SAVE PRICE HISTORY TO A SPREADSHEET
#     #todays_price = prices[1].split()
#     
#     prices_df = pd.DataFrame(data=prices[1:], columns=['month', 'day', 'year', 'Price Change (cents)', 'filler column', 'Price (cents/L)', 'filler2 column'])
#     # convert month names to month numbers
#     def monthToNum(monthName):
#         return {
#                 'January':1,
#                 'February':2,
#                 'March':3,
#                 'April':4,
#                 'May':5,
#                 'June':6,
#                 'July':7,
#                 'August':8,
#                 'September':9,
#                 'October':10,
#                 'November':11,
#                 'December':12
#             }[monthName]
#     
#     prices_df = prices_df.drop(['filler column', 'filler2 column'], axis=1)
#     prices_df['month'] = prices_df['month'].map(monthToNum)
#         
#     for i in range(len(prices_df)):
#         #prices_df['day'][i] = prices_df['day'][i].replace(',', '')
#         prices_df.loc[i, 'day'] = prices_df['day'][i].replace(',', '')
#         
#     for col in prices_df.columns:
#         prices_df[col] = prices_df[col].astype('int', errors='ignore')
#     #print(prices_df)
#         
#     prices_df['datetime'] = pd.to_datetime(prices_df[['year', 'month', 'day']])
#     #prices_df = prices_df.drop(['year', 'month', 'day'], axis=1)
#     
#     
#     if os.path.isfile(os.path.join(os.getcwd(), 'gas_prices.csv')) == False: #file does not exist
#         # create dataframe    
#         prices_sheet = pd.DataFrame(data=None, columns=['Price Change (cents)', 'Price (cents/L)', 'datetime'])
#         prices_sheet.to_csv(os.path.join(os.getcwd(), 'gas_prices.csv'), index=False)
#         print('Created new spreadsheet and saved to hard drive: {}'.format(os.path.join(os.getcwd(), 'gas_prices.csv')))
#         
#             # add price for date if not in the spreadsheet
#         for i in range(len(prices_df)):
#             value_to_find = prices_df['datetime'][i].strftime('%Y-%m-%d')
#             result = prices_sheet[prices_sheet['datetime'] == value_to_find]
#             if result.empty is True: #date is not in the historical gas data
#                 #prices_sheet = prices_sheet.append(prices_df.loc[i])
#                 prices_sheet = pd.concat([prices_sheet, prices_df.loc[i]], ignore_index=True, axis=1)
#                 print('Added data from {}'.format(prices_df['datetime'][i].strftime('%Y-%m-%d')))
#         #prices_sheet['datetime'] = pd.to_datetime(prices_sheet['datetime'])
#         prices_sheet = prices_sheet.sort_values(by='datetime') #arrange oldest date at the top
#         prices_sheet.to_csv(os.path.join(os.getcwd(), 'gas_prices.csv'), index=False)
#         
#     elif os.path.isfile(os.path.join(os.getcwd(), 'gas_prices.csv')) == True: #file does exist
#         # load dataframe
#         prices_sheet = pd.read_csv(os.path.join(os.getcwd(), 'gas_prices.csv'))
#         print('Loaded spreadsheet from hard drive: {}'.format(os.path.join(os.getcwd(), 'gas_prices.csv')))
#         
#         # add price for date if not in the spreadsheet
#         for i in range(len(prices_df)):
#             value_to_find = prices_df['datetime'][i].strftime('%Y-%m-%d')
#             print("finding: ", value_to_find)
#             result = prices_sheet[prices_sheet['datetime'] == value_to_find]
#             if result.empty is True: #date is not in the historical gas data
#                 #prices_sheet = prices_sheet.append(prices_df.loc[i])
#                 prices_sheet = pd.concat([prices_sheet, prices_df.loc[i]], ignore_index=True, axis=1)
#                 print(prices_df.loc[i])
#                 print('Added data from {}'.format(prices_df['datetime'][i].strftime('%Y-%m-%d')))
#         #prices_sheet['datetime'] = pd.to_datetime(prices_sheet['datetime'])
#         #prices_sheet = prices_sheet.sort_values(by='datetime') #arrange oldest date at the top
#             else:
#                 print("That data is already in the spreadsheet")
#         prices_sheet.to_csv(os.path.join(os.getcwd(), 'gas_prices.csv'), index=False)
#         return prices_sheet
# print("prices:\n",prices)
# prices_sheet = add_new_price_data(prices)
# PLOT GAS PRICES OVER TIME

# title: date, price change (coloured), price
# x axis: time (date)
# y axis: price

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def save_plot(prices_ssd):
    plt.figure(figsize=(6.0, 4.8))
    plt.plot(prices_ssd['datetime'][-30:], prices_ssd['Price (cents/L)'][-30:])
    plt.ylabel('Price (\xa2 / L)')
    plt.xlabel('Last 30 Days')
    plt.xticks(rotation=90)

    title_text = str(prices_ssd['Price Change (cents)'].tail(1).iloc[0])

    plt.title('Change In Gas Price Today: ' + title_text + ' \xa2')
    my_dpi = 96
    plt.savefig('prices_plot.jpg')

def wrapper():
    prices = scrape_prices()
    prices_df = parse_prices_make_sheet(prices)
    save_new_prices_to_drive(prices_df)
    prices_ssd = pd.read_csv(os.path.join(os.getcwd(), 'gas_prices.csv'))
    print(prices_ssd)
    save_plot(prices_ssd)
    return os.path.join(os.getcwd(), 'prices_plot.jpg')

wrapper()


