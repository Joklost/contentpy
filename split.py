import json
import os


def split_json(log, validate_amount: int,
               json_path: str,
               training_name: str,
               validation_name: str) -> (str, str):

    cur_dir = os.getcwd()

    with open(json_path, 'r') as infile:
        o = json.load(infile)
        l = len(o)
        calc_validation_amount = (validate_amount if not validate_amount == -1 else int(l * 0.1))
        log.info("splitting json data. adding {} to training data and {} to validation data".format(
            l - calc_validation_amount, calc_validation_amount))
        training_data = l - calc_validation_amount
    training_path = cur_dir + "/" + training_name
    with open(training_path, 'w') as training_file:
        json.dump(o[0:training_data], training_file)

    validation_path = cur_dir + "/" + validation_name
    with open(validation_path, 'w') as validate_file:
        json.dump(o[training_data + 1:len(o)], validate_file)

    return (training_path, validation_path)
