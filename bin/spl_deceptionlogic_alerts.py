'''
Send Deception Logic alerts to Splunk
'''
import os
import sys
import json
import logging
import logging.handlers
import requests


def setup_logger(level):
    '''
    WRITE THE INTERNAL LOGS TO LOGFILE FOR DECEPTIONLOGIC
    '''
    logger = logging.getLogger('')
    logger.propagate = False # Prevent the log messages from being duplicated in the python.log file
    logger.setLevel(level)
    log_file = os.path.join(sys.path[0], "..", "..", "..", "..", 'var', 'log', 'splunk', 'deceptionlogic.log')
    file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=25000000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger

### MAIN FUNCTION ###

if __name__ == "__main__":

    ## CHECK For the deceptionlogic.json file exists ##
    filename = "deceptionlogic.json"
    jsonfile = os.path.join(sys.path[0], filename)
    try:
        with open(jsonfile, 'r') as argfile:
            data = argfile.read()
    except:
        logger = setup_logger(logging.ERROR)
        logger.error("Alert Error: Deceptionlogic args file missing : ./%s ", jsonfile)
        exit()

    # parse file
    try:
        args = json.loads(data)
    except ValueError as jsonerror:
        logger = setup_logger(logging.ERROR)
        logger.error("Alert Error: File %s data read error %s ", jsonfile, jsonerror)
        exit()

    if ("X-DeceptionLogic-KeyId" in args) and ("X-DeceptionLogic-SecretKey" in args):
        keyId = str(args['X-DeceptionLogic-KeyId'])
        SecretKey = str(args['X-DeceptionLogic-SecretKey'])
    else:
        logger = setup_logger(logging.ERROR)
        logger.error("Alert Error: Deceptionlogic args X-DeceptionLogic-KeyId OR/AND X-DeceptionLogic-SecretKey missing in file : ./%s ", jsonfile)
        exit()

    if (keyId and SecretKey):
        headers = {
            'X-DeceptionLogic-KeyId': keyId,
            'X-DeceptionLogic-SecretKey': SecretKey,
        }

        response = requests.get('https://api.deceptionlogic.com/v0/authenticate', headers=headers, verify=False)
        if response.status_code == 200:
            logger = setup_logger(logging.INFO)
            logger.info("Alert Info: DeceptionLogic API Authentication Success")
        else:
            logger = setup_logger(logging.ERROR)
            logger.error("Alert Error: DeceptionLogic API Authentication Failed. Response Code:%s ", response.status_code)
            exit()

        auth = response.json()
        token = auth['token']
        api_id = auth['id']

        headers = {
            'X-DeceptionLogic-Token': token,
            'X-DeceptionLogic-Id': api_id,
        }

        if "alertapi_run_time" in args:
            runtime = str(args['alertapi_run_time'])

        if runtime is None:
            runtime = '1m' ## Default value of runtime 1m

        if runtime[-1] == "m" or runtime[-1] == "s" or runtime[-1] == "h" or runtime[-1] == "d":
            if runtime[:-1].isdigit():
                url = 'https://api.deceptionlogic.com/v0/alerts?from={0}'.format(runtime)
                response = requests.get(url, headers=headers, verify=False)
            else:
                logger = setup_logger(logging.ERROR)
                logger.error("Alert Error: Please enter the alertapi_run_time in deceptionlogic.json in right format (digits + m for months, d for days, s for seconds and h for hours). E.g for 1 min : 1m")
                exit()
        else:
            logger = setup_logger(logging.ERROR)
            logger.error("Alert Error: Please enter the alertapi_run_time in deceptionlogic.json in right format (digits + m for months, d for days, s for seconds and h for hours). E.g for 1 min : 1m")
            exit()

        try:
            alertjson = response.json()
            if alertjson:
                for i in alertjson:
                    ### Send Data to Splunk ###
                    date_time = i["date_time"]
                    del i["date_time"]
                    data_j = json.dumps(i)
                    data_j = data_j[:1] + "\"date\": \"" + date_time + "\", \"" + data_j[2:] + "\n"
                    print data_j

        except ValueError:
            logger = setup_logger(logging.ERROR)
            logger.error("Alert API call failed . Please check your authentication key or check with DeceptionLogic Support team. API response code: %s", response.status_code)
            exit()
    else:
        logger = setup_logger(logging.ERROR)
        logger.error("DeceptionLogic API key ID and Secret Key can not be blank. Please Enter the right keys")
        exit()
