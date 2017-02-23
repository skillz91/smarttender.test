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
    def setUp(self):
        self.login("bened@it.ua", "111111")
        WebService.execute("_UITEST.ORG.RESIDENT", {"login": "bened@it.ua"})

    def tearDown(self):
        WebService.execute("_UITEST.ORG.RESIDENT", {"login": "bened@it.ua"})
        self.logout()

    @data(*get_csv_data('./data/form_invoice.csv'))
    @unpack
    def test_invoice(self, resident, sum, ua_agency, ua_account):
        if resident == "1":
            WebService.execute("_UITEST.ORG.NONRESIDENT", {"login": "bened@it.ua"})
        self.driver.find_element_by_link_text(u"Особистий кабінет").click()
        self.driver.find_element_by_xpath("//a[contains(@onclick, '_TENDERFORMINVOICE')]").click()
        time.sleep(2)
        self.driver.switch_to.frame(self.driver.find_element_by_id("widget"))
        if resident == "1":
            if ua_agency == "1":
                self.driver.find_element_by_id("haveUahAgency").click()
            if ua_account == "1":
                self.driver.find_element_by_id("haveUahAccount").click()
        time.sleep(1)
        if (resident == "1" and ua_account == "1" and ua_agency == "1") or resident == "0":
            self.driver.find_element_by_id("uahAmount").send_keys(sum)
        else:
            self.driver.find_element_by_id("currencyamount").send_keys(sum)
            time.sleep(2)
        self.driver.find_element_by_id("submit").click()
        WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, 'formInvoice')))
        link = self.driver.find_element_by_id('formInvoice')
        href = link.get_attribute("href")
        h = httplib2.Http()
        resp, content = h.request(href)
        self.assertEqual(resp.status, 200)
