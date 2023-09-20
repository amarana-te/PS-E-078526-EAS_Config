import time
import re
import json
import getpass
import logging
from datetime import datetime
from progress.bar import Bar
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from certificate import CERT

# Date & Time
def timestamp():
    date_time_now = datetime.now()
  
    return date_time_now.strftime("%m/%d/%H:%M:%S")

# Configure logging
logfile = timestamp().replace("/", "-").replace(":", "") + '-app.log'
logging.basicConfig(filename=logfile, level=logging.INFO)


# Ask for the password before selenium instance
try:

    while True:

        new_password = getpass.getpass("Enter Agent(s) new password: ")

        # Check if the password contains at least one capital letter
        if not re.search(r'[A-Z]', new_password):
            print("Password must contain at least one capital letter.")
            continue

        # Check if the password contains at least one digit
        if not re.search(r'[0-9]', new_password):
            print("Password must contain at least one digit.")
            continue

        # Check if the password is at least 8 characters long
        if len(new_password) < 8:
            print("Password must be at least 8 characters long.")
            continue

        # If all criteria are met, break out of the loop
        break

    print("\nPassword accepted!\n")

except KeyboardInterrupt:
    
    print("\nPassword input was canceled.")

except Exception as e:
    
    print("An error occurred:", e)



#Load Config
config_path = "config.json"
try:
    print("\nReading Config\n")
    with open(config_path, 'r') as file:
        # Step 3: Load the JSON data into a Python dictionary
        config_data = json.load(file)
        
except FileNotFoundError:
    print(f"Config file '{config_path}' not found.")
    exit()


#Selenium Object START#####

opts = FirefoxOptions()
opts.add_argument("--headless") #headless is a must when there isn't desktop environment
opts.set_preference("accept_insecure_certs", True)
opts.binary_location = "/opt/firefox/firefox"
if config_data.get("firefox_proxy"):

    PROXY = config_data.get("firefox_proxy")
    webdriver.DesiredCapabilities.FIREFOX['proxy'] = {
    "httpProxy": PROXY,
    "sslProxy": PROXY,
    "proxyType": "manual",
}
   
driverService = Service('/usr/bin/geckodriver', log_output='geckodriver.log') 
driver = webdriver.Firefox(service=driverService, options=opts)
driver.capabilities['timeouts']['implicit'] = 30

#Selenium Object END######


# Log driver capabilities
logging.info(driver.capabilities)



def dump_logs(d_logs):
    d_logs = str(d_logs)
    file_name = 'source_code' + timestamp().replace('/', '_')[:8] + '.log'
    f = open(file_name, 'a+')  # open file in append mode
    f.write(d_logs)
    f.close()


def wait_and_click(selector, timeout):
        
    try:

        logging.info(f"Waiting for element and clicking: {selector}")
        element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(selector))
        element.click()
        logging.info(f"Clicked element: {selector}")

    except TimeoutException:
        error_message = f"Timeout while waiting for element to be clickable: {selector}"
        logging.error(error_message)
        
    except NoSuchElementException:
        error_message = f"Element not found: {selector}"
        logging.error(error_message)
        
    except ElementNotInteractableException:
        error_message = f"Element not interactable: {selector}"
        logging.error(error_message)


def only_wait(selector, timeout):
    
    try:

        logging.info(f"selector: {selector}")
        element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(selector))
        logging.info(f"Element located: {element.tag_name}")
        
    except TimeoutException:
        logging.error(f"Timeout while waiting for element: {selector}")
        
    except NoSuchElementException:
        
        logging.error(f"Element not found: {selector}")
        

def issue_click():

    try:

        modal = driver.find_element(By.CSS_SELECTOR, "#SetupModal___BV_modal_content_")

        if modal.is_displayed():

            logging.info(timestamp() + "-----> The SETUP modal is present and visible.")
                        
        else:
            
            logging.info(timestamp() + "-----> The SETUP modal is NOT present and visible.")
    
    except NoSuchElementException:
            
            logging.info(timestamp() + "-----> The modal ELEMENT is NOT present and visible.")

    try:

        actions = ActionChains(driver)
        actions.move_by_offset(1250, 200)
        actions.perform()

        # Perform a click action at the center of the screen
        actions.click()
        actions.perform()
        logging.info(timestamp() + "-> >>>>> Clicking <<<<<")

    except Exception as e:

        logging.error(f"An error occurred while issuing a click: {str(e)}")


def logout(button_CSS):

    try:

        logging.debug(timestamp() + "---> " + driver.title)
        logout = (By.CSS_SELECTOR, button_CSS)#child(2)
        wait_and_click(selector=logout, timeout=30)
        logging.info(timestamp() + "-> *** Logout ***")

    except NoSuchElementException as ex:
        
        logging.error(f"Logout button not found with CSS selector: {button_CSS}")
        logging.exception(ex)

    except Exception as e:

        logging.error(f"An error occurred while logging out: {str(e)}")


def swap_window(host_ip):
        
        portal = 'https://' + host_ip + '/status'
        time.sleep(0.77)
        driver.switch_to.new_window('tab')
        tabs = driver.window_handles
        #driver.switch_to.window(tabs[0])
        #driver.close()
        time.sleep(0.77)
        driver.switch_to.window(tabs[1])
        time.sleep(0.77)
        driver.get(portal)
        time.sleep(1.77)
        driver.refresh()
        time.sleep(1.77)
        # Wait until the specified text appears in the element
        #diagnostics_message_locator = (By.CLASS_NAME, "diagnostics-message")
        #diagnostics_message_text = "Agent is running."
        #WebDriverWait(driver, 17).until(EC.text_to_be_present_in_element(diagnostics_message_locator, diagnostics_message_text))


def login(host_ip, password) -> bool:

    portal = 'https://' + host_ip
    logging.info(timestamp() + "-> Trying to login " + portal)

    try:

        #driver.set_page_load_timeout(7)
        driver.get(portal)
        time.sleep(0.77)
        username = (By.NAME, 'username')
        only_wait(selector=username, timeout=10)
        driver.find_element(*username).send_keys('admin')
        time.sleep(0.77)
        driver.find_element(By.NAME, "password").send_keys(password)
        time.sleep(0.77)
        driver.find_element(By.CSS_SELECTOR, '.btn-outline-default').submit()
        time.sleep(5)
        logging.info(timestamp() + "---> Logged in " + portal)
        logging.debug(timestamp() + "---> " + driver.title)

        return True
    

    except TimeoutException as ex:
        logging.error(f"Host not reachable: {portal}")
        logging.exception(ex)
        return False

    except NoSuchElementException as ex:
        logging.error(f"Element not found: {ex.msg}")
        logging.exception(ex)
        return False

    except (ElementNotInteractableException, ElementClickInterceptedException) as ex:
        logging.error(f"Element not interactable or click intercepted: {ex.msg}")
        logging.exception(ex)
        return False

    except WebDriverException as ex:
        logging.error(f"WebDriver exception occurred: Host {portal} not reachable")
        logging.exception(ex)
        return False


def setup_account_group(accgroup_token):

    try:

        time.sleep(5) 
        issue_click() #new
        logging.debug(timestamp() + "------> " + driver.title)        
        menu_agent = (By.LINK_TEXT, "Agent")
        wait_and_click(selector=menu_agent, timeout=30)
        logging.debug(timestamp() + "------> " + driver.title)
        logging.info(timestamp() + "-> Attempting to setup the Account Group Token")
        account_token_element = (By.NAME, "accountToken")
        only_wait(selector=account_token_element, timeout=30)
        driver.find_element(*account_token_element).send_keys(accgroup_token)
        time.sleep(1.77)
        #next_button = (By.ID, "setupButtonNext")
        submit_button = (By.CSS_SELECTOR, "#submit-form")
        wait_and_click(selector=submit_button, timeout=20)
        time.sleep(5.7)
        logging.info(timestamp() + "-> Account Group Token Changed Successfully")

        return True


    except NoSuchElementException as ex:

        logging.warning(timestamp() + "-> Account Group Token input element not found")
        logging.exception(ex)

        try:

            logging.debug(timestamp() + "------> " + driver.title)

        except TypeError as err:

            logging.warning(str(err))

        return False

    except ElementNotInteractableException as ex:

        logging.warning(timestamp() + "-> Account Group Token input element not interactable")
        logging.exception(ex)

        return False

    except Exception as e:

        logging.error(timestamp() + "-> Error occurred while changing Account Group Token: " + str(e))

        return False


def initial_setup(new_password, accgroup_token, default_password):
    
    logging.info(timestamp() + "-> Starting Initial Setup ")

    try:

        time.sleep(10)
        issue_click()
        original_password = (By.NAME, "originalPassword")
        only_wait(selector=original_password, timeout=15)
        driver.find_element(*original_password).send_keys(default_password)
        time.sleep(0.77)
        driver.find_element(By.NAME, "newPassword").send_keys(new_password)
        time.sleep(0.77)
        driver.find_element(By.NAME, "confirmPassword").send_keys(new_password)
        time.sleep(0.77)
        change_password = (By.CSS_SELECTOR, "button.btn:nth-child(5)")
        wait_and_click(selector=change_password, timeout=20)
        #driver.find_element(*change_password).submit()
        time.sleep(5)
        logging.info(timestamp() + "-> Original Password Has Changed Successfully")


    except NoSuchElementException as ex:

        logging.warning(timestamp() + "-> Original Password input element not found")
        logging.exception(ex)

        return False

    except ElementNotInteractableException as ex:

        logging.warning(timestamp() + "-> Original Password input element not interactable")
        logging.exception(ex)

        return False

    except Exception as e:

        logging.error(timestamp() + "-> Error occurred while changing Default Password: " + str(e))

        return False


    #Setup account group

    driver.refresh()
    time.sleep(5)
    issue_click()
    logout(button_CSS=".d-flex > button:nth-child(1)") 
    login(eas_ipAddress, new_password)

    setup_account_group(accgroup_token=accgroup_token) 
    
    
def setup_ntp(ntp, eas_ipAddress):

    menu_time = (By.LINK_TEXT, "Time")
    wait_and_click(selector=menu_time, timeout=10)
    
    # Define the CSS selectors
    selector1 = 'div.form-group:nth-child(2) > div:nth-child(2) > input:nth-child(1)'
    selector2 = 'div.form-group:nth-child(1) > div:nth-child(2) > input:nth-child(1)'
            
    logging.info(timestamp() + "-> Attempting to configure the NTP")

    try:
            
        current_ntp_element = WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector1)))
        current_ntp = current_ntp_element.get_attribute("value")
            
    except NoSuchElementException:
            
        current_ntp_element = WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector2)))
        current_ntp = current_ntp_element.get_attribute("value")

    if current_ntp != ntp:

        current_ntp_element.clear()
                
        try:

            time.sleep(0.77)    
            current_ntp_element.send_keys(ntp)
            driver.find_element(By.ID, "submit-form").submit()
            time.sleep(3.3)
            logging.info(timestamp() + " NTP changed")

            swap_window(host_ip=eas_ipAddress)
            logout(button_CSS="button.btn-outline-default:nth-child(2)")
            login(eas_ipAddress, new_password)
            
            return True
        
        except NoSuchElementException:

            logging.warning(timestamp() + "-> NTP input element not found")
            swap_window(host_ip=eas_ipAddress)
            logout(button_CSS="button.btn-outline-default:nth-child(2)")
            login(eas_ipAddress, new_password)


            return False

        except ElementNotInteractableException:

            logging.warning(timestamp() + "-> NTP input element not interactable")
            swap_window(host_ip=eas_ipAddress)
            logout(button_CSS="button.btn-outline-default:nth-child(2)")
            login(eas_ipAddress, new_password)

                        
            return False       

        except Exception as e:
            
            logging.error(timestamp() + "-> Error occurred while changing NTP: " + str(e))
            swap_window(host_ip=eas_ipAddress)
            logout(button_CSS="button.btn-outline-default:nth-child(2)")
            login(eas_ipAddress, new_password)

            return False       

        
    else:

        logging.info(timestamp() + " NTP nothing to change")
        swap_window(host_ip=eas_ipAddress)
        logout(button_CSS="button.btn-outline-default:nth-child(2)")
        login(eas_ipAddress, new_password)

        return False


def setup_hostname(hostname: str):

    try:

        logging.info(timestamp() + "-> Replacing Hostname")
        time.sleep(0.77)
        driver.find_element(By.ID, "hostname").clear()
        time.sleep(0.77)
        driver.find_element(By.ID, "hostname").send_keys(hostname)
        time.sleep(0.77)
        logging.info(timestamp() + "-> Hostname Changed ")

        return True

    except NoSuchElementException as ex:

        logging.warning(timestamp() + "-> Hostname input element not found")
        logging.exception(ex)

        return False

    except ElementNotInteractableException as ex:

        logging.warning(timestamp() + "-> Hostname input element not interactable")
        logging.exception(ex)

        return False

    except Exception as e:

        logging.error(timestamp() + "-> Error occurred while changing hostname: " + str(e))

        return False


def setup_ssl(CERT: str):

    try:

        logging.info(timestamp() + "-> trying to replace SSL cert ")
        time.sleep(0.77)        
        proxy_ca = (By.NAME, "proxy-ca")
        only_wait(selector=proxy_ca, timeout=10)
        apt_cert = driver.find_element(*proxy_ca)
        apt_cert.clear()
        time.sleep(0.77)
        apt_cert.send_keys(CERT)

        logging.info(timestamp() + "-> SSL cert replaced ")
        

    except NoSuchElementException as ex:

        logging.warning(timestamp() + "-> SSL input element not found")
        logging.exception(ex)

        return False

    except ElementNotInteractableException as ex:

        logging.warning(timestamp() + "-> SSL input element not interactable")
        logging.exception(ex)

        return False

    except Exception as e:

        logging.error(timestamp() + "-> Error occurred while changing the SSL cert: " + str(e))

        return False
   

def setup_apt_proxy(proxy: str, proxy_port: int):

    try:

        # Find the checkbox element
        time.sleep(0.77)
        apt_get_proxy = (By.NAME, "use-apt-proxy")
        only_wait(selector=apt_get_proxy, timeout=10)
        checkbox = driver.find_element(*apt_get_proxy)

        logging.info(timestamp() + " setting apt-get proxy")

        # Check if the checkbox is checked (ticked)
        if checkbox.is_selected(): 
            
            time.sleep(0.77)
            driver.find_element(By.NAME, "apt-proxy-host").clear()
            time.sleep(0.77)
            driver.find_element(By.NAME, "apt-proxy-host").send_keys(proxy)
            time.sleep(0.77)
            driver.find_element(By.NAME, "apt-proxy-port").clear()
            time.sleep(0.77)
            driver.find_element(By.NAME, "apt-proxy-port").send_keys(proxy_port)

        else:

            driver.find_element(By.NAME, "use-apt-proxy").click()
            time.sleep(0.77)
            proxy_host = (By.NAME, "apt-proxy-host")
            only_wait(selector=proxy_host, timeout=10)
            driver.find_element(*proxy_host).send_keys(proxy)
            time.sleep(0.77)
            driver.find_element(By.NAME, "apt-proxy-port").send_keys(proxy_port)
            time.sleep(0.77)


        logging.info(timestamp() + " apt-get proxy changed")


    except NoSuchElementException as ex:

        logging.warning(timestamp() + "-> apt-proxy input element not found")
        logging.exception(ex)

        return False

    except ElementNotInteractableException as ex:

        logging.warning(timestamp() + "-> apt-proxy input element not interactable")
        logging.exception(ex)

        return False

    except Exception as e:

        logging.error(timestamp() + "-> Error occurred while changing the apt-proxy " + str(e))

        return False
   

def network_setup(eas_ipAddress, hostname, ntp, proxy, proxy_port, cert):

    logging.info(timestamp() + "-> Network Setup")
    time.sleep(10)
    issue_click()
    
    #NTP
    if ntp:

        setup_ntp(ntp, eas_ipAddress)
        time.sleep(5)
        issue_click()


    #NETWORK TAB ############################
    menu_network = (By.LINK_TEXT, "Network")
    wait_and_click(selector=menu_network, timeout=20)
    time.sleep(0.77)
    #########################################

    #Hostname
    if hostname:

        setup_hostname(hostname)


    #SSL
    if cert > 0:
                
        setup_ssl(CERT)


    #apt-get proxy
    if proxy and proxy_port:

        setup_apt_proxy(proxy=proxy, proxy_port=proxy_port)

    
    # Done Network
    time.sleep(0.77)
    driver.find_element(By.ID, "submit-form").submit()
    time.sleep(7.77)
    logging.info(timestamp() + "-> Network Setup Complete ")
    

    return True



start_time = time.perf_counter()

file_path = 'agents.csv'
try:

    with open(file_path, 'r') as file:

        lines = file.readlines()
        line_count = len(lines)

        # Progress Bar
        bar = Bar('Configuring Agent(s): ', max=line_count)
        

        for line in lines:

            bar.next()

            # Split each line using the comma delimiter
            eas = line.strip().split(',')
            eas_ipAddress = str(eas[0])
            eas_hostName = str(eas[1])
            eas_status = eas[2]


            if eas_status == "NEW":

                if login(eas_ipAddress, config_data.get("defaultPassword")):

                    logging.info("login successfull for the new Agent")

                    initial_setup(new_password, accgroup_token=config_data['accountGroupToken'], default_password=config_data['defaultPassword'])

                    time.sleep(5)
                    logout(button_CSS=".d-flex > button:nth-child(1)") 
                    login(eas_ipAddress, new_password)
                    time.sleep(3)

                    network_setup(eas_ipAddress=eas_ipAddress,
                                  hostname=eas_hostName,
                                  ntp=config_data['NTP'], 
                                  proxy=config_data['proxy_url'], 
                                  proxy_port=config_data['proxy_port'], 
                                  cert=config_data['cert'])

                else:

                    logging.warning("Could not Login, not a new agent?")                
                    

            elif eas_status == "NOTNEW":

                
                if login(eas_ipAddress, new_password):

                    logging.info("login successfull for not new Agent")

                    network_setup(eas_ipAddress=eas_ipAddress,
                                  hostname=eas_hostName, 
                                  ntp=config_data['NTP'], 
                                  proxy=config_data['proxy_url'], 
                                  proxy_port=config_data['proxy_port'], 
                                  cert=config_data['cert'])
            
                else:

                    logging.warning("Could not Login, Password incorrect?")     
            
             
            #delete all cookies
            driver.delete_all_cookies() 

except FileNotFoundError:
    print(f"CSV file '{config_path}' not found.")
    #exit()

except Exception as e:
    print("An error occurred:", e)  


bar.finish()
driver.quit()
print("\n\tTotal Elapsed Time ", time.perf_counter() - start_time)
print("\n\n")