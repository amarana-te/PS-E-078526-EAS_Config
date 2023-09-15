import time
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException, Web>


opts = FirefoxOptions()
opts.add_argument("--headless") #headless is a must when there isn't desktop environment
opts.set_preference("accept_insecure_certs", True)
opts.binary_location = "/opt/firefox/firefox"
driverService = Service('geckodriver', log_output='geckodriver.log') 
driver = webdriver.Firefox(service=driverService, options=opts)
driver.capabilities['timeouts']['implicit'] = 30
print(driver.capabilities)


