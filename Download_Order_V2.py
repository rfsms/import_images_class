from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import json
import os
import pandas as pd
import boto3
import shutil

################################################################
# S3 Related
################################################################

def save_to_s3(file_path, bucket_name, s3_save_path):
    print('Starting Saving to S3 bucket ' + file_path)
    client = boto3.client('s3')
    client.upload_file(file_path, bucket_name, s3_save_path)
    print('Saving to S3 Bucket Ended successfully ' + file_path)

def uploading_to_s3(bucket_name, local_path, partitioned_prefix, img_name):
    print('Starting uploading to s3 ' + img_name)
    images = os.listdir(local_path)
    uploaded_images = 0
    if len(images) > 0:
        for img in images:
            count = 0
            img_path = local_path + img
            s3_save_path = partitioned_prefix + img
            while count < 3:
                try:
                    save_to_s3(img_path, bucket_name, s3_save_path)
                    count = 10
                    uploaded_images += 1
                except:
                    count += 1
    else:
        print('No images to be uploaded')
        return 0
    if uploaded_images > 0:
        print('Uploading to s3 Ended successfully')
    else:
        print('No image has been successfully uploaded')
    return len(images)

########### Browser Set Up ##################

def driver_setup(download_path,order_no = 0):
    if int(order_no) != 0:
        order_path = os.path.join(download_path, str(order_no))
        prefs = {'download.default_directory': order_path}
        browser_options = Options()
        browser_options.add_experimental_option("detach", True)
        browser_options.add_argument("--allow-running-insecure-content")
        # browser_options.headless = True
        browser_options.add_argument('--headless')
        browser_options.add_experimental_option('prefs', prefs)
        driver = webdriver.Chrome(options=browser_options)


    else:
        browser_options = Options()
        browser_options.add_experimental_option("detach", True)
        browser_options.add_argument("--allow-running-insecure-content")
        # browser_options.headless = True
        browser_options.add_argument('--headless')
        driver = webdriver.Chrome(options=browser_options)

    return driver

def login(login_url,usr_name,password,driver):

    driver.get(login_url)
    driver.maximize_window()
    sleep(5)
    username = driver.find_element(by='name',value='j_username')
    username.send_keys(usr_name)

    password_btn = driver.find_element(by='name',value='j_password')
    password_btn.send_keys(password)

    log_in_button = driver.find_element(by='xpath',value='//*[@type="submit"]')

    log_in_button.click()
    print("Logged In Successfully ....\n")
    sleep(5)

############ open txt file #####################

def open_txt_file(path):
    f = open(path)
    data = json.load(f)
    return data

def check_order_status(order_url,order_no,driver):

    driver.get(order_url + str(order_no))
    print(order_no)
    try:
        data = driver.find_element(by='xpath', value='//tr[@class="white"]')
        order_status = data.text.split(' ')[5]
        print("Order status is : ",order_status)
        if order_status == "Ready" or order_status == "Delivered":
            return "ready"
        else:
            print("Order Status is : "+order_status+"\nNo Data Found ....")
            return "not ready"
    except:
        print("No Order found ....")
        return "expired"

def check_order_subfolder(driver):

    order_btn = driver.find_element(by='xpath', value='//tr[@class="white"]//td//a')
    order_btn.click()
    sleep(10)
    try:
        sub_fldrs = driver.find_element(by='xpath',value="//table[contains(@class,'zebra center')]")
        print(" No Sub Folder Found,\nDownloading Products")
        return False
    except:
        return True


def download_order_products(lst,downloaded_product_name):
    downloaded_product_urls = []
    for itm in lst:
        itm_txt = str(itm.get_attribute('href'))
        if 'http' in itm_txt and "logout" not in itm_txt:
            if 'helpOpen' in itm_txt:
                product_name = itm_txt.split('001/')[1].split("')")[0]
                if product_name not in downloaded_product_name and itm_txt not in downloaded_product_urls:
                    itm.click()
                    print(product_name)
                    downloaded_product_urls.append(itm.get_attribute('href'))
                    downloaded_product_name.append(product_name)
                    sleep(10)
                    parent_han = driver.window_handles
                    all_han = driver.window_handles
                    new_han = [x for x in all_han if x != parent_han][1]
                    driver.switch_to.window(new_han)
                    driver.close()
                    driver.switch_to.window([x for x in all_han if x != parent_han][0])
    return downloaded_product_urls

def download_files(download_path,order_no):

    order_path = os.path.join(download_path, str(order_no))
    os.makedirs(order_path, exist_ok=True)
    downloaded_product_name = os.listdir(order_path)
    sleep(5)
    loading = True
    while loading == True:
        try:
            elements = driver.find_elements(by='xpath',value=
                "//table[contains(@class,'zebra center')]//tbody//tr//td//a[last ()]")
            element = elements[-1]
            driver.execute_script("arguments[0].scrollIntoView();", element)

            click_flag = True
            while click_flag == True:

                condition = True
                old_item = None
                while condition == True:
                    elements = driver.find_elements(by='xpath',value=
                        "//table[contains(@class, 'zebra center')]//tbody//tr//td//a[last ()]")
                    element_1 = elements[-1]
                    items = driver.find_elements(by='xpath',value='//table[@class="zebra center"]//tbody//tr//td//a')
                    download_order_products(items,downloaded_product_name)

                    if element_1 == old_item:
                        try:
                            sleep(2)
                            delay = 5
                            ActionChains(driver).send_keys(Keys.HOME).perform()
                            Next_page = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, "//input[contains(@value, ' Next ')]")))
                            ActionChains(driver).move_to_element(Next_page).perform()
                            Next_page.click()
                            sleep(5)

                        except:
                            sleep(5)
                            click_flag = False
                            print("No next page found ... ")
                        condition = False

                    else:
                        old_item = element_1
                        driver.execute_script("arguments[0].scrollIntoView();", old_item)
                        sleep(2)
            loading = False
        except:
            print("No Data Available")
            loading = False


if __name__ == "__main__":

    csv_file_path = 'order_info.csv'
    bucket_name = "rfims-prototype"
    credentials_file = 'login_parameters.json'
    cnfig_file_name = "search_config_file.json"
    login_data = open_txt_file(credentials_file)
    login_url = login_data['login_url']
    order_url_data = open_txt_file(cnfig_file_name)
    order_url = order_url_data['order_url']
    data_folder = 'data'
    current_path = os.getcwd()
    download_path = os.path.join(current_path, data_folder)
    username = login_data['username']
    password = login_data['password']
    pending_order_no = None
    print("Attempting Downloading Products From Pending Orders ....")
    df = pd.read_csv(csv_file_path)
    filtrd = df[df['status'] == 'pending']

    if not filtrd.empty:
        for order in filtrd['order_no']:
            pending_order_no = order
            driver = driver_setup(download_path, pending_order_no)

            # Attempt to log in with retries
            login_attempts = 1
            max_login_attempts = 3
            while login_attempts <= max_login_attempts:
                print(f'Login Attempt: {login_attempts} of 3')
                try:
                    login(login_url, username, password, driver)
                    break  # Exit loop if login is successful
                except WebDriverException as e:
                    print(f"Error accessing {login_url}: {e}")
                    login_attempts += 1
                    if login_attempts == max_login_attempts:
                        print(f"Max login attempts reached for order {pending_order_no}. Skipping to next order.")
                        continue  # Skip to the next order

            status_flag = check_order_status(order_url, pending_order_no,driver)
            if status_flag == "ready" and not check_order_subfolder(driver):

                download_files(download_path, pending_order_no)
                df.loc[df.order_no == order, 'status'] = "done"
                sat_name = df.loc[df.order_no == order, 'satelite_checked'].values[0]
                print("Data For Order :" + str(pending_order_no) + " is Successfully Downloaded ....")
                partitioned_prefix = "stand_alone/CLASS/" + str(sat_name) + "/" + str(pending_order_no) + "/"
                uploading_to_s3(bucket_name, download_path + "/" + str(pending_order_no) + "/", partitioned_prefix,
                                str(pending_order_no))
                shutil.rmtree(download_path + "/" + str(pending_order_no) + "/")
            elif status_flag == "expired":
                df.loc[df.order_no == order, 'status'] = "expired"
            df.to_csv(csv_file_path, index=False)
    else:
        print("No Pending order to Download")
    # df.to_csv(csv_file_path,index=False)







