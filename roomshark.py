#!/usr/bin/python3
import os
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
fh = logging.FileHandler(str(os.path.dirname(os.path.realpath(__file__)) + '/debug.log'))
# Create console handler with a higher log level
ch = logging.StreamHandler(sys.stdout)
# Log level information, debug messages visible in file console handler
ch.setLevel(logging.DEBUG)
fh.setLevel(logging.INFO)
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
parser.add_argument('--starttime', default='9',
                    help='Either 8 or 12. Booking will be for starttime + 4 hours')
parser.add_argument('--room', default='510S313', help='The id of the room you wish to book.' +
                    'For S312 use 510S312 and for S313 use 510S313')
parser = parser.parse_args()

# Creating chromedriver
# Using virtualdisplay, will be running on server with no window manager
logger.info("Starting chromedriver")
display = Display(visible=0, size=(800,600))
display.start()
driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")


# Log in to feide and send reservation
# @param start_time should be either 8 or 12
# @param room should be '510S312' or '510S313'
def send_reservation(start_time, room):
    # Go directly to the date two weeks from now with the correct starting time
    # Days should be 14 if server has GMT+1 timezone
    date = str(datetime.date.today() + datetime.timedelta(days=14))
    logger.info("Reserving for date: " + date)
    url = 'https://tp.uio.no/ntnu/rombestilling/?start=' + start_time + ':00&duration=4:00&preset_date=' + date + '&roomid=' + room
    driver.get(url)

    # Find the element which decides end time
    try:
        search_box = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "rb-bestill")))
        search_box.click()
        logger.debug("Clicked submit, waiting view to change")
    except Exception:
        logger.error("Wrong login, room already booked or no more bookings available for this user.")
        return False

    # Clicked submit, waiting up to 5 seconds for view to change
    element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "name")))
    try:
        element.send_keys("\ue004\ue004\ue004\ue006")
        logger.debug("Sending confirmation")
    except Exception:
        logger.exception("Selenium couldnt find confirmation button")
    finally:
        logger.info('Successfully created reservation')
        return True;

# Start chromedriver
def login(username, password):
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



def main():
    # Get arguments
    username = parser.__getattribute__('username')
    password = parser.__getattribute__('password')
    start_time = parser.__getattribute__('starttime')
    room = parser.__getattribute__('room')
    # Get cookie
    login(username, password)
    # Reservation for 9 - 13
    if (not send_reservation('9', room)):
        # If the reservation doesnt go through just try to book room 312 instead
        logger.debug("Room booked it seems, trying S313")
        send_reservation('9', '510S312')
    # Reservation for 13 - 17
    if (not send_reservation('13', room)):
        # If the reservation doesnt go through just try to book room 312 instead
        logger.debug("Room booked it seems, trying S313")
        send_reservation('13', '510S312')
    driver.quit()


if __name__ == "__main__":
        main()
