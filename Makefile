package:
	tar -czf splunk_ta_deceptionlogic.tar.gz splunk_ta_deceptionlogic

env:
	python3 -m venv .env
	.env/bin/pip install --upgrade pip
	.env/bin/pip install ruff requests wheel splunk-appinspect

inspect:
	.env/bin/splunk-appinspect inspect splunk_ta_deceptionlogic.tar.gz

lint:
	.env/bin/ruff format splunk_ta_deceptionlogic/bin/spl_deceptionlogic_alerts.py
	.env/bin/ruff format splunk_ta_deceptionlogic/bin/spl_deceptionlogic_events.py
	.env/bin/ruff check splunk_ta_deceptionlogic/bin/spl_deceptionlogic_alerts.py
	.env/bin/ruff check splunk_ta_deceptionlogic/bin/spl_deceptionlogic_events.py

clean:
	-rm splunk_ta_deceptionlogic.tar.gz
	-rm splunk-appinspect-latest.tar.gz
	-rm -rf .env
