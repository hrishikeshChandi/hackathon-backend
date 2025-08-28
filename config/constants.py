import os
from dotenv import load_dotenv

load_dotenv()

CITIES_FILE_PATH = os.getenv("CITIES_FILE_PATH")
INSTRUCTIONS_PATH = os.getenv("INSTRUCTIONS_PATH")
REPORT_FILE_NAME = os.getenv("REPORT_FILE_NAME")
FOLDER = os.getenv("FOLDER")

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
MODULE = os.getenv("MODULE")

PROACTO_URL = os.getenv("PROACTO_URL")
PHAR_EASY_URL = os.getenv("PHAR_EASY_URL")
MED_PLUS_URL = os.getenv("MED_PLUS_URL")
