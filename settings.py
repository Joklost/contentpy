import os

SCRAPE_DATA = os.environ.get("SCRAPE_DATA", "data/scrape.data")
JSON_PATH = os.environ.get("JSON_PATH", "data/output.json")
TRAINING_PATH = os.environ.get("TRAINING_PATH", "data/training.json")
TRAINING_AMOUNT = os.environ.get("TRAINING_AMOUNT", 500)
VALIDATION_PATH = os.environ.get("VALIDATION_PATH", "data/validation.json")
VALIDATION_AMOUNT = os.environ.get("VALIDATION_AMOUNT", 0)
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
API_TOKEN = os.environ.get('API_TOKEN', 'FOOBAR1')
LOGFILE = os.environ.get("LOGFILE", "out.log")
IP = os.environ.get("IP", "localhost")
