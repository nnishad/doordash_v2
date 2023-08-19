import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from src.util.custom_logger import Logger
from src.util.utility import fetch_otp_details, get_user_information, get_random_canadian_city, verify_phone, \
    get_referral_link, \
    save_parent_account, save_child_account, retry, retry_on_exception

max_retries = 2
sleep_time = 5  # Seconds


# @retry(max_retries, sleep_time)
def step_signup(driver, user, logger):
    try:
        driver.get("https://www.doordash.com/food-delivery/")

        time.sleep(4)

        driver.get("https://doordash.com/")

        time.sleep(5)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(10)

        try:
            acceptAllButton = driver.find_element(By.XPATH, "//button[@id='cassie_accept_all_pre_banner']")
            acceptAllButton.click()
        except:
            logger.info("Cookieee popup not found!")

        signUpButton = driver.find_element(By.XPATH, '//span[text()="Sign Up"]')
        signUpButton.click()

        time.sleep(5)
        # Wait until the element is present
        iframe = driver.find_element(By.XPATH, "//iframe[@title='Login/Signup']")
        driver.switch_to.frame(iframe)
        inputFirstName = driver.find_element(By.XPATH, "//input[@data-anchor-id='IdentitySignupFirstNameField']")
        for char in user['firstName']:
            inputFirstName.send_keys(char)
            time.sleep(0.5)
        time.sleep(0.3)
        inputLastName = driver.find_element(By.XPATH, "//input[@data-anchor-id='IdentitySignupLastNameField']")
        for char in user['lastName']:
            inputLastName.send_keys(char)
            time.sleep(0.5)
        time.sleep(0.3)

        inputEmail = driver.find_element(By.XPATH, "//input[@data-anchor-id='IdentitySignupEmailField']")
        time.sleep(0.3)
        for char in user['email']:
            inputEmail.send_keys(char)
            time.sleep(0.5)
        time.sleep(0.5)
        inputPhone = driver.find_element(By.XPATH, "//input[@data-anchor-id='IdentitySignupPhoneField']")
        time.sleep(0.3)
        for char in user['phone']:
            inputPhone.send_keys(char)
            time.sleep(0.5)
        time.sleep(0.5)
        inputPassword = driver.find_element(By.XPATH, "//input[@data-anchor-id='IdentitySignupPasswordField']")
        for char in user['password']:
            inputPassword.send_keys(char)
            time.sleep(0.5)

        time.sleep(0.7)

        if driver.find_element(By.XPATH,"//[text()='Error']"):
            raise RuntimeError("Error with form data")

        signupButton = driver.find_element(By.XPATH, '//span[text()="Sign Up"]')
        signupButton.click()
        time.sleep(4)

        driver.switch_to.default_content()

        time.sleep(15)

        driver.get("https://www.doordash.com/restaurants-near-me/")

        time.sleep(5)

        delivery_city = driver.find_element(By.XPATH, '//input[@aria-controls="addressAutocompleteDropdown"]')
        for char in get_random_canadian_city():
            delivery_city.send_keys(char)
            time.sleep(0.5)

        time.sleep(5)

        delivery_city.send_keys(Keys.ENTER)

        time.sleep(10)
    except Exception as e:
        raise RuntimeError("Failed to complete signup")


# @retry(max_retries, sleep_time)
def step_verify_phone(driver, user, env, logger):
    driver.get("https://www.doordash.com/")
    time.sleep(3)
    try:
        driver.find_element(By.XPATH,"//*[@data-anchor-id='AnnouncementDismissButton']").click()
    except:
        logger.info("Announcement not found")

    time.sleep(5)
    try:
        driver.find_elements(By.XPATH, "//span[text()='Skip']")[0].click()
    except:
        logger.info("Suggestion Popup not found 1")
        try:
            driver.find_elements(By.XPATH, "//span[text()='Skip']")[1].click()
        except:
            logger.info("Suggestion Popup not found 1")

    try:
        signInButton = driver.find_element(By.XPATH, '//span[text()="Sign In"]')
        signInButton.click()
    except:
        logger.info("signIn button not found")

    time.sleep(20)
    try:
        verify_phone(env, driver, logger, user)
    except Exception as e:
        raise RuntimeError("Error occurred while phone verification.")


# @retry(max_retries, sleep_time)
def step_get_referral_link(driver, user, logger):
    try:
        referral_link = get_referral_link(driver, logger)

        logger.info(referral_link)

        user['referralLink'] = referral_link

        family_id = save_parent_account(user, logger)

        return referral_link, family_id
    except Exception as e:
        raise RuntimeError("Error while getting referral link")


def start_parent_signup(env, driver: webdriver, profile_uuid, logger: Logger):
    user = get_user_information(profile_uuid, environment=env, logger=logger)

    steps_to_execute = [
        (step_signup, [driver, user, logger], {}),
        (step_verify_phone, [driver, user, env, logger], {}),
        (step_get_referral_link, [driver, user, logger], {})
    ]
    try:
        results = retry_on_exception(max_retries, sleep_time, steps_to_execute)
        print(results)
    except Exception as e:
        logger.info(e)
    time.sleep(10)
    #
    # return referral_link, family_id


def start_child_signup(env, driver: webdriver, profile_uuid, referral_link, family_id, logger: Logger):
    driver.get(referral_link)

    time.sleep(4)

    try:
        acceptAllButton = driver.find_element(By.XPATH, "//button[@id='cassie_accept_all_pre_banner']")
        acceptAllButton.click()
    except:
        logger.info("Cookieee popup not found!")

    user = get_user_information(profile_uuid, environment=env, logger=logger)

    time.sleep(20)
    try:
        inputFirstName = driver.find_element(By.XPATH, "//input[@data-anchor-id='IdentitySignupFirstNameField']")
        for char in user['firstName']:
            inputFirstName.send_keys(char)
            time.sleep(0.5)
        time.sleep(0.3)
        inputLastName = driver.find_element(By.XPATH, "//input[@data-anchor-id='IdentitySignupLastNameField']")
        for char in user['lastName']:
            inputLastName.send_keys(char)
            time.sleep(0.5)
        time.sleep(0.3)

        inputEmail = driver.find_element(By.XPATH, "//input[@data-anchor-id='IdentitySignupEmailField']")
        time.sleep(0.3)
        for char in user['email']:
            inputEmail.send_keys(char)
            time.sleep(0.5)
        time.sleep(0.5)
        inputPhone = driver.find_element(By.XPATH, "//input[@data-anchor-id='IdentitySignupPhoneField']")
        time.sleep(0.3)
        for char in user['phone']:
            inputPhone.send_keys(char)
            time.sleep(0.5)
        time.sleep(0.5)
        inputPassword = driver.find_element(By.XPATH, "//input[@data-anchor-id='IdentitySignupPasswordField']")
        for char in user['password']:
            inputPassword.send_keys(char)
            time.sleep(0.5)
    except:
        logger.info("Error while inputting signup form values")

    time.sleep(0.7)
    signupButton = driver.find_element(By.XPATH, '//span[text()="Sign Up"]')
    signupButton.click()
    time.sleep(15)

    status, otp_message = fetch_otp_details(env, logger, user)
    otp_input = driver.find_element(By.XPATH, "//input[@type='number']")

    if status == 3:
        for char in otp_message:
            otp_input.send_keys(char)
            time.sleep(0.5)
    else:
        logger.info(f"SMS API returned status: {status}")
        time.sleep(0.5)

    otp_submit_btn = driver.find_element(By.XPATH, "//span[text() = 'Submit']")
    otp_submit_btn.click()

    time.sleep(15)

    driver.get("https://www.doordash.com/restaurants-near-me/")

    time.sleep(5)

    delivery_city = driver.find_element(By.XPATH, '//input[@aria-controls="addressAutocompleteDropdown"]')
    for char in get_random_canadian_city():
        delivery_city.send_keys(char)
        time.sleep(0.5)

    time.sleep(5)

    # find_restro_btn = driver.find_element(By.XPATH, "//button[@aria-label='Find Restaurants']")
    # find_restro_btn.click()

    delivery_city.send_keys(Keys.ENTER)

    time.sleep(15)

    try:
        driver.find_elements(By.XPATH, "//span[text()='Skip']")[0].click()
    except:
        logger.info("Suggestion Popup not found 1")
        try:
            driver.find_elements(By.XPATH, "//span[text()='Skip']")[1].click()
        except:
            logger.info("Suggestion Popup not found 1")
    try:
        signInButton = driver.find_element(By.XPATH, '//span[text()="Sign In"]')
        signInButton.click()
    except:
        logger.info("signIn button not found")

    time.sleep(20)

    referral_link = get_referral_link(driver, logger)

    logger.info(referral_link)

    user['referralLink'] = referral_link

    save_child_account(user, family_id, logger)

    return referral_link
