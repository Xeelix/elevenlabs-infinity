import os
import sys
import time
import zipfile

import undetected_chromedriver as uc
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


# Prevent closing browser after complete registration
class MyUDC(uc.Chrome):
    def __del__(self):
        try:
            self.service.process.kill()
        except:  # noqa
            pass
        # self.quit()


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def extract_zip(path):
    extension_name = path.split('.')[0]
    print(f"Extracting {path} in path {os.getcwd()}...")
    with zipfile.ZipFile(path, 'r') as zip_ref:
        # Create folder for extension
        if not os.path.exists(f"{extension_name}"):
            os.mkdir(f"{extension_name}")

        zip_ref.extractall(f"{extension_name}")


def close_extension_start_page(driver):
    driver.switch_to.window(driver.window_handles[0])
    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def initialize_driver():
    options = uc.ChromeOptions()
    options.page_load_strategy = 'eager'
    options.add_argument("--headless")

    driver = MyUDC(debug=True, options=options, use_subprocess=True)
    driver.set_window_size(800, 600)

    return driver


def get_temp_email(driver, wait):
    driver.get('https://tempmail.plus/')

    wait.until(ec.visibility_of_element_located((By.ID, 'domain'))).click()
    wait.until(ec.visibility_of_element_located((By.XPATH, "//button[text()='any.pink']"))).click()

    email_name = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "#pre_button"))).get_attribute('value')
    email_domain = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "#domain"))).text
    new_email = email_name + email_domain
    return new_email


def register_to_evenlab(driver, wait, email):
    driver.switch_to.new_window()
    driver.get('https://elevenlabs.io/sign-up')
    wait.until(ec.presence_of_element_located((By.NAME, "email"))).send_keys(email)
    wait.until(ec.presence_of_element_located((By.NAME, "password"))).send_keys(email)

    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR,
                                               "body > div.bg-gray-100.lg\:p-3.min-h-screen.flex.flex-col > div.flex.flex-col.items-center.bg-white.bg-crosses.min-h-full.flex-1 > div > div > div.absolute.right-0.top-0.bottom-0.flex.w-full.sm\:w-1\/2.xl\:w-1\/3.z-10.bg-gray-100\/80.backdrop-blur-lg.justify-start.sm\:justify-center.py-12.px-4.sm\:px-6.lg\:px-16.lg\:flex-none > div > div:nth-child(2) > form > div:nth-child(4) > button"))).click()


def confirm_email(driver, wait):
    driver.switch_to.window(driver.window_handles[0])
    while True:
        try:
            wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "#container-body > div > div.inbox > div.mail"))).click()
            break
        except TimeoutException:
            driver.refresh()
    confirm_url = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR,
                                                             "#info > div.overflow-auto.mb-20 > center > div > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table:nth-child(4) > tbody > tr > td > table > tbody > tr > td > a"))).get_property(
        "href")
    return confirm_url


def click_confirmation_link(driver, confirm_url):
    driver.get(confirm_url)


def login_again(driver, wait, email):
    wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR,
                                               "#headlessui-dialog-panel-P0-0 > div.bg-gray-50.px-4.py-3.flex.justify-end.sm\:px-6 > button"))).click()
    wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, "#sign-in-form > div:nth-child(2) > input"))).send_keys(
        email)
    wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, "#sign-in-form > div:nth-child(3) > input"))).send_keys(
        email)
    wait.until(ec.visibility_of_element_located(
        (By.CSS_SELECTOR, "#sign-in-form > div.flex.items-center.justify-between.space-x-2 > button"))).click()


def open_api_key(driver, wait):
    wait.until(
        ec.visibility_of_element_located((By.CSS_SELECTOR, "div.relative.inline-block.font-sans.text-left"))).click()
    wait.until(ec.visibility_of_element_located((By.XPATH, '//div[@role="menu"]//a[@role="menuitem"]'))).click()

    time.sleep(3)
    # Click show api
    # wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, '.space-y-3 svg'))).click()
    api_key = wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, "input[type='password']"))).get_attribute(
        'value')
    return api_key


def register():
    driver = initialize_driver()
    wait = WebDriverWait(driver, 20)

    print("Trying to get email")
    email = get_temp_email(driver, wait)

    print("Registering to evenlab")
    register_to_evenlab(driver, wait, email)

    print("Confirming email")
    confirm_url = confirm_email(driver, wait)
    click_confirmation_link(driver, confirm_url)

    print("Logging in again to get api key")
    login_again(driver, wait, email)
    api_key = open_api_key(driver, wait)

    return api_key


if __name__ == '__main__':
    api = register()
    print(f"API KEY: {api}")
