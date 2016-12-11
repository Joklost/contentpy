#!/usr/bin/env python3
from engine import ContentEngine
from flask import Flask, request, abort, current_app
from functools import wraps
from split import split_json
import json
import logging
import os
import sys

HOME = os.path.expanduser("~")
FORMAT_STR = "[%(asctime)s][%(filename)12s:%(lineno)3d][%(threadName)s][%(levelname)1s]: %(message)s"
FORMAT = logging.Formatter(FORMAT_STR)

app = Flask(__name__)
app.debug = True
app.config.from_object("settings")


def token_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.args["TOKEN"] != current_app.config['API_TOKEN']:
            # if request.headers.get('TOKEN', None) != current_app.config['API_TOKEN']:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@app.route("/logs/")
def logs():
    if os.path.exists(current_app.config["LOGFILE"]):
        with open(current_app.config["LOGFILE"], "r") as logfile:
            log_lines = "<html><pre>"
            for line in logfile.readlines():
                log_lines += "{}{}".format(line, "")
            log_lines += "</pre></html>"
            return "{}".format(log_lines)

    return "No logs found."


@app.route("/predict/", methods=['GET'])
@token_auth
def predict():
    engine = ContentEngine()
    return str(engine.predict(request.args["subreddit"]))


@app.route("/train/")
@token_auth
def train():
    # Opens the "scrape.data" (as specified in settings.py)
    # file, where each line is a json dictionary, and adds
    # every subreddit with a given minimum of subscribers
    # to a list.
    min_subscribers = 100
    i = 0
    subreddits = []
    with open(current_app.config["SCRAPE_DATA"], "r") as j:
        for l in j.readlines():
            sr = json.loads(l)
            if sr["subscribers"] > min_subscribers and sr["lang"] == "en":
                if sr["description"] == "" or not sr["description"]:
                    continue
                if current_app.config["TRAINING_AMOUNT"] == i:
                    break
                sr["id"] = i
                i += 1
                subreddits.append(sr)
    log.info("read {} json objects from scrape.data".format(i))

    # Writes the subreddits array (an array of dictionaries)
    # as a single json file. This file is used by either the
    # following split function, or by pandas in the engine
    # class following the splitter.
    with open(current_app.config["TRAINING_PATH"], "w", encoding="utf-8") as j:
        out = json.dumps(subreddits)
        j.write(str(out))

    # Should the dataset be too big to fit in memory
    # the split module takes a set amount of json
    # objects, and splits the amount to a new file
    # to be used by the kernel for training.
    # However, as it stands right now, the dataset
    # is just small enough to be able to fit in
    # memory, so the current validation amount
    # is set to 0.
    if current_app.config["VALIDATION_AMOUNT"] != 0:
        training_path, validation_path = split_json(
            log,
            current_app.config["VALIDATION_AMOUNT"],
            current_app.config["JSON_PATH"],
            current_app.config["TRAINING_PATH"],
            current_app.config["VALIDATION_PATH"]
        )
    engine = ContentEngine()
    engine.train()

    return "SUCCESS"


if __name__ == "__main__":
    with app.app_context():
        logging.basicConfig(
            format=FORMAT_STR,
            level=logging.DEBUG,
            stream=sys.stdout,
            datefmt="%H:%M:%S"
        )

        file_log_handler = logging.FileHandler(current_app.config["LOGFILE"], "w")
        file_log_handler.setFormatter(FORMAT)

        log = logging.getLogger("content")
        log.addHandler(file_log_handler)
        app.run(current_app.config["IP"])
