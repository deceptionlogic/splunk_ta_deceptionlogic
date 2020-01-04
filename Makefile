package:
	tar -czf splunk_ta_deceptionlogic.tar.gz splunk_ta_deceptionlogic

inspect:
	wget https://download.splunk.com/misc/appinspect/splunk-appinspect-latest.tar.gz
	virtualenv .env
	.env/bin/pip install splunk-appinspect-latest.tar.gz
	.env/bin/splunk-appinspect inspect splunk_ta_deceptionlogic.tar.gz	

lint:
	pylint splunk_ta_deceptionlogic/bin/spl_deceptionlogic_alerts.py
	pylint splunk_ta_deceptionlogic/bin/spl_deceptionlogic_events.py

clean:
	-rm splunk_ta_deceptionlogic.tar.gz
	-rm splunk-appinspect-latest.tar.gz
	-rm -rf .env
