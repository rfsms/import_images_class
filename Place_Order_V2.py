






from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import datetime
import json
import os
import pandas as pd

########### Browser Set Up ##################

def driver_setup(download_path,order_no = 0):
    if int(order_no) != 0:
        order_path = os.path.join(download_path, str(order_no))
        prefs = {'download.default_directory': order_path}
        browser_options = Options()
        browser_options.add_experimental_option("detach", True)
        browser_options.add_argument("--allow-running-insecure-content")
        browser_options.headless = True
        browser_options.add_argument('--headless')
        browser_options.add_experimental_option('prefs', prefs)
        driver = webdriver.Chrome(options=browser_options)


    else:
        browser_options = Options()
        browser_options.add_experimental_option("detach", True)
        browser_options.add_argument("--allow-running-insecure-content")
        browser_options.headless = True
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



def pars_data_from_cnfg_file(data):

    key_lst = []
    value_xpath_lst = []
    for key, value in data.items():
        if value['status'] == 'yes':
            print(key, " >>> Checked")
            value_xpath = value['xpath']
            value_xpath_lst.append(value_xpath)
            key_lst.append(key)



    return value_xpath_lst,key_lst



def pars_mapdata_from_cnfg_file(d):
    nlat = 0
    wlon = 0
    elon = 0
    slat = 0
    loc = 0
    for key, value in d.items():
        if value['status'] == 'yes':
            print(key, " >>> Checked")
            loc = key
            nlat = value['nlat']
            wlon = value['wlon']
            elon = value['elon']
            slat = value['slat']
    return loc ,nlat ,wlon, elon, slat



def input_data(element,input):
    element.click()
    sleep(2)
    element.send_keys(Keys.CONTROL, 'a')
    element.send_keys(Keys.BACKSPACE)
    element.send_keys(input)
    sleep(2)



def map_point(cnfig_file_name):
    config_dict = open_txt_file(cnfig_file_name)

    loc, nlat ,wlon, elon, slat = pars_mapdata_from_cnfg_file(config_dict["location_map_points"])

    nlat_el = driver.find_element(by='name', value='nlat')
    input_data(nlat_el, nlat)

    wlon_el = driver.find_element(by='name', value='wlon')
    input_data(wlon_el, wlon)

    elon_el = driver.find_element(by='name', value='elon')
    input_data(elon_el, elon)

    slat_el = driver.find_element(by='name', value='slat')
    input_data(slat_el, slat)

    print(str(loc) +" located ....\n")
    sleep(2)
    click_out = driver.find_element(by='xpath', value="//html")
    click_out.click()
    sleep(2)
    return loc



def order_criteria(start_date,end_date,config_dict,sat_xpth):
    start = driver.find_element(by='name',value='start_date')
    driver.execute_script("arguments[0].scrollIntoView();", start)
    start.clear()
    sleep(2)
    start.send_keys(start_date)

    end = driver.find_element(by='name',value='end_date')
    end.clear()
    sleep(2)
    end.send_keys(end_date)


    print("\nSelecting Satellite ....")
    sat_click = driver.find_element(by='xpath',value=sat_xpth)
    sat_click.click()

    sleep(2)

    print("\nSelecting Station ....")
    data_xpath_value, datatype_keys_lst = pars_data_from_cnfg_file(config_dict["station"])
    for data_type_xpth in data_xpath_value:
        data_type = driver.find_element(by='xpath', value=data_type_xpth)
        data_type.click()
    sleep(2)

    print("\nSelecting Data Type ....")
    station_xpath_value, station_keys_lst = pars_data_from_cnfg_file(config_dict["data_type"])
    for station_xpth in station_xpath_value:
        station_check_box = driver.find_element(by='xpath', value=station_xpth)
        station_check_box.click()
    sleep(2)

    return sat_keys_lst, datatype_keys_lst, station_keys_lst

def check_data_in_order_search():
    search_btn = driver.find_element(by='xpath',value='//*[@value="Search"]')
    driver.execute_script("arguments[0].scrollIntoView();", search_btn)
    search_btn.click()
    sleep(5)
    try:
        search_results = driver.find_element(by='xpath',value='//span[@style="color:red"]')
        if 'Search generated 0 hits.' in search_results.text:
            print(search_results.text)

            return False
    except:
        print("Results Found ....")
        driver.back()
        sleep(5)
        return True

def get_ticket_order_no():
    ticket = driver.find_element(by='xpath',value='//table[@class="class_table center"]//tbody//tr//td')
    ticket_txt = ticket.text
    order_no = ticket_txt.split(': ')[1].split('.')[0]
    print("the order No. >>>>> ",order_no)
    return order_no



def place_order(comnt):

    place_order_btn = driver.find_element(by='xpath',value='//*[@value="Quick Search & Order"]')
    place_order_btn.click()
    sleep(5)

    cmnt = driver.find_element(by='name',value='order_comment')
    cmnt.send_keys(comnt)
    sleep(2)

    place_order_last = driver.find_element(by='xpath',value='//*[@value="PlaceOrder"]')
    place_order_last.click()
    print("Order Placed Successfully ....\n")
    sleep(5)
    order_no = get_ticket_order_no()

    return order_no


def order_info_tocsv(file_path,today_Date,order_no,sat_keys_lst, datatype_keys_lst, station_keys_lst,loc):
    data = [order_no, today_Date, sat_keys_lst, datatype_keys_lst, station_keys_lst, loc, "pending"]
    if (os.path.exists(file_path) and os.path.isfile(file_path)):
        df = pd.read_csv(file_path)
        df.loc[len(df)] = data
        df.to_csv(file_path,index=False)
    else:
        header = ["order_no", "run_script_date", "satelite_checked", "datatype_checked", "station_checked","location_on_map", "status"]
        df = pd.DataFrame(data, headers=header)
        print("No Order Info File Found ....")
        print("Creating Order Info File ....")
        df.to_csv(file_path,index=False)
    print("Order Info Saved ....")
    return df

if __name__ == "__main__":


    csv_file_path = 'order_info.csv'
    credentials_file = 'login_parameters.json'
    cnfig_file_name = "search_config_file.json"
    login_data = open_txt_file(credentials_file)
    login_url = login_data['login_url']
    order_url_data = open_txt_file(cnfig_file_name)
    username = login_data['username']
    password = login_data['password']
    if order_url_data['start_date'] == "None":
        end_date = str(datetime.datetime.today().strftime('%Y-%m-%d'))
        start_date = str((datetime.datetime.today() - datetime.timedelta(days = 1)).strftime('%Y-%m-%d'))
        today_Date = str(datetime.datetime.today().strftime('%Y-%m-%d'))
    else:
        start_date_formated = pd.to_datetime(order_url_data['start_date'])
        start_date = str(start_date_formated.strftime('%Y-%m-%d'))
        days_after = order_url_data['days_after']
        end_date = str((start_date_formated+(datetime.timedelta(days=days_after))).strftime('%Y-%m-%d'))
        today_Date = str(datetime.datetime.today().strftime('%Y-%m-%d'))

    driver = driver_setup('data')
    login(login_url, username, password, driver)

    print("Selecting Location On Map .... ")
    loc = map_point(cnfig_file_name)

    print("Selecting Order's Parameter ....")

    config_dict = open_txt_file(cnfig_file_name)

    sat_xpath_value, sat_keys_lst = pars_data_from_cnfg_file(config_dict["satellite"])
    for sat_xpth, sat_name in zip(sat_xpath_value, sat_keys_lst):

        sat_keys_lst, datatype_keys_lst, station_keys_lst = order_criteria(start_date, end_date, config_dict, sat_xpth)
        current_url = driver.current_url
        if check_data_in_order_search():
            print("Placing Order ....")
            order_no = place_order('ASAP')
            sleep(2)
            driver.get(current_url)
        else:
            order_no = 0
            print("No Results Found ....")

        sat_keys_lst, datatype_keys_lst, station_keys_lst = order_criteria(start_date, end_date, config_dict, sat_xpth)

        if order_no != 0:
            print("Order Info Saved Successfully ....")
            order_info_tocsv(csv_file_path, today_Date, order_no, sat_name, ','.join(map(str, datatype_keys_lst)),
                             ','.join(map(str, station_keys_lst)), loc)
        else:
            print("No order placed please Modify Search Criteria")










