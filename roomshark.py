#!/usr/bin/env python3

import sys
import time
import logging
import argparse
import requests
import datetime
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Logging
logger = logging.getLogger('Roomshark')
logger.setLevel(logging.DEBUG)
# Create file handler which logs even debug messages
fh = logging.FileHandler('debug.log')
# Create console handler with a higher log level
ch = logging.StreamHandler(sys.stdout)
# Log level information, excludes debug messages
# TODO Change to info when done debugging
ch.setLevel(logging.DEBUG)
# Create format and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# Add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

# Argument parsing
parser = argparse.ArgumentParser(description='Automatic room reservation for NTNU', formatter_class=argparse.RawDescriptionHelpFormatter, usage='./roomshark.py user pw room date')
parser.add_argument('username', help='Your feide username')
parser.add_argument('password', help='Your feide password')
parser.add_argument('Room ID', help='The id of the room you wish to book')
parser.add_argument('Time', help='The date and time of the reservation on format: TODO')
parser.add_argument('-t', metavar='--test', help='Test order placement only')
parser.add_argument('-g', metavar='--graph', help='Show price spread graph')
parser = parser.parse_args()


# Lets create a cookie to use for the reservation using selenium with chrome
def create_cookie(username, password):
    # Using virtualdisplay, will be running on server with no window manager 
    display = Display(visible=0, size=(800,600))
    display.start()
    driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
    logger.debug("Creating headless chromium")
    driver.get("https://idp.feide.no/simplesaml/module.php/feide/login.php?asLen=241&AuthState=_4b555877341923271e48c51b9f56db91a63873a9a8%3Ahttps%3A%2F%2Fidp.feide.no%2Fsimplesaml%2Fsaml2%2Fidp%2FSSOService.php%3Fspentityid%3Dhttps%253A%252F%252Flogin.paas2.uninett.no%252Ffeide-feide-kp%252Fmetadata%26cookieTime%3D1520351802%26RelayState%3Dhttps%253A%252F%252Fkunde.feide.no%252F") 
    search_box = driver.find_element_by_id("org_selector-selectized") 
    try:
        search_box.send_keys("NTNU\ue006") 
    except Exception:
        logger.debug("Selenium couldn't find object")
        return 0
    search_box = driver.find_element_by_id("username") 
    search_box.send_keys(username) 
    search_box = driver.find_element_by_id("password") 
    search_box.send_keys(password) 
    search_box.submit() 
    logger.debug("Sent cookie request")
    all_cookies = driver.get_cookies() 
    cookies_dict = {}

    # TODO All related to manual POST. Not currently working.
    # Make cookies into dict format to parse
    for cookie in all_cookies:
            cookies_dict[cookie['name']] = cookie['value']
    cookie = cookies_dict['SimpleSAMLSessionID']
    logger.debug(cookie)

    # Request website from right domain to get our PHPSESSID cookie
    driver.get("https://tp.uio.no/ntnu/rombestilling/?start=8:00&preset_date=2018-03-21&roomid=51003.012")
    all_cookies = driver.get_cookies() 
    cookies_dict = {}
    # Make cookies into dict format to parse
    for cookie in all_cookies:
            cookies_dict[cookie['name']] = cookie['value']

    # Returning correct cookie now
    cookie = cookies_dict['PHPSESSID']
    logger.debug(cookie)

    search_box = driver.find_element_by_id("duration") 
    search_box.send_keys("12") 
    search_box = driver.find_element_by_id("rb-bestill") 
    search_box.send_keys("\ue006") 
    logger.debug("Sending submit and waiting up to 5sec for page to load")
    # Wait for element to be loaded
    element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "name")))
    try:
        element.send_keys("\ue004\ue004\ue004\ue006") 
        logger.debug("Sending confirmation")
    finally:
        driver.quit() 
        return cookie


# TODO For sending reservation through curl in case of competition. NOT CURRENTLY WORKING.
# Send the reservation with cookie
def send_reservation(cookie, date, first):
    url = 'https://tp.uio.no/ntnu/rombestilling/?start=8:00&preset_date=2018-03-21&roomid=51003.012'
    # Only split day into two, from 8 and from 12
    time = '08%3A00'
    if not first:
        # Second reservation today, booking from 12-16
        time = '12%3A00'
    date = datetime.date.today() + datetime.timedelta(days=13)
    logger.info("Date: " + str(date))
    data = {
        'name':'',
        'notes':'',
        'confirmed':'true',
        'start':time,
        'size':'5',
        'roomtype':'GRUPPE',
        'duration':'04%3A00',
        'area':'50000',
        'room%5B%5D':'51003.012',
        'building':'510',
        'preset_day':'WED',
        'preset_date':'2018-03-21', #Wrong form, make this an argument
        'exam':'',
        'dates%5B%5D':'2018-03-21',
        'tokenrb':'1337'
    }

    # Include cookie in headers along with user agent (dont want the website to think we are a bot)
    headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36' , 'cookie':  'PHPSESSID=' + cookie}

    r = requests.post(url = url2, headers = headers, data = data)
    answer = r.text.encode('UTF-8')
    logger.debug(answer)
    logger.debug(headers)
    logger.debug(data)


def main():
    logger.debug('Starting')
    username = parser.__getattribute__('username')
    password = parser.__getattribute__('password')
    cookie = create_cookie(username, password)
    logger.debug('Successfully created reservation')
    # TODO For manual request 
    #logger.debug("Got cookie: "+ cookie)
    #send_reservation(cookie, '2018-03-21', 1)
    #logger.debug("Sent reservation")


if __name__ == "__main__":
        main()
