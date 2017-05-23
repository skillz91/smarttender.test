import os
import unittest
import time
import core
from tools.webservice import WebService
from selenium import webdriver
from ddt import ddt, data, unpack
from tools.get_data import get_csv_data
from selenium.webdriver.support.select import Select
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

@ddt
class Registration(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.driver = core.driver.Driver.get_driver()

        def setUp(self):
            url = os.getenv("testUrl", "http://test.smarttender.biz")
            self.driver.get(url + "/registration?testMode=1")

        @data(*get_csv_data('./data/registration.csv'))
        @unpack
        def test_register(self, name, surname, phone, role, subject, unique_code,
                          country, norg, norgs, web, physical_address, inn, activity,
                          law_address, email, password, additional, file1, file2, categories):
            self.input_text_by_partial_name("NameTb", name)
            self.input_text_by_partial_name("SurnameTb", surname)
            self.input_text_by_partial_name("PhoneTb", phone)
            self.select_value("role-select", role)
            is_physical = role == "Buyer" and subject == "4"
            is_participant = role == "Part" or role == "Buyer"
            if is_participant:
                self.select_value("subject-select", subject)
            self.input_text_by_partial_name("OkpoTb", unique_code)
            if is_participant and subject == "3":
                self.select_value("koraiat-select", country)
            if subject != "4":
                self.input_textarea_by_partial_name("OrgInfo_NameTb", norg)
                self.input_text_by_partial_name("OrgInfo_ShortNameTb", norgs)
                self.input_text_by_partial_name("OrgInfo_WebSiteTb", web)
            if subject != "3":
                self.input_textarea_by_partial_name("OrgInfo_PhysicalAddress", physical_address)
                if subject != "4":
                    self.input_text_by_partial_name("OrgInfo_InnTb", inn)
            if is_participant and subject != "1" and subject != "4":
                self.input_textarea_by_partial_name("OrgInfo_LegalAddress", law_address)
            if subject != "4":
                self.input_text_by_partial_name("OrgInfo_ActivityTb", activity)
            self.input_text_by_partial_name("Contact_EmailTb", email)
            if is_participant:
                self.input_text_by_partial_name("Contact_PasswordTb", password)
                self.input_text_by_partial_name("Contact_RepeatPasswordTb", password)
            self.input_textarea_by_partial_name("AdditionalInfoTb", additional)
            self.check_checkbox("SecurityCheck", True)
            categories_list = []
            if role == "Part":
                self.check_checkbox("ProzorroWarningCheckBox", True)
            if is_participant:
                splited = categories.split(";")
                for category in splited:
                    cat = self.select_category(category)
                    categories_list.append(cat)

            if subject == "4":
                self.select_file(0)
                self.select_file(1)

            self.driver.find_element_by_xpath("//a[contains(@id, 'SubmitBtn')]").click()
            self.driver.find_element_by_xpath("//iframe[contains(@src,'_TENDER_REGISTRATION_INFO')]")
            itworg_row = WebService.execute("_UITEST.REGISTRATION.GET", {"email": email})[0]
            WebService.execute("_UITEST.REGISTRATION.DELETE", {"unworg": itworg_row["UNWORG"]})

            self.assertEqual(name, itworg_row["RUK_NAM"])
            self.assertEqual(surname, itworg_row["RUK_FAM"])
            self.assertEqual(phone, itworg_row["TEL"])
            self.assertEqual(subject, str(itworg_row["KUMTSDA"]))
            self.assertEqual(unique_code, itworg_row["OKPO"])
            if is_participant and subject == "3":
                self.assertEqual(country, itworg_row["KORAIAT"])
            if subject != "4":
                self.assertEqual(norg, itworg_row["NORG_DOC"])
                self.assertEqual(norgs, itworg_row["NORG_S"])
                self.assertEqual(web, itworg_row["URL"])
            if subject != "3":
                self.assertEqual(physical_address, itworg_row["ADR_FACT"])
                if subject != "4":
                    self.assertEqual(inn, itworg_row["INN"])
            if subject != "4":
                self.assertEqual(activity, itworg_row["VIDDEYAT"])
            if is_participant and subject != "1" and subject != "4":
                self.assertEqual(law_address, itworg_row["APOTR"])
            self.assertEqual(email, itworg_row["LOGIN_E"])
            self.assertEqual(additional, itworg_row["COMM"])
            if is_participant:
                self.assertCountEqual(categories_list, itworg_row["KWCATSTR"].split(","))
            # WebService.execute("_UITEST.REGISTRATION.DELETE", {"unworg": itworg_row["UNWORG"]})

        @classmethod
        def tearDownClass(cls):
            cls.driver.quit()

        def input_text_by_partial_name(self, partial_name, text):
            elem = self.driver.find_element_by_xpath("//input[contains(@id, '" + partial_name + "')]")
            elem.clear()
            elem.send_keys(text)

        def input_textarea_by_partial_name(self, partial_name, text):
            elem = self.driver.find_element_by_xpath("//textarea[contains(@id, '" + partial_name + "')]")
            elem.clear()
            elem.send_keys(text)

        def select_value(self, partial_class, value):
            elem = Select(self.driver.find_element_by_xpath("//select[contains(@class, '" + partial_class + "')]"))
            elem.select_by_value(value)

        def check_checkbox(self, partial_name, check):
            elem = self.driver.find_element_by_xpath("//input[contains(@id, '" + partial_name + "')]")
            if (check and not elem.is_selected()) or (not check and elem.is_selected()):
                elem.click()

        def select_category(self, category):
            sequence = category.split('-')
            for i in range(len(sequence) - 1):
                xpath = "//div[@id='tree']//li[@id='" + sequence[i] + "']"
                node = self.driver.find_element_by_xpath(xpath)
                is_expanded = node.get_attribute("aria-expanded") == "true"
                if not is_expanded:
                    self.driver.find_element_by_xpath(xpath + "//i[contains(@class, 'jstree-ocl')]").click()
                    time.sleep(1)
            xpath = "//div[@id='tree']//li[@id='" + sequence[len(sequence)-1] + "']"
            node = self.driver.find_element_by_xpath(xpath)
            if node.get_attribute("aria-selected") != "true":
                self.driver.find_element_by_xpath(xpath + "//i[contains(@class, 'jstree-checkbox')]").click()
            return sequence[len(sequence)-1]

        def select_file(self, index):
            file_name = "fakefile.txt"
            f = open(file_name, "w+")
            f.write("fake data")
            f.close()
            inp = self.driver.find_elements_by_xpath("//input[@type='file']")[index]
            inp.send_keys(os.getcwd() + "\\" + file_name)
            time.sleep(1)

if __name__ == '__main__':
    # scenario = unittest.TestLoader().loadTestsFromTestCase(Registration)
    # suite = unittest.TestSuite([scenario])
    # unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))
    # unittest.TextTestRunner(verbosity=2).run(suite)
    unittest.main()
