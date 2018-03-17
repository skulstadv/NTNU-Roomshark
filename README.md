# NTNU-Roomshark
Automatic reservation of rooms for NTNUs room reservation system

Use chromedriver v 2.33 (copy in this repo)
http://chromedriver.storage.googleapis.com/index.html?path=2.33/

Installation:

```sudo apt-get install -y chromium-browser xvfb python3-pip chromium-chromedriver
sudo cp chromedriver /usr/lib/chromium-browser/chromedriver
sudo chmod a+x /usr/lib/chromium-browser/chromedriver
pip3 install -r requirements.txt
```
Then run the script every day at 00:00 with crontab or something. It will automatically use the date two weeks from now as it is not possible to book more than two weeks in advance.
