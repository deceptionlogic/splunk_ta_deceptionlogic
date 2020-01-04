'''
Send Deception Logic events to Splunk
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
        logger.error("Events Error: Deceptionlogic args file missing : ./%s ", jsonfile)
        sys.exit()

    # parse file
    try:
        args = json.loads(data)
    except ValueError as jsonerror:
        logger = setup_logger(logging.ERROR)
        logger.error("Events Error: File %s data read error %s ", jsonfile, jsonerror)
        sys.exit()

    if ("X-DeceptionLogic-KeyId" in args) and ("X-DeceptionLogic-SecretKey" in args):
        keyId = str(args['X-DeceptionLogic-KeyId'])
        SecretKey = str(args['X-DeceptionLogic-SecretKey'])
    else:
        logger = setup_logger(logging.ERROR)
        logger.error("Events Error: Deceptionlogic args X-DeceptionLogic-KeyId OR/AND X-DeceptionLogic-SecretKey missing in file : ./%s ", jsonfile)
        sys.exit()

    if (keyId and SecretKey):
        headers = {
            'X-DeceptionLogic-KeyId': keyId,
            'X-DeceptionLogic-SecretKey': SecretKey,
        }

        response = requests.get('https://api.deceptionlogic.com/v0/authenticate', headers=headers, verify=False)
        if response.status_code == 200:
            logger = setup_logger(logging.INFO)
            logger.info("Events INFO : DeceptionLogic API Authentication Success")
        else:
            logger = setup_logger(logging.ERROR)
            logger.error("Events Error: DeceptionLogic API Authentication Failed. Response Code:%s ", response.status_code)
            sys.exit()

        auth = response.json()
        token = auth['token']
        apid_id = auth['id']

        headers = {
            'X-DeceptionLogic-Token': token,
            'X-DeceptionLogic-Id': apid_id,
        }

        if "eventapi_run_time" in args:
            runtime = str(args['eventapi_run_time'])

        if runtime is None:
            runtime = '1m' ## Default value of runtime 1m

        if runtime[-1] == "m" or runtime[-1] == "s" or  runtime[-1] == "h" or runtime[-1] == "d":
            if runtime[:-1].isdigit():
                url = 'https://api.deceptionlogic.com/v0/events?from={0}'.format(runtime)
                response = requests.get(url, headers=headers, verify=False)
            else:
                logger = setup_logger(logging.ERROR)
                logger.error("Events Error: Please enter the eventapi_run_time in deceptionlogic.json in right format (digits + m for months, d for days, s for seconds and h for hours). E.g for 1 min : 1m")
                sys.exit()
        else:
            logger = setup_logger(logging.ERROR)
            logger.error("Events Error: Please enter the eventapi_run_time in deceptionlogic.json in right format (digits + m for months, d for days, s for seconds and h for hours). E.g for 1 min : 1m")
            sys.exit()

        try:
            eventjson = response.json()
            if eventjson:
                for i in eventjson:
                    ### Send Data to Splunk ###
                    data_j = json.dumps(i)
                    print(data_j)

        except ValueError:
            logger = setup_logger(logging.ERROR)
            logger.error("Events API call failed . Please check your authentication key or check with DeceptionLogic Support team. API response code : %s", response.status_code)
            sys.exit()
    else:
        logger = setup_logger(logging.ERROR)
        logger.error("DeceptionLogic API key ID and Secret Key can not be blank. Please Enter the right keys")
        sys.exit()
