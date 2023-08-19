import concurrent.futures
import os

import configparser

import requests
import time

from src.automation import family_automation
from src.util.custom_logger import Logger
from src.util.http_client import HTTPClient
from src.util.utility import retry_api_call


# Read the configuration file
config = configparser.ConfigParser()
config.read('../config.ini')

# Determine the environment from the command-line argument
input_environment = os.environ.get('ENVIRONMENT', 'Local')
env = config[input_environment]


# Usage examples
if __name__ == "__main__":
    # Get the number of families from the user
    num_families = 1
    max_retries = 3

    # Create a ThreadPoolExecutor with the desired number of threads
    with concurrent.futures.ThreadPoolExecutor() as executor:
        family_threads = []

        for i in range(num_families):
            parent_name = f"Parent_{i + 1}"
            logger = Logger()
            parent_remote_url = None

            try:
                response = HTTPClient("http://localhost:3001").post(endpoint="profile/create")

                if response.status_code in [200, 201]:
                    profile_response_data = response.json()
                    profile_uuid = profile_response_data['profile']['uuid']
                    logger.info(profile_response_data['profile']['uuid'])
                    logger.info("Response data:" + profile_response_data['profile']['uuid'])
                    retry_count = 0

                    response = retry_api_call(lambda: HTTPClient(env['multilogin_server'])
                                              .get(endpoint="api/v1/profile/start",
                                                   params={"automation": True,
                                                           "profileId": profile_response_data['profile']['uuid']}),
                                              logger)
                    parent_remote_url = response.json()['value']

                    # while retry_count <= max_retries:
                    #     try:
                    #         json_response = HTTPClient("http://127.0.0.1:35000/api/v1/profile/start") \
                    #             .get(endpoint="",
                    #                  params={"automation": True, "profileId": profile_response_data['profile']['uuid']})
                    #         if json_response.status_code == 500:
                    #             # Retry after waiting for some time (e.g., 5 seconds)
                    #             time.sleep(60)
                    #             retry_count += 1
                    #         else:
                    #             parent_remote_url = json_response.json()['value']
                    #             break
                    #     except requests.exceptions.RequestException as e:
                    #         logger.info("Request error:")

                else:
                    logger.info("Request failed with status code:" + response.status_code)

            except requests.exceptions.RequestException as e:
                logger.info(e)

            # Use executor.submit to execute family_automation in a separate thread
            future = executor.submit(family_automation, parent_name, "profile_uuid", parent_remote_url, logger)
            family_threads.append(future)

        # Wait for all threads to complete using as_completed
        for future in concurrent.futures.as_completed(family_threads):
            # Retrieve the result of the completed thread (if needed)
            result = future.result()
            logger.info("Thread completed with result: " + str(result))
