import json
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.constants import (
    CITIES_FILE_PATH,
    PROACTO_URL,
    PHARM_EASY_URL,
    MED_PLUS_URL,
    FINAL_INSTRUCTIONS_PATH,
)


with open(CITIES_FILE_PATH) as f:
    cities = json.load(f)


def get_details(hospital, time_to_wait: int = 2) -> dict:

    name = hospital.find_element(By.CSS_SELECTOR, "h2").text
    location = hospital.find_element(By.CSS_SELECTOR, "span.c-locality-info span").text
    consultation_fee = hospital.find_element(
        By.CSS_SELECTOR, "p.line-3 span.u-bold"
    ).text
    link = hospital.find_element(By.CSS_SELECTOR, "a").get_attribute("href")

    try:
        rating = (
            WebDriverWait(hospital, time_to_wait)
            .until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.text-1 span.u-bold")
                )
            )
            .text
        )
    except Exception as e:
        print(e)
        rating = "--"

    return {
        "name": name,
        "location": location,
        "rating": rating,
        "consultation_fee": consultation_fee,
        "link": link,
    }


def hospitals_info(city: str, driver) -> list:
    url = PROACTO_URL + city
    driver.get(url)
    driver.refresh()
    hospitals = []
    hospital_elements = WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.c-estb-card"))
    )
    for hospital in hospital_elements:
        if len(hospitals) == 10:
            break
        hospitals.append(get_details(hospital))
    return hospitals


def pharm_easy(tablet: str) -> str:
    return PHARM_EASY_URL + tablet


def med_plus(tablet: str, driver) -> str | None:
    driver.get(MED_PLUS_URL)
    driver.refresh()
    search_box = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".homepage-input input.form-control-lg")
        )
    )
    driver.execute_script("arguments[0].click();", search_box)
    search = driver.find_element(
        By.XPATH,
        "/html/body/div[2]/div/div[1]/div/div/div/div/div/div[1]/div/div/input",
    )
    search.send_keys(tablet, Keys.ENTER)
    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".item"))
        )
        link = driver.current_url
        print(link)
        return link
    except (NoSuchElementException, TimeoutException):
        return None


def price_comp(medicines: list, driver) -> str:
    med_plus_links = []
    pharm_easy_links = []
    with open(FINAL_INSTRUCTIONS_PATH, "r") as f:
        instructions = f.read()
    for tablet in medicines:
        med_plus_links.append(med_plus(tablet, driver))
        pharm_easy_links.append(pharm_easy(tablet))
    for tablet, m_link, p_link in zip(medicines, med_plus_links, pharm_easy_links):
        if not m_link:
            instructions += (
                f"{tablet} : Confirm this with a doctor or pharmacist once.\n"
            )
        else:
            instructions += f"{tablet}:\nMed plus : {m_link}\nPharm Easy : {p_link}\n\n"
    return instructions
