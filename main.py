import os, shutil, json, uvicorn, requests, time
from fastapi import FastAPI, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from selenium import webdriver
from typing import List, Optional
from selenium.common import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC

app = FastAPI()

FOLDER = "uploads"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

roles = {
    "physician": "general-physician",
    "psychologist": "psychologist",
    "gynecologist": "gynecologist",
    "pediatrician": "pediatrician",
    "endocrinologist": "endocrinologist",
    "dermatologist": "dermatologist",
    "urologist": "urologist",
    "neurologist": "neurologist",
    "gastroenterologist": "gastroenterologist",
}

with open("./hosp_cities.json") as f:
    cities = json.load(f)


class Doctor(BaseModel):
    city: str
    role: str


# working
def get_driver():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--disable-geolocation")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option(
        "prefs",
        {"profile.default_content_setting_values.geolocation": 2},
    )
    # chrome_options.add_argument("--headless")
    service = Service(r"C:\webdrivers\chromedriver-win64\chromedriver.exe")
    # service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


# working
def doc_details(obj: Doctor):
    driver = get_driver()
    url = f"https://www.healthgennie.com/{obj.city}/{roles[obj.role]}"
    driver.get(url)
    doctors = driver.find_elements(
        By.CSS_SELECTOR, ".container-inner .right-content .listing"
    )
    details = []
    for doctor in doctors:
        name = doctor.find_element(By.CSS_SELECTOR, ".profile-detail h3").text
        availability = doctor.find_element(By.CSS_SELECTOR, ".doc_available p").text
        role = doctor.find_element(
            By.CSS_SELECTOR, ".profile-detail .dgree-top li"
        ).text
        degree = doctor.find_element(
            By.CSS_SELECTOR, ".profile-detail .dgree-top .Dgree-section span"
        ).text
        experience = doctor.find_element(
            By.CSS_SELECTOR, ".profile-detail .dgree-top h4 span"
        ).text
        fees = doctor.find_element(By.CSS_SELECTOR, ".fees .cons-fees strong").text
        details.append(
            {
                "name": name,
                "role": role,
                "degree": degree,
                "experience": experience,
                "availability": availability,
                "tele_consultation_fees": int(fees),
            }
        )
    driver.quit()
    details.sort(key=lambda x: x["tele_consultation_fees"])
    return details


# working
def side_effects(medicines: list):
    output = "\nSide effects of your current medications according to OpenFDA reports:"
    effects = []
    for tablet in medicines:
        url = f"https://api.fda.gov/drug/event.json?search=patient.drug.medicinalproduct:{tablet}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if (
                data.get("results")
                and isinstance(data["results"], list)
                and len(data["results"]) > 0
                and "patient" in data["results"][0]
                and "reaction" in data["results"][0]["patient"]
            ):
                reactions = data["results"][0]["patient"]["reaction"]
                reactions_list = []
                for reaction in reactions:
                    reaction_text = reaction.get("reactionmeddrapt", "No reaction info")
                    reactions_list.append(reaction_text)
                effects.append(
                    {"tablet": tablet, "reaction": ", ".join(reactions_list)}
                )
        else:
            effects.append(
                {
                    "tablet": tablet,
                    "reaction": "Failed to retrieve data (doesn't exist in OpenFDA database, please check the spelling)",
                }
            )
    for effect in effects:
        output += f"\n{effect['tablet']} : {effect['reaction']}"
    output += "\n"
    return output


# working
def price_comp(medicines: list):
    driver = get_driver()
    med_plus_links = []
    pharm_easy_links = []
    with open("./final_instructions.txt", "r") as f:
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
    driver.quit()
    return instructions


# working
def pharm_easy(tablet: str):
    return f"https://pharmeasy.in/search/all?name={tablet}"


# working
def med_plus(tablet: str, driver):
    driver.get("https://www.medplusmart.com/")
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
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".item"))
        )
        link = driver.current_url
        print(link)
        return link
    except (NoSuchElementException, TimeoutException):
        return None


def hospitals_info(city: str):
    driver = get_driver()
    url = f"https://www.practo.com/search/hospitals?results_type=hospital&q=%5B%7B%22word%22%3A%22hospitals%22%2C%22autocompleted%22%3Atrue%2C%22category%22%3A%22hospital_name%22%7D%5D&city={city}"
    driver.get(url)
    hospitals = []
    driver.refresh()
    hospital_elements = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.c-estb-card"))
    )
    try:
        for hospital in hospital_elements:
            if len(hospitals) == 10:
                break
            
            name = (
                WebDriverWait(hospital, 10)
                .until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2")))
                .text
            )
            location = (
                WebDriverWait(hospital, 10)
                .until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "span.c-locality-info span")
                    )
                )
                .text
            )
            consultation_fee = (
                WebDriverWait(hospital, 10)
                .until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "p.line-3 span.u-bold")
                    )
                )
                .text
            )
            link = (
                WebDriverWait(hospital, 10)
                .until(EC.presence_of_element_located((By.CSS_SELECTOR, "a")))
                .get_attribute("href")
            )
            try:
                rating = (
                    WebDriverWait(hospital, 15)
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
            hospitals.append(
                {
                    "name": name,
                    "location": location,
                    "rating": rating,
                    "consultation_fee": consultation_fee,
                    "link": link,
                }
            )
        return hospitals
    finally:
        driver.quit()


# working
@app.get("/doc_data", status_code=status.HTTP_200_OK)
async def get_doc_data(city: str, role: str):
    try:
        if city.title() in cities and role in roles:
            obj = Doctor(city=city, role=role)
            results = doc_details(obj)
            if len(results) > 0:
                return {"data": results}
        elif city.title() not in cities:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="City not found. Please check the city name and try again.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found. Please check the role name and try again.",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# working
@app.get("/hospitals_data", status_code=status.HTTP_200_OK)
async def get_hospital_data(city: str):
    if city.title() not in cities:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hospitals found for the given city. Please check your city name and try again.",
        )
    try:
        results = hospitals_info(city.title())
        if results and len(results) > 0:
            return {"data": results}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hospitals found for the given city. Please check your city name and try again.",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Please try again.",
        )


@app.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload(
    diet: str,
    symptoms: str,
    current_medicines: str,
    exercise: str,
    additional_info: Optional[str] = None,
    files: List[UploadFile] = File(...),
):
    try:
        if not os.path.exists(FOLDER):
            os.mkdir(FOLDER)

        for file in files:
            path = os.path.join(FOLDER, file.filename)
            print(f"added : {path}")

            with open(path, "wb") as f:
                shutil.copyfileobj(file.file, f)

        print(diet, symptoms, current_medicines, exercise, additional_info)

        # medicines = current_medicines.split(",")
        # medicines = [med.strip() for med in medicines]
        # compared_prices = price_comp(medicines)
        # compared_prices += "\n" + side_effects(medicines) + "\n"
        # with open("./info.txt", "w") as f:
        #     f.write(compared_prices)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    finally:
        current_files = os.listdir(FOLDER)
        if len(current_files):
            for file in current_files:
                path = os.path.join(FOLDER, file)
                os.remove(path)


# working
@app.get("/download", status_code=status.HTTP_200_OK)
async def download(filename: str):
    # to be improved using "reports.txt" so that no need of any parameters
    path = os.path.join(FOLDER, filename)
    if os.path.exists(path):
        return FileResponse(filename=filename, path=path)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Please upload your file to get a report",
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
