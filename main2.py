import threading

from src.util.webdriver_manager import WebDriverManager


def run_test(thread_id):
    manager = WebDriverManager()
    driver = manager.get_driver()

    # Your test or automation code using the 'driver' instance

    # manager.close_driver()

# Create multiple threads to run tests
threads = []
for i in range(15):
    thread = threading.Thread(target=run_test, args=(i,))
    threads.append(thread)
    thread.start()

# Wait for all threads to finish
for thread in threads:
    thread.join()
