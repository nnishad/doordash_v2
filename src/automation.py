import concurrent.futures
import os

import configparser
import random
import threading
import time
import requests as requests

from src.doordash.signup import start_parent_signup, start_child_signup
from src.util.custom_logger import Logger
from src.util.http_client import HTTPClient
from src.util.webdriver_manager import WebDriverManager

# Read the configuration file
config = configparser.ConfigParser()
config.read('../config.ini')

# Determine the environment from the command-line argument
input_environment = os.environ.get('ENVIRONMENT', 'Local')

env = config[input_environment]


# @log_function_execution(CustomLogger("ChildAutomation"))
def child_automation(profile_uuid, referral_link, family_id, child_name, remote_url=None, logger=None):
    if not logger:
        logger = Logger()
    manager = WebDriverManager(threading.get_ident(), remote_url)
    driver = manager.get_driver()

    logger.info(f"Child log for {child_name} from family {family_id}")

    start_child_signup(env, driver, profile_uuid, referral_link, family_id, logger)
    # ...
    time.sleep(10)
    manager.close_driver()


# @log_function_execution(CustomLogger("FamilyAutomation"))
def family_automation(parent_name, profile_uuid, remote_url=None, logger=None):
    if not logger:
        logger = Logger()

    manager = WebDriverManager(threading.get_ident(), remote_url)
    driver = manager.get_driver()

    logger.info(f"Parent log for {parent_name}")

    referral_link, family_id = start_parent_signup(env, driver, profile_uuid, logger)
    try:
        manager.close_driver()
    except:
        logger.error("Error while closing session")

    HTTPClient("http://127.0.0.1:35000") \
        .get(endpoint="api/v1/profile/stop", params={"profileId": profile_uuid})

    logger.info(family_id)

    # family_id="64c65e22c8dc8aef1a7962ed"
    # referral_link="https://drd.sh/EKra12d5Snk6Qjba"
    # Execute child tasks in parallel using ThreadPoolExecutor
    num_children = random.randint(1, 5)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        child_tasks = []
        for j in range(num_children):
            child_name = f"{parent_name}_Child_{j + 1}"
            try:
                response = HTTPClient("http://localhost:3001").post(endpoint="profile/create")
                if response.status_code in [200, 201]:
                    profile_response_data = response.json()
                    profile_uuid = profile_response_data['profile']['uuid']
                    logger.info(profile_response_data['profile']['uuid'])
                    logger.info("Response data:" + profile_response_data['profile']['uuid'])
                    json_response = HTTPClient("http://127.0.0.1:35000/api/v1/profile/start") \
                        .get(endpoint="",
                             params={"automation": True, "profileId": profile_response_data['profile']['uuid']})
                    logger.info(json_response.json())
                    child_remote_url = json_response.json()['value']
                else:
                    logger.info("Request failed with status code:" + response.status_code)

            except requests.exceptions.RequestException as e:
                logger.info(e)
            child_task = executor.submit(child_automation, profile_uuid, referral_link, family_id, child_name,
                                         child_remote_url, logger)
            child_tasks.append(child_task)

        # Wait for all child tasks to complete
        concurrent.futures.wait(child_tasks)
