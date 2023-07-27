import concurrent.futures
import threading
import queue

import requests as requests

from src.automation import family_automation
from src.util.custom_logger import Logger
from src.util.http_client import HTTPClient

# Usage examples
if __name__ == "__main__":
    # Get the number of families from the user
    # num_families = int(input("Enter the number of families: "))
    num_families = 1

    # Create threads for family automation
    family_threads = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
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
                    json_response = HTTPClient("http://127.0.0.1:35000/api/v1/profile") \
                        .get(f"start?automation=true&profileId={profile_response_data['profile']['uuid']}")
                    parent_remote_url = json_response['value']
                else:
                    logger.info("Request failed with status code:" + response.status_code)

            except requests.exceptions.RequestException as e:
                logger.info("Request error:")

            thread = executor.submit(family_automation, parent_name,profile_uuid, parent_remote_url,  logger)
            family_threads.append(thread)

    # Wait for all family threads to finish
    concurrent.futures.wait(family_threads)
