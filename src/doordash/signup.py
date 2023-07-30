import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from src.util.custom_logger import Logger
from src.util.utility import get_user_information, get_random_canadian_city, verify_phone, get_referral_link, \
    save_parent_account, save_child_account


def start_parent_signup(env, driver: webdriver,profile_uuid, logger: Logger):
    driver.get("https://www.doordash.com/food-delivery/")

    time.sleep(4)

    driver.get("https://www.doordash.com/search/store/restaurants/")

    time.sleep(5)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    time.sleep(4)

    try:
        acceptAllButton = driver.find_element(By.XPATH, "//button[@id='cassie_accept_all_pre_banner']")
        acceptAllButton.click()
    except:
        logger.info("Cookieee popup not found!")

    try:
        signUpButton = driver.find_element(By.XPATH, '//span[text()="Sign Up"]')
        signUpButton.click()
    except:
        logger.info("signup button not found")
    time.sleep(5)
    # Wait until the element is present
    iframe = driver.find_element(By.XPATH, "//iframe[@title='Login/Signup']")
    driver.switch_to.frame(iframe)
    user = get_user_information(profile_uuid, environment=env,logger=logger)
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

    # find_restro_btn = driver.find_element(By.XPATH, "//button[@aria-label='Find Restaurants']")
    # find_restro_btn.click()

    delivery_city.send_keys(Keys.ENTER)


    time.sleep(15)

    try:
        driver.find_elements(By.XPATH,"//span[text()='Skip']")[0].click()
    except:
        logger.info("Suggestion Popup not found 1")
        try:
            driver.find_elements(By.XPATH,"//span[text()='Skip']")[1].click()
        except:
            logger.info("Suggestion Popup not found 1")

    try:
            signInButton = driver.find_element(By.XPATH, '//span[text()="Sign In"]')
            signInButton.click()
    except:
        logger.info("signIn button not found")

    time.sleep(20)

    verify_phone(env, driver, logger, user)

    time.sleep(10)

    referral_link = get_referral_link(driver,logger)

    logger.info(referral_link)

    user['referralLink'] = referral_link

    family_id = save_parent_account(user,logger)

    return referral_link, family_id


def start_child_signup(env, driver:webdriver, profile_uuid, referral_link, family_id,  logger:Logger):
    driver.get(referral_link)

    time.sleep(4)

    try:
        acceptAllButton = driver.find_element(By.XPATH, "//button[@id='cassie_accept_all_pre_banner']")
        acceptAllButton.click()
    except:
        logger.info("Cookieee popup not found!")

    user = get_user_information(profile_uuid, environment=env,logger=logger)
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
    time.sleep(4)

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
        driver.find_elements(By.XPATH,"//span[text()='Skip']")[0].click()
    except:
        logger.info("Suggestion Popup not found 1")
        try:
            driver.find_elements(By.XPATH,"//span[text()='Skip']")[1].click()
        except:
            logger.info("Suggestion Popup not found 1")
    try:
        signInButton = driver.find_element(By.XPATH, '//span[text()="Sign In"]')
        signInButton.click()
    except:
        logger.info("signIn button not found")

    time.sleep(20)

    verify_phone(env, driver, logger, user)

    time.sleep(10)

    referral_link = get_referral_link(driver,logger)

    logger.info(referral_link)

    user['referralLink'] = referral_link

    save_child_account(user,family_id,logger)

    return referral_link
