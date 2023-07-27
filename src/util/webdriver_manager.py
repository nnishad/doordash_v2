import threading
from selenium import webdriver


class WebDriverManager:
    _lock = threading.Lock()
    _webdrivers = {}

    def __new__(cls, thread_id, remote_url=None):
        with cls._lock:
            if thread_id not in cls._webdrivers:
                cls._webdrivers[thread_id] = super().__new__(cls)
        return cls._webdrivers[thread_id]

    def __init__(self, thread_id, remote_url=None):
        self.driver = None
        self.thread_id = thread_id
        self.remote_url = remote_url
        self.lock = threading.Lock()

    def get_driver(self):
        with self.lock:
            if not self.driver:
                if self.remote_url:
                    self.driver = webdriver.Remote(self.remote_url,
                                                   desired_capabilities=webdriver.DesiredCapabilities.CHROME)
                else:
                    chrome_options = webdriver.ChromeOptions()
                    chrome_executable_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
                    chrome_options.binary_location = chrome_executable_path
                    chrome_profile_path = '/Users/nnishad/Library/Application Support/Google/Chrome/NikhilInstaProfile'
                    chrome_options.add_argument(f'--user-data-dir={chrome_profile_path}')
                    # disable the AutomationControlled feature of Blink rendering engine
                    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                    chrome_options.add_argument('--no-sandbox')
                    chrome_options.add_argument('--disable-dev-shm-usage')
                    self.driver = webdriver.Chrome(executable_path='/Users/nnishad/PythonProjects/doordash_v2/src/chromedriver/chromedriver',
                                                   chrome_options=chrome_options)
        return self.driver

    def close_driver(self):
        with self.lock:
            if self.driver:
                self.driver.quit()
                self.driver = None
