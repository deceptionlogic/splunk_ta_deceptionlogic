package:
	tar -czf splunk_ta_deceptionlogic.tar.gz splunk_ta_deceptionlogic

inspect:
	wget https://download.splunk.com/misc/appinspect/splunk-appinspect-latest.tar.gz
	virtualenv .env
	.env/bin/pip install splunk-appinspect-latest.tar.gz
	.env/bin/splunk-appinspect inspect splunk_ta_deceptionlogic.tar.gz	

clean:
	-rm splunk_ta_deceptionlogic.tar.gz
	-rm splunk-appinspect-latest.tar.gz
	-rm -rf .env
