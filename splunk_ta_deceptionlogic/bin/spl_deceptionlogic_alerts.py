"""
Send Deception Logic alerts to Splunk
"""
import os
import sys
import json
import logging
import logging.handlers
import requests
from configparser import ConfigParser
from splunk.clilib import cli_common as cli  # pylint: disable=import-error


def get_app_version():
    """
    Return current app version
    """
    bin_dir = os.path.dirname(os.path.abspath(__file__))
    app_conf_path = os.path.join(bin_dir, "..", "default", "app.conf")
    version = "0.0.0"
    config = ConfigParser()
    config.read(app_conf_path)
    # Get the version value from the [launcher] section
    if config.has_section("launcher") and config.has_option("launcher", "version"):
        version = config.get("launcher", "version")

    return version


def setup_logger(level):
    """
    WRITE THE INTERNAL LOGS TO LOGFILE FOR DECEPTIONLOGIC
    """
    logger = logging.getLogger("")
    logger.propagate = (
        False  # Prevent the log messages from being duplicated in the python.log file
    )
    logger.setLevel(level)
    log_file = os.path.join(
        sys.path[0],
        "..",
        "..",
        "..",
        "..",
        "var",
        "log",
        "splunk",
        "deceptionlogic.log",
    )
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=25000000, backupCount=5
    )
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger


### MAIN FUNCTION ###

if __name__ == "__main__":
    ## get splunk version
    splunk_version = cli.getConfKeyValue("app", "launcher", "version")
    ## get splunk app version
    app_version = get_app_version()
    ## compose ua string
    user_agent = "Deception Logic Spunk App/{} (Splunk {}; Requests {})".format(
        app_version, splunk_version, requests.__version__
    )

    ## CHECK For the deceptionlogic.json file exists ##
    jsonfile = os.path.join(sys.path[0], "deceptionlogic.json")
    try:
        with open(jsonfile, "r") as argfile:
            data = argfile.read()
    except Exception:
        logger = setup_logger(logging.ERROR)
        logger.error("Alert Error: Deceptionlogic args file missing : ./%s ", jsonfile)
        sys.exit()

    # parse file
    try:
        args = json.loads(data)
    except ValueError as jsonerror:
        logger = setup_logger(logging.ERROR)
        logger.error("Alert Error: File %s data read error %s ", jsonfile, jsonerror)
        sys.exit()

    if ("X-DeceptionLogic-KeyId" in args) and ("X-DeceptionLogic-SecretKey" in args):
        keyId = str(args["X-DeceptionLogic-KeyId"])
        SecretKey = str(args["X-DeceptionLogic-SecretKey"])
    else:
        logger = setup_logger(logging.ERROR)
        logger.error(
            "Alert Error: Deceptionlogic args X-DeceptionLogic-KeyId OR/AND X-DeceptionLogic-SecretKey missing in file : ./%s ",  # noqa: E501
            jsonfile,
        )
        sys.exit()

    if keyId and SecretKey:
        headers = {
            "X-DeceptionLogic-KeyId": keyId,
            "X-DeceptionLogic-SecretKey": SecretKey,
            "User-Agent": user_agent,
        }

        response = requests.get(
            "https://api.deceptionlogic.com/v0/authenticate",
            headers=headers,
        )
        if response.status_code == 200:
            logger = setup_logger(logging.INFO)
            logger.info("Alert Info: DeceptionLogic API Authentication Success")
        else:
            logger = setup_logger(logging.ERROR)
            logger.error(
                "Alert Error: DeceptionLogic API Authentication Failed. Response Code:%s ",  # noqa: E501
                response.status_code,
            )
            sys.exit()

        auth = response.json()
        token = auth["token"]
        api_id = auth["id"]

        headers = {
            "X-DeceptionLogic-Token": token,
            "X-DeceptionLogic-Id": api_id,
            "User-Agent": user_agent,
        }

        if "alertapi_run_time" in args:
            runtime = str(args["alertapi_run_time"])

        if runtime is None:
            runtime = "1m"  ## Default value of runtime 1m

        if (
            runtime[-1] == "m"
            or runtime[-1] == "s"
            or runtime[-1] == "h"
            or runtime[-1] == "d"
        ):
            if runtime[:-1].isdigit():
                url = "https://api.deceptionlogic.com/v0/alerts?from={0}".format(
                    runtime
                )
                response = requests.get(url, headers=headers)
            else:
                logger = setup_logger(logging.ERROR)
                logger.error(
                    "Alert Error: Please enter the alertapi_run_time in deceptionlogic.json in right format (digits + m for months, d for days, s for seconds and h for hours). E.g for 1 min : 1m"  # noqa: E501
                )
                sys.exit()
        else:
            logger = setup_logger(logging.ERROR)
            logger.error(
                "Alert Error: Please enter the alertapi_run_time in deceptionlogic.json in right format (digits + m for months, d for days, s for seconds and h for hours). E.g for 1 min : 1m"  # noqa: E501
            )
            sys.exit()

        try:
            alertjson = response.json()
            if alertjson:
                for i in alertjson:
                    ### Send Data to Splunk ###
                    date_time = i["date_time"]
                    del i["date_time"]
                    data_j = json.dumps(i)
                    data_j = (
                        data_j[:1]
                        + '"date": "'
                        + date_time
                        + '", "'
                        + data_j[2:]
                        + "\n"
                    )
                    print(data_j)

        except ValueError:
            logger = setup_logger(logging.ERROR)
            logger.error(
                "Alert API call failed . Please check your authentication key or check with DeceptionLogic Support team. API response code: %s",  # noqa: E501
                response.status_code,
            )
            sys.exit()
    else:
        logger = setup_logger(logging.ERROR)
        logger.error(
            "DeceptionLogic API key ID and Secret Key can not be blank. Please Enter the right keys"  # noqa: E501
        )
        sys.exit()
