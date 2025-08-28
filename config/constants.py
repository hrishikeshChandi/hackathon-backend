import os

CITIES_FILE_PATH = "./data/cities.json"
FOLDER = "uploads"
PORT = 1200
HOST = "127.0.0.1"
MODULE = "main:app"
REPORT_FILE_NAME = "reports.txt"
FINAL_INSTRUCTIONS_PATH = "./data/final_instructions.txt"
PHARM_EASY_URL = "https://pharmeasy.in/search/all?name="
MED_PLUS_URL = "https://www.medplusmart.com/"
PROACTO_URL = "https://www.practo.com/search/hospitals?results_type=hospital&q=%5B%7B%22word%22%3A%22hospitals%22%2C%22autocompleted%22%3Atrue%2C%22category%22%3A%22hospital_name%22%7D%5D&city="


if not os.path.exists(FOLDER):
    os.mkdir(FOLDER)
