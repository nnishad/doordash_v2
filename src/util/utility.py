import random
import string
import time

from faker import Faker
from random_address import random_address
from selenium.webdriver.common.by import By

from src.constant import sms_pool_services
from src.constant.cities import CANADIAN_CITIES
from src.util.custom_logger import Logger
from src.util.http_client import HTTPClient

import requests

fake = Faker(['en_US'])


def make_email_unique(email):
    username, domain = email.split('@', 1)
    random_string = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))
    return f"{username}_{random_string}@{domain}"


def get_random_canadian_city():
    return random.choice(CANADIAN_CITIES)


def generate_us_city_address(city):
    return random_address.real_random_address_by_state('CA')


def get_user_information(profile_uuid, environment, logger: Logger):
    # Get the necessary data
    country_id = '1'
    profile = fake.profile()
    user = {
        'firstName': profile['name'].split(" ")[0],
        'lastName': profile['name'].split(" ")[1],
        'email': make_email_unique(profile['mail']),
        'password': Faker().password(length=12),
        'name': profile['name'],
        'address': generate_us_city_address(""),
        "multiLoginProfileId": profile_uuid
    }

    for element in sms_pool_services.ServiceList().get_services():
        if element.name == 'United States':
            country_id = element.id

    service_id = '280'  # Doordash
    response = HTTPClient(environment['sms_pool_purchase_api']) \
        .get(endpoint="",
             params={"key": environment['key'], "country": country_id, "service": service_id})

    if response.status_code in [200, 201]:
        sms_pool_response_data = response.json()
        phoneNumber = sms_pool_response_data['phonenumber']
        orderId = sms_pool_response_data['order_id']
        country = sms_pool_response_data['country']
        success = sms_pool_response_data['success']
        countryCode = sms_pool_response_data['cc']
        message = sms_pool_response_data['message']

        user['phone'] = str(phoneNumber)
        user['smsPoolOrderId'] = orderId
        return user
    else:
        logger.info("Request failed with status code:" + response.status_code)
        return None


def process_response(response, logger: Logger):
    if "status" in response and "message" in response:
        logger.info(response)
        status = response["status"]
        switch_cases = {
            1: "pending",
            2: "expired",
            4: "resend",
            5: "cancelled",
            6: "refunded"
        }
        message = switch_cases.get(status, "")
        return status, message
    elif "success" in response and response["success"] == 0:
        return response["success"], response["message"]
    elif "status" in response and "sms" in response:
        return response["status"], response["sms"]


def fetch_otp_details(environment, logger: Logger, user):
    global message
    api_status = 1
    while api_status not in [0, 2, 3, 4, 5, 6]:
        try:
            time.sleep(60)
            response = HTTPClient(environment['sms_pool_fetch_api']) \
                .get(endpoint="", params={"orderid": user['smsPoolOrderId'], "key": environment['key']})
            logger.info(response)
            if response.status_code == 200:
                json_data = response.json()
                api_status, message = process_response(json_data, logger)
                logger.info(str(api_status) + " " + message)
                time.sleep(4)
            else:
                logger.info(response)
                logger.info('API status:' + str(response.status_code))
                break
        except Exception as e:
            logger.info('An error occurred while checking API status:' + str(e))
    logger.info('[Status of the API is] ' + str(api_status))
    return api_status, message


def verify_phone(environment, driver, logger: Logger, user):
    open_menu = driver.find_element(By.XPATH, "//button[@aria-label='Open Menu']")
    open_menu.click()
    time.sleep(8)

    account_btn = driver.find_element(By.XPATH, "//span[text() = 'Account']")
    account_btn.click()

    time.sleep(10)
    verify_btn = driver.find_element(By.XPATH, "//span[text() = 'Verify']")
    verify_btn.click()
    time.sleep(11)

    otp_input = driver.find_element(By.XPATH, "//input[@type='number']")

    status, otp_message = fetch_otp_details(environment, logger, user)
    if status == 3:
        for char in otp_message:
            otp_input.send_keys(char)
            time.sleep(0.5)
    else:
        logger.info(f"SMS API returned status: {status}")
    time.sleep(0.5)

    otp_submit_btn = driver.find_element(By.XPATH, "//span[text() = 'Submit']")
    otp_submit_btn.click()


def get_referral_link(driver, logger: Logger):
    try:
        open_menu = driver.find_element(By.XPATH, "//button[@aria-label='Open Menu']")
        open_menu.click()
        time.sleep(8)

        menu_referral_link = driver.find_element(By.XPATH, "//span[contains(text(), 'Get ') and contains(text(), "
                                                           "' in Credits')]")
        menu_referral_link.click()
        time.sleep(15)

        referral_link_elm = driver.find_element(By.XPATH, "//input[@aria-label='Share Your Link']")
        referral_link = referral_link_elm.get_attribute("value")
        logger.info(referral_link)
        time.sleep(5)
        return referral_link

    except:
        logger.info("Error while getting referral link")


def save_parent_account(user, logger: Logger):
    logger.info(user)
    response = HTTPClient("http://localhost:3001").post("family/create", json=user)
    if response.status_code == 201:
        json_response = response.json()
        logger.info(json_response)
        return json_response['family']['_id']
    else:
        logger.info(response)
        return None


def save_child_account(user, family_id, logger: Logger):
    logger.info(user)
    response = HTTPClient("http://localhost:3001").post(f"family/update/{family_id}/children", json=user)
    if response.status_code == 201:
        json_response = response.json()
        logger.info(json_response)
    else:
        logger.info(response)
        return None


def retry_api_call(api_func, logger: Logger, max_retries=3, retry_delay=5):
    for retry_count in range(max_retries + 1):
        try:
            response = api_func()
            if response.status_code == 200:
                return response
            else:
                logger.info(f"API call failed with status code: {response.status_code}. Retrying...")
                time.sleep(retry_delay)
        except requests.exceptions.RequestException as e:
            logger.info(f"Request error: {e}")
            time.sleep(retry_delay)
    return None


def retry(max_retries, sleep_time):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Exception occurred in {func.__name__}: {e}")
                    print(f"Retrying {func.__name__} in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                    retries += 1
            else:
                print(f"Max retries reached for {func.__name__}.")

        return wrapper

    return decorator


def retry_on_exception(max_retries, sleep_time, steps):
    results = []
    for step_info in steps:
        step_func, args, kwargs = step_info

        retries = 0
        while retries < max_retries:
            try:
                result = step_func(*args, **kwargs)
                results.append(result)  # Collect the result
                break  # Exit the loop if step is successful
            except Exception as e:
                print(f"Exception occurred in step {step_func.__name__}: {e}")
                print(f"Retrying step {step_func.__name__} in {sleep_time} seconds...")
                time.sleep(sleep_time)
                retries += 1
        else:
            print(f"Max retries reached for step {step_func.__name__}.")
            raise Exception(f"Failed to complete step {step_func.__name__} after {max_retries} retries.")

    return results  # Return the list of results

