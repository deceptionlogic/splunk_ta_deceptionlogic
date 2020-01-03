# Splunk TA for Deception Logic

This Splunk App pulls event and alert data from the Deception Logic API.

## Install

Place this app on your search head under `$SPLUNK_HOME/etc/apps/`
Create the index on your indexer, see Create Indexes section below for instructions.

## Configure

In order for the app to pull data from Deception Logic you must add your API keys to the configuration. There are two files used to configure the app:

- `bin/deceptionlogic.json`
- `default/inputs.conf`

At minimum, and recommended, you only need to add your Deception Logic API key ID and secret key to `bin/deceptionlogic.json`.

__Configuration file: `bin/deceptionlogic.json`__

    {
        "X-DeceptionLogic-KeyId": "<your key ID>",
        "X-DeceptionLogic-SecretKey": "<your secret key>",
        "eventapi_run_time": "1m",
        "alertapi_run_time": "30s"
    }

Additional options:

- The `eventapi_run_time` option is used to define the duration of event data to be extracted from Deception Logic. You must specify `<number><unit>`. For example, "1m" indicates one minute. Valid units are "d" (days), "h" (hours), "m" (minutes), and "s" (seconds).

- The `alertapi_run_time` option is used to define the duration of the alert data to be extracted from Deception Logic. You must specify `<number><unit>`. For example, "1m" indicates one minute. Valid units are "d" (days), "h" (hours), "m" (minutes), and "s" (seconds).

__Note:__ While you can modify the values of the `eventapi_run_time` and `alertapi_run_time` options, it is recommended to use the default values.

If you change the duration options above, you will also need to change the interval values in `default/inputs.conf`. In order to avoid dupilicate or missing data issues, the duration options must match with the coorosponding interval values.

## Create Indexes

Create indexes.conf on your indexer with the default index name "Deceptionlogic" Below is the sample of index:

    [deceptionlogic]
    homePath   = $SPLUNK_DB/deceptionlogic/db
    coldPath   = $SPLUNK_DB/deceptionlogic/colddb 
    thawedPath = $SPLUNK_DB/deceptionlogic/thaweddb
    #1 day retention 
    frozenTimePeriodInSecs = 86400
    #14 day retention
    #frozenTimePeriodInSecs = 1209600

__**NOTE:__ If you change the index name, make sure you update `default/inputs.conf` to reflect the new index name, e.g. `index = <new index name >`

__**NOTE:__ If you modify any files in the `default` folder, please create the copy of the file in local directory and change it in local directory. After completing changes, restart the Splunk process.

## Viewing data in Splunk

index="deceptionlogic" sourcetype="deceptionlogic_alerts"

index="deceptionlogic" sourcetype="deceptionlogic_events"

_If you changed index name or sourcetype, please modify the above query accordingly._

## Troubleshooting

- You can view Splunk app error messages by querying `index=_internal source="*splunk/deceptionlogic.log"` or `index=_internal source = *splunkd.log`

## Dashboard

1. Select splunk_ta_deceptionlogic app in the Splunk UI. Go to Dashboards and click on __Deception Logic Events__.
