import time
import json
import getpass
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




# Ask for the password before selenium instance

try:
    new_password = getpass.getpass("Enter Agents new password: ")
    #print("You entered:", new_password)
except KeyboardInterrupt:
    print("\nPassword input was canceled.")
except Exception as e:
    print("An error occurred:", e)


#Load Config
config_path = "config.json"
try:
    print("Reading Config")
    with open(config_path, 'r') as file:
        # Step 3: Load the JSON data into a Python dictionary
        config_data = json.load(file)
        
except FileNotFoundError:
    print(f"Config file '{config_path}' not found.")
    exit()


#Selenium Object



opts = FirefoxOptions()
opts.add_argument("--headless") #headless is a must when there isn't desktop environment
opts.set_preference("accept_insecure_certs", True)
#opts.profile.set_preference()
driverService = Service('geckodriver') 
driver = webdriver.Firefox(service=driverService, options=opts)


# Variables
status = ''

# Date & Time
def timestamp():
    date_time_now = datetime.now()
  
    return date_time_now.strftime("%m/%d/%H:%M:%S")


def dump_logs(d_logs):
    d_logs = str(d_logs)
    file_name = 'dump' + timestamp().replace('/', '_')[:8] + '.log'
    f = open(file_name, 'a+')  # open file in append mode
    f.write(d_logs)
    f.close()


def login(host_ip, password) -> bool:

    portal = 'https://' + host_ip
    dump_logs(d_logs=portal)

    try:

        driver.set_page_load_timeout(7)
        driver.get(portal)
        time.sleep(1.77)
        driver.find_element(By.NAME, 'username').send_keys('admin')
        time.sleep(0.77)
        driver.find_element(By.NAME, "password").send_keys(password)
        time.sleep(0.77)
        driver.find_element(By.CSS_SELECTOR, '.btn-outline-default').submit()
        time.sleep(1.77)

        return True
    
    except TimeoutException as ex:
        print(f" Host not reachable: {portal}")
        dump_logs(d_logs=ex)
        return False

    except NoSuchElementException as ex:
        print(f" Element not found: {ex.msg}")
        dump_logs(d_logs=ex)
        return False

    except (ElementNotInteractableException, ElementClickInterceptedException) as ex:
        print(f" Element not interactable or click intercepted: {ex.msg}")
        step = "\nNetwork Conf " + portal
        dump_logs(d_logs=step)
        dump_logs(d_logs=ex)
        return False

    except WebDriverException as ex:
        print(" WebDriver exception occurred: Host " + portal + " not reachable")
        dump_logs(d_logs=ex)
        return False
    

def wait_and_click(selector, timeout=10):
        
    element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(selector))
    element.click()


def initial_setup(new_password, accgroup_token, default_password):
    status = ''
    status += "\n" + timestamp() + "-> Enterprise Agent Reachable "

    try:

        time.sleep(1.77)
        driver.find_element(By.NAME, "originalPassword").send_keys(default_password)
        time.sleep(0.77)
        driver.find_element(By.NAME, "newPassword").send_keys(new_password)
        time.sleep(0.77)
        driver.find_element(By.NAME, "confirmPassword").send_keys(new_password)
        time.sleep(3.33)
        #change_password = WebDriverWait(driver, 17).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn:nth-child(5)")))
        #change_password.click()
        driver.find_element(By.CSS_SELECTOR, "button.btn:nth-child(5)").submit()
        time.sleep(2.77)

        status += "\n" + timestamp() + "-> Original Password Has Changed Successfully "

    except(NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException) as ex:
        pass
            #print(ex)
        dump_logs(d_logs=ex)

        status += "\n" + timestamp() + "-> Could not Change Original Password"

    try:
        time.sleep(2.3)
        driver.find_element(By.NAME, "accountToken").send_keys(accgroup_token)
        time.sleep(1.77)
        next_button = WebDriverWait(driver, 7).until(EC.element_to_be_clickable((By.ID, "setupButtonNext")))
        time.sleep(1.77)
        next_button.click()
        status += "\n" + timestamp() + "-> Account Group Token Changed Successfully "
        time.sleep(5.4)##setupButtonNext

    except(NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException) as ex:
        pass
        dump_logs(d_logs=ex)

        return status


def logout(button_CSS):

    try:
        
        logout = (By.CSS_SELECTOR, button_CSS)#child(2)
        wait_and_click(logout)

    except TypeError as err:

        print(err)
        


def get_status(host_ip, hostname):

    portal = ('https://' + host_ip + '/status')
    portal = portal.strip(' ')
    hostname = hostname + '.png'
    driver.switch_to.new_window('tab')
    tabs = driver.window_handles
    time.sleep(0.77)
    driver.switch_to.window(tabs[0])
    time.sleep(0.77)
    driver.close()
    time.sleep(0.77)
    driver.switch_to.window(tabs[1])
    driver.get(portal)
    time.sleep(1.77)
    driver.execute_script("window.scrollTo(0, 277)")
    time.sleep(1.77)

    final_status = ''
    for i in driver.find_elements(By.CLASS_NAME, "diagnostics-message"):
        final_status += "\n" + i.text

    driver.save_screenshot(hostname)

    return final_status


def swap_window(host_ip):
        
        portal = 'https://' + host_ip + '/status'
        
        time.sleep(1.77)
        driver.switch_to.new_window('tab')
        tabs = driver.window_handles
        #time.sleep(1.77)
        #driver.switch_to.window(tabs[0])
        #time.sleep(1.77)
        #driver.close()
        time.sleep(1.77)
        driver.switch_to.window(tabs[1])
        time.sleep(1.77)
        driver.get(portal)
        time.sleep(1.77)
        driver.refresh()
        time.sleep(1.77)
        # Wait until the specified text appears in the element
        #diagnostics_message_locator = (By.CLASS_NAME, "diagnostics-message")
        #diagnostics_message_text = "Agent is running."
        #WebDriverWait(driver, 17).until(EC.text_to_be_present_in_element(diagnostics_message_locator, diagnostics_message_text))



def network_setup(eas_ipAddress, hostname, ntp, proxy, proxy_port, cert):

    status = ''

    try:

        if ntp:

            driver.find_element(By.LINK_TEXT, "Time").click()
            #time.sleep(1.07)
            # Define the CSS selectors
            selector1 = 'div.form-group:nth-child(2) > div:nth-child(2) > input:nth-child(1)'
            selector2 = 'div.form-group:nth-child(1) > div:nth-child(2) > input:nth-child(1)'
            

            try:
            
                current_ntp_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector1)))
                current_ntp = current_ntp_element.get_attribute("value")
            
            except NoSuchElementException:
            
                current_ntp_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector2)))
                current_ntp = current_ntp_element.get_attribute("value")

            if current_ntp != ntp:
                current_ntp_element.clear()
                
                try:
                    current_ntp_element.send_keys(ntp)
                    driver.find_element(By.ID, "submit-form").submit()
                    time.sleep(3.3)
                except (NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException) as ex:
                    pass

                
                swap_window(host_ip=eas_ipAddress)
                logout(button_CSS="button.btn-outline-default:nth-child(2)")
                login(eas_ipAddress, new_password)

            else:

                swap_window(host_ip=eas_ipAddress)
                logout(button_CSS="button.btn-outline-default:nth-child(2)")
                login(eas_ipAddress, new_password)

        #Hostname
        driver.find_element(By.LINK_TEXT, "Network").click()
        time.sleep(1.77)

        if hostname:

            driver.find_element(By.ID, "hostname").clear()
            time.sleep(0.77)
            driver.find_element(By.ID, "hostname").send_keys(hostname)
            time.sleep(0.77)
            status += "\n" + timestamp() + "-> Hostname Changed "

        else:
            status += "\n" + timestamp() + "-> Hostname Default"
            time.sleep(0.77)


        #SSL
        if cert > 0:
                
                driver.find_element(By.LINK_TEXT, "Network").click()
                time.sleep(1.77)

                driver.find_element(By.NAME, "proxy-ca").send_keys(CERT)
                status += "\n" + timestamp() + "-> SSL cert ok "
                time.sleep(0.77)


        #apt-get proxy
        if proxy:

            # Find the checkbox element
            checkbox = driver.find_element(By.NAME, "use-apt-proxy")

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

                time.sleep(0.77)
                driver.find_element(By.NAME, "use-apt-proxy").click()
                time.sleep(0.77)
                driver.find_element(By.NAME, "apt-proxy-host").send_keys(proxy)
                time.sleep(0.77)
                driver.find_element(By.NAME, "apt-proxy-port").send_keys(proxy_port)
                time.sleep(0.77)

        # Done Network
        driver.find_element(By.ID, "submit-form").submit()
        time.sleep(5.55)
        status += "\n" + timestamp() + "-> Network Setup Complete "
        time.sleep(5.55)

            #Status

        return status

    except(TimeoutException, NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException) as ex:

        status += "\n" + timestamp() + "-> Network Setup Fail"
        dump_logs(d_logs=ex)

        return False




start_time = time.perf_counter()

file_path = 'agents.csv'
try:

    with open(file_path, 'r') as file:

        lines = file.readlines()
        line_count = len(lines)

        # Progress Bar
        bar = Bar('Configuring ', max=line_count)

        for line in lines:

            #bar.next()
            # Split each line using the comma delimiter
            eas = line.strip().split(',')

            eas_ipAddress = eas[0]
            eas_hostName = eas[1]
            eas_status = eas[2]
            #eas_portal = "https://" + eas_ipAddress

            #print(" " + eas_ipAddress + " ")

            if eas_status == "NEW":

                if login(eas_ipAddress, config_data.get("defaultPassword")):

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

                    print(" Not New Agent")                  
                    

            elif eas_status == "NOTNEW":

                
                if login(eas_ipAddress, new_password):

                    network_setup(eas_ipAddress=eas_ipAddress,
                                  hostname=eas_hostName, 
                                  ntp=config_data['NTP'], 
                                  proxy=config_data['proxy_url'], 
                                  proxy_port=config_data['proxy_port'], 
                                  cert=config_data['cert'])
            
                else:

                    print(" Login Failed")
            
            
            
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

#