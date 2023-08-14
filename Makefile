package:
	tar -czf splunk_ta_deceptionlogic.tar.gz splunk_ta_deceptionlogic

env:
	python3 -m venv .env
	.env/bin/pip install black ruff requests wheel

inspect:
	wget https://download.splunk.com/misc/appinspect/splunk-appinspect-latest.tar.gz
	.env/bin/pip install splunk-appinspect-latest.tar.gz
	.env/bin/splunk-appinspect inspect splunk_ta_deceptionlogic.tar.gz	

lint:
	.env/bin/black splunk_ta_deceptionlogic/bin/spl_deceptionlogic_alerts.py
	.env/bin/black splunk_ta_deceptionlogic/bin/spl_deceptionlogic_events.py
	.env/bin/ruff splunk_ta_deceptionlogic/bin/spl_deceptionlogic_alerts.py
	.env/bin/ruff splunk_ta_deceptionlogic/bin/spl_deceptionlogic_events.py

clean:
	-rm splunk_ta_deceptionlogic.tar.gz
	-rm splunk-appinspect-latest.tar.gz
	-rm -rf .env
