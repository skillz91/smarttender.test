import time

import httplib2
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ddt import ddt, data, unpack
from tools.get_data import get_csv_data
from core.not_anonymous_case import NonAnonymousCase
from tools.webservice import WebService


@ddt
class FormInvoiceTest(NonAnonymousCase):
    def tearDown(self):
        self.logout()

    @data(*get_csv_data('./data/form_invoice.csv'))
    @unpack
    def test_invoice(self, login, password, resident, sum, ua_agency, ua_account):
        self.login(login, password)
        self.driver.find_element_by_link_text(u"Особистий кабінет").click()
        self.driver.find_element_by_xpath("//a[contains(@onclick, '_TENDERFORMINVOICE')]").click()
        time.sleep(2)
        self.driver.switch_to.frame(self.driver.find_element_by_id("widget"))
        if resident == "1":
            if ua_agency == "1":
                self.driver.find_element_by_xpath("//label[@for='haveUahAgency']").click()
            if ua_account == "1":
                self.driver.find_element_by_xpath("//label[@for='haveUahAccount']").click()
        time.sleep(1)
        if (resident == "1" and ua_account == "1" and ua_agency == "1") or resident == "0":
            self.driver.find_element_by_id("uahAmount").send_keys(sum)
        else:
            self.driver.find_element_by_id("currencyamount").send_keys(sum)
            self.driver.find_element_by_id("uahAmount").click()
            time.sleep(1)
        self.driver.find_element_by_id("submit").click()
        WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, 'formInvoice')))
        link = self.driver.find_element_by_id('formInvoice')
        href = link.get_attribute("href")
        h = httplib2.Http()
        resp, content = h.request(href)
        self.assertEqual(resp.status, 200)
