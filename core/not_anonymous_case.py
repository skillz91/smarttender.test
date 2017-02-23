import unittest
import time
from core.driver import Driver


class NonAnonymousCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = Driver.get_driver()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def login(self, login, password):
        self.driver.get("http://test.smarttender.biz/")
        self.driver.find_element_by_id("LoginAnchor").click()
        time.sleep(0.2)
        logins = self.driver.find_elements_by_class_name("login-tb")
        logins[1].send_keys(login)
        passwords = self.driver.find_elements_by_class_name("password-tb")
        passwords[1].send_keys(password)
        btns = self.driver.find_elements_by_id("LoginBlock_LogInBtn")
        btns[1].click()

    def logout(self):
        self.driver.get("http://test.smarttender.biz/")
        logout = self.driver.find_elements_by_id("LogoutBtn")
        if len(logout) > 0:
            logout[0].click()