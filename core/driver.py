import os
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


class Driver:
    @staticmethod
    def get_driver():
        browser = os.getenv("browser", "")
        # if browser == "chrome":
        #     driver = webdriver.Chrome("c:\\smarttender.test\\chromedriver.exe")
        if browser == "firefox":
            binary = FirefoxBinary("C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe")
            driver = webdriver.Firefox(firefox_binary=binary)
        elif browser == "ie":
            driver = webdriver.Ie("c:\\smarttender.test\\IEDriverServer.exe")
        else:
            driver = webdriver.Chrome("c:\\smarttender.test\\chromedriver.exe")
        driver.implicitly_wait(30)
        driver.maximize_window()
        return driver