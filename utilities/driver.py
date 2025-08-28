from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager


def get_driver() -> webdriver.Firefox:
    firefox_options = Options()
    firefox_options.set_preference("dom.webnotifications.enabled", False)
    firefox_options.set_preference("geo.enabled", False)
    firefox_options.set_preference("useAutomationExtension", False)
    firefox_options.set_preference("dom.push.enabled", False)

    firefox_options.add_argument("--headless")

    service = Service(GeckoDriverManager().install())
    return webdriver.Firefox(service=service, options=firefox_options)
