#!/usr/bin/env python3
import sys
import time
import logging
import argparse
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
parser = argparse.ArgumentParser(description='Room reservation for NTNU',
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 usage='roomshark.py USERNAME PASSWORD [--starttime {8|12}] [--room roomID]')
parser.add_argument('username', help='Your feide username')
parser.add_argument('password', help='Your feide password')
parser.add_argument('--starttime', default='8',
                    help='Either 8 or 12. Booking will be for starttime + 4 hours')
parser.add_argument('--room', default='51003.012', help='The id of the room you wish to book.' +
                    'For S312 use 51003.012 and for S313 use 51003.013')
parser = parser.parse_args()


# Log in to feide and send reservation
# @param start_time should be either 8 or 12
# @param room should be '51003.012' or '51003.013'
def send_reservation(username, password, start_time, room):
    # Using virtualdisplay, will be running on server with no window manager 
    logger.debug("Starting chromedriver")
    display = Display(visible=0, size=(800,600))
    display.start()
    driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
    driver.get("https://idp.feide.no/simplesaml/module.php/feide/login.php?asLen=241&AuthState=_4b555877341923271e48c51b9f56db91a63873a9a8%3Ahttps%3A%2F%2Fidp.feide.no%2Fsimplesaml%2Fsaml2%2Fidp%2FSSOService.php%3Fspentityid%3Dhttps%253A%252F%252Flogin.paas2.uninett.no%252Ffeide-feide-kp%252Fmetadata%26cookieTime%3D1520351802%26RelayState%3Dhttps%253A%252F%252Fkunde.feide.no%252F") 
    logger.debug("Logging in to feide")
    try:
        search_box = driver.find_element_by_id("org_selector-selectized") 
        search_box.send_keys("NTNU\ue006") 
        search_box = driver.find_element_by_id("username") 
        search_box.send_keys(username) 
        search_box = driver.find_element_by_id("password") 
        search_box.send_keys(password) 
        search_box.submit() 
    except Exception:
        logger.exception("Couldnt select NTNU when logging in to feide")
        return

    # Go directly to the date two weeks from now with the correct starting time
    date = str(datetime.date.today() + datetime.timedelta(days=14))
    url = 'https://tp.uio.no/ntnu/rombestilling/?start=' + start_time + ':00&preset_date=' + date + '&roomid=' + room
    driver.get(url)

    # Find the element which decides end time
    try:
        search_box = driver.find_element_by_id("duration") 
        if (start_time == '8'):
            search_box.click()
            search_box.send_keys("12")
        else:
            search_box.click()
            search_box.send_keys("16")
        search_box = driver.find_element_by_id("rb-bestill") 
        search_box.send_keys("\ue006") 
        logger.debug("Clicked submit, waiting view to change")
    except Exception:
        logger.critical("Wrong login or room already booked.")
        return
    # Clicked submit, waiting up to 5 seconds for view to change
    element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "name")))
    try:
        element.send_keys("\ue004\ue004\ue004\ue006") 
        logger.debug("Sending confirmation")
    except Exception:
        logger.exception("Selenium couldnt find confirmation button")
    finally:
        logger.info('Successfully created reservation')
        driver.quit() 


def main():
    # Get arguments
    username = parser.__getattribute__('username')
    password = parser.__getattribute__('password')
    start_time = parser.__getattribute__('starttime')
    room = parser.__getattribute__('room')
    send_reservation(username, password, start_time, room)


if __name__ == "__main__":
        main()
