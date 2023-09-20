import time
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException, WebDriverException





try:
    proxy_host = input("Enter Proxy hostname: ")
    proxy_port = input("Enter Proxy port: ")
    AGENT = input("Enter Agent ip address https://")
    #print("You entered:", new_password)
except KeyboardInterrupt:
    print("\nPassword input was canceled.")
except Exception as e:
    print("An error occurred:", e)


PROXY = proxy_host + ":" + str(proxy_port)
webdriver.DesiredCapabilities.FIREFOX['proxy'] = {
"httpProxy": PROXY,
"sslProxy": PROXY,
"proxyType": "manual",

}


opts = FirefoxOptions()
opts.add_argument("--headless") #headless is a must when there isn't desktop environment
opts.set_preference("accept_insecure_certs", True)
driverService = Service('geckodriver') 
driver = webdriver.Firefox(service=driverService, options=opts)


try:

    AGENT = 'https://' + str(AGENT)
    driver.set_page_load_timeout(5)
    driver.get(AGENT)
    time.sleep(1.77)
    print("Web page title:   ", driver.title)
    driver.quit()
    
except TimeoutException as ex:
     
    print(f" Host not reachable: {AGENT}\n")
        

except NoSuchElementException as ex:
        
        print(f" Element not found: {ex.msg}\n")
        

except (ElementNotInteractableException, ElementClickInterceptedException) as ex:
        
    print(f" Element not interactable or click intercepted: {ex.msg}\n")
        