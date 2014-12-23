#!/usr/bin/env python
#
# $ python $0 heroku_app_name slack_incoming_webhook_url

import commands
import os
import sys
import json

heroku_app_name = sys.argv[1]
slack_incoming_webhook_url = sys.argv[2]

cmd = "heroku pipeline:promote -a %s" % (heroku_app_name)
print cmd
out = commands.getoutput(cmd)
print out

payload = json.dumps({'text': out})
os.system("curl -s -X POST --data-urlencode 'payload=%s' %s" % (payload, slack_incoming_webhook_url))
