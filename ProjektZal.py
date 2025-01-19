import unittest
import os
import time
import glob
import PyPDF2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

test_data = {
    "user": {
        "name": "Tomek",
        "new_name": "Marek",
        "last_name": "Nowak",
        "new_last_name": "Kowalski",
        "email": "Nowy2322@wp.pl",
        "new_email": "Kowal1231@wp.pl",
        "friends_mail": "testmail22@o2.pl",
        "password": "zaq12wsx",
        "gender": "male"
    },
    "address": {
        "country": "Poland",
        "city": "Warsaw",
        "street": "Kwiatowa 2",
        "post_code": "00-202",
        "phone_number": "111 222 333"
    },
    "product_search": {
        "query": "laptop",
    }
}


class Complete_tests(unittest.TestCase):

    def setUp(self):
        project_dir = os.path.dirname(os.path.abspath(__file__))
        self.download_dir = os.path.join(project_dir, "downloads")

        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

        chrome_options = Options()
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": False
        })

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get("https://demowebshop.tricentis.com")
        self.driver.maximize_window()
        self.driver.implicitly_wait(5)

    def tearDown(self):
        self.driver.quit()

    def wait_for_download(self, directory, pattern="*"):
        for _ in range(10):
            files = glob.glob(f"{directory}/{pattern}")
            if files:
                return files[0]
            time.sleep(1)
        return None

    def extract_text_from_pdf(self, pdf_path):
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text

    def login(self, email, password):
        self.driver.find_element(By.XPATH, "//*[@class='ico-login']").click()
        self.driver.find_element(By.ID, "Email").send_keys(email)
        self.driver.find_element(By.ID, "Password").send_keys(password)
        self.driver.find_element(By.XPATH, "//input[@value='Log in']").click()

    def send_product_email(self, friend_email):
        self.driver.find_element(By.LINK_TEXT, "Computers").click()
        self.driver.find_element(By.LINK_TEXT, "Desktops").click()
        self.driver.find_element(By.XPATH, "//a[@href='/build-your-own-expensive-computer-2']").click()
        self.driver.find_element(By.ID, "product_attribute_74_5_26_82").click()
        self.driver.find_element(By.ID, "product_attribute_74_6_27_85").click()
        self.driver.find_element(By.ID, "product_attribute_74_3_28_87").click()
        self.driver.find_element(By.ID, "product_attribute_74_8_29_90").click()
        self.driver.find_element(By.XPATH, "//input[@value='Email a friend']").click()
        self.driver.find_element(By.ID, "FriendEmail").send_keys(friend_email)

    # Test 1: Rejestracja użytkownika
    def test_001_user_registration(self):
        driver = self.driver
        user_data = test_data["user"]
        driver.find_element(By.LINK_TEXT, "Register").click()
        if user_data["gender"] == "female":
            driver.find_element(By.ID, "gender-female").click()
        else:
            driver.find_element(By.ID, "gender-male").click()
        driver.find_element(By.ID, "FirstName").send_keys(user_data["name"])
        driver.find_element(By.ID, "LastName").send_keys(user_data["last_name"])
        driver.find_element(By.ID, "Email").send_keys(user_data["email"])
        driver.find_element(By.ID, "Password").send_keys(user_data["password"])
        driver.find_element(By.ID, "ConfirmPassword").send_keys(user_data["password"])
        driver.find_element(By.ID, "register-button").click()

        success_message = driver.find_element(By.CLASS_NAME, "result").text
        self.assertIn("Your registration completed", success_message)

    # Test 2: Logowanie i wylogowanie użytkownika
    def test_002_user_login_logout(self):
        driver = self.driver
        user_data = test_data["user"]
        self.login(user_data["email"], user_data["password"])
        logout_link = driver.find_element(By.LINK_TEXT, "Log out")
        self.assertTrue(logout_link.is_displayed())
        logout_link.click()
        self.assertIn("Log in", driver.page_source)

    # Test 3: Wyszukiwanie produktu
    def test_003_search_product(self):
        driver = self.driver
        search_box = driver.find_element(By.ID, "small-searchterms")
        search_box.send_keys("laptop")
        search_box.submit()
        results = driver.find_elements(By.CLASS_NAME, "product-item")
        self.assertGreater(len(results), 0)

    # Test 4: Dodanie kilku produktów do koszyka
    def test_004_add_multiple_products_to_cart(self):
        driver = self.driver
        driver.find_element(By.LINK_TEXT, "Books").click()
        driver.find_element(By.XPATH, "//input[@class='button-2 product-box-add-to-cart-button']").click()
        driver.find_element(By.LINK_TEXT, "Computers").click()
        driver.find_element(By.LINK_TEXT, "Notebooks").click()
        driver.find_element(By.XPATH, "//input[@class='button-2 product-box-add-to-cart-button']").click()
        driver.find_element(By.LINK_TEXT, "Shopping cart").click()
        cart_items = driver.find_elements(By.CLASS_NAME, "cart-item-row")
        self.assertGreaterEqual(len(cart_items), 2,)

    # Test 5: Zamówienie bez zaakceptowania regulaminu
    def test_005_order_without_accepted_terms(self):
        driver = self.driver
        driver.find_element(By.LINK_TEXT, "Books").click()
        driver.find_element(By.XPATH, "//input[@class='button-2 product-box-add-to-cart-button']").click()
        driver.find_element(By.LINK_TEXT, "Shopping cart").click()
        driver.find_element(By.ID, "checkout").click()
        error_message = driver.find_element(By.XPATH, "//div[@id='terms-of-service-warning-box']/p").text
        self.assertEqual("Please accept the terms of service before the next step.", error_message)

    # Test 6: Zarządzanie adresem dostawy
    def test_006_manage_shipping_address(self):
        driver = self.driver
        user_data = test_data["user"]
        address_data = test_data["address"]
        self.login(user_data["email"], user_data["password"])
        driver.find_element(By.XPATH, "//*[@href='/customer/info']").click()
        driver.find_element(By.XPATH, "//*[@href='/customer/addresses']").click()
        driver.find_element(By.XPATH, "//input[@value='Add new']").click()
        driver.find_element(By.ID, "Address_FirstName").send_keys(user_data["new_name"])
        driver.find_element(By.ID, "Address_LastName").send_keys(user_data["new_last_name"])
        driver.find_element(By.ID, "Address_Email").send_keys(user_data["new_email"])
        country_select = Select(driver.find_element(By.ID, "Address_CountryId"))
        country_select.select_by_visible_text(address_data["country"])
        driver.find_element(By.ID, "Address_City").send_keys(address_data["city"])
        driver.find_element(By.ID, "Address_Address1").send_keys(address_data["street"])
        driver.find_element(By.ID, "Address_ZipPostalCode").send_keys(address_data["post_code"])
        driver.find_element(By.ID, "Address_PhoneNumber").send_keys(address_data["phone_number"])
        driver.find_element(By.XPATH, "//input[@value='Save']").click()
        self.assertIn(user_data["new_name"], driver.page_source)

    # Test 7: Subskrypcja newslettera
    def test_007_subscribe_to_newsletter(self):
        driver = self.driver
        user_data = test_data["user"]
        newsletter_box = driver.find_element(By.ID, "newsletter-email")
        newsletter_box.send_keys(user_data["email"])
        driver.find_element(By.ID, "newsletter-subscribe-button").click()
        time.sleep(1)
        success_message = driver.find_element(By.ID, "newsletter-result-block").text
        self.assertEqual("Thank you for signing up! A verification email has been sent. We appreciate your interest.", success_message)

    # Test 8: Sortowanie produktów według ceny
    def test_008_sort_products_by_price(self):
        driver = self.driver
        driver.find_element(By.LINK_TEXT, "Books").click()
        sort_dropdown = Select(driver.find_element(By.ID, "products-orderby"))
        sort_dropdown.select_by_visible_text("Price: Low to High")
        time.sleep(2)  # Poczekaj na załadowanie
        products = driver.find_elements(By.CLASS_NAME, "price actual-price")
        prices = [float(p.text.replace("$", "")) for p in products if p.text]
        self.assertEqual(prices, sorted(prices), "Products are not sorted by price.")

    # Test 9: Reset hasła
    def test_009_reset_password(self):
        driver = self.driver
        user_data = test_data["user"]
        driver.find_element(By.XPATH, "//*[@class='ico-login']").click()
        driver.find_element(By.XPATH, "//a[@href='/passwordrecovery']").click()
        driver.find_element(By.ID, "Email").send_keys(user_data["email"])
        driver.find_element(By.XPATH, "//input[@value='Recover']").click()
        recovery_result = driver.find_element(By.XPATH, "//*[@class='result']").text
        self.assertEqual("Email with instructions has been sent to you.", recovery_result)

    # Test 10: Próba wysłania maila z produktem przez niezarejestrowanego użytkownika
    def test_010_send_mail_with_product(self):
        driver = self.driver
        user_data = test_data["user"]
        self.send_product_email(user_data["friends_mail"])
        driver.find_element(By.ID, "YourEmailAddress").send_keys(user_data["email"])
        driver.find_element(By.ID,"PersonalMessage").send_keys("Look at this pc set up!")
        driver.find_element(By.XPATH, "//input[@value='Send email']").click()
        error_message = driver.find_element(By.XPATH, "//div[@class='validation-summary-errors']/ul/li").text
        self.assertEqual("Only registered customers can use email a friend feature", error_message)

    #Test 11: Próba wysłania maila z produktem przez zarejestrowanego użytkownika
    def test_011_send_mail_with_product_registred_user(self):
        driver = self.driver
        user_data = test_data["user"]
        self.login(user_data["email"], user_data["password"])
        self.send_product_email(user_data["friends_mail"])
        driver.find_element(By.ID,"PersonalMessage").send_keys("Look at this pc set up!")
        driver.find_element(By.XPATH, "//input[@value='Send email']").click()
        time.sleep(1)
        message_after_send = driver.find_element(By.XPATH, "//div[@class='result']").text
        self.assertEqual("Your message has been sent.", message_after_send)


    # Test 12: Złożenie zamówienia jako gość, pobranie oraz weryfikacja faktury
    def test_012_guest_order(self):
        driver = self.driver
        user_data = test_data["user"]
        address_data = test_data["address"]
        driver.find_element(By.LINK_TEXT, "Books").click()
        driver.find_element(By.XPATH, "//input[@class='button-2 product-box-add-to-cart-button']").click()
        driver.find_element(By.XPATH, "//span[@class='cart-qty']").click()
        driver.find_element(By.ID, "termsofservice").click()
        driver.find_element(By.ID, "checkout").click()
        driver.find_element(By.XPATH, "//input[@value='Checkout as Guest']").click()
        driver.find_element(By.ID, "BillingNewAddress_FirstName").send_keys(user_data["name"])
        driver.find_element(By.ID, "BillingNewAddress_LastName").send_keys(user_data["last_name"])
        driver.find_element(By.ID, "BillingNewAddress_Email").send_keys(user_data["email"])
        country_select = Select(driver.find_element(By.ID, "BillingNewAddress_CountryId"))
        country_select.select_by_visible_text(address_data["country"])
        driver.find_element(By.ID, "BillingNewAddress_City").send_keys(address_data["city"])
        driver.find_element(By.ID, "BillingNewAddress_Address1").send_keys(address_data["street"])
        driver.find_element(By.ID, "BillingNewAddress_ZipPostalCode").send_keys(address_data["post_code"])
        driver.find_element(By.ID, "BillingNewAddress_PhoneNumber").send_keys(address_data["phone_number"])
        driver.find_element(By.XPATH, "//input[@value='Continue']").click()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='checkout-step-shipping']/div/input"))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "shippingoption_2"))).click()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//form[@id='co-shipping-method-form']/div/input"))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "paymentmethod_3"))).click()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='checkout-step-payment-method']/div/input"))).click()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='checkout-step-payment-info']/div/input"))).click()
        driver.find_element(By.XPATH, "//input[@value='Confirm']").click()
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@class='section order-completed']/ul/li/a"))).click()
        order_number_element = driver.find_element(By.XPATH, "//div[@class='order-number']/strong")
        order_number = order_number_element.text.split("#")[-1].strip()
        print(f"Numer zamówienia: {order_number}")
        pdf_filename = f"order_{order_number}.pdf"
        pdf_link_element = driver.find_element(By.PARTIAL_LINK_TEXT, "PDF Invoice")
        pdf_link_element.click()
        downloaded_file = self.wait_for_download(self.download_dir, pdf_filename)
        assert downloaded_file, f"Plik {pdf_filename} nie został pobrany!"
        print(f"Pobrano plik PDF: {downloaded_file}")
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        local_pdf_path = f"file://{os.path.abspath(downloaded_file)}"
        driver.get(local_pdf_path)
        time.sleep(3)
        screenshot_path = os.path.join(self.download_dir, f"screenshot_{order_number}.png")
        driver.save_screenshot(screenshot_path)
        print(f"Zrzut ekranu zapisano: {screenshot_path}")
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        pdf_text = self.extract_text_from_pdf(downloaded_file)
        print(f"Zawartość faktury:\n{pdf_text}")
        self.assertIn(order_number, pdf_text, "Numer zamówienia nie znajduje się na fakturze!")
        print("Faktura poprawnie zweryfikowana!")


if __name__ == "__main__":
    unittest.main()