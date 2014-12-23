#!/usr/bin/env python
#
# $ python $0 host:port database user password s3_bucket_name slack_incoming_webhook_url

import sys
import os
import json
from datetime import datetime

host_port = sys.argv[1]
database = sys.argv[2]
user = sys.argv[3]
password = sys.argv[4]
s3_bucket_name = sys.argv[5]
slack_incoming_webhook_url = sys.argv[6]

job_url = os.environ.get('JOB_URL')

# Create dump directory
cmd = 'mkdir -p dump'
print cmd
exitcode = os.system(cmd)
if exitcode != 0:
    payload = json.dumps({'text': 'Command failed: %s' % (cmd)})
    os.system("curl -s -X POST --data-urlencode 'payload=%s' %s" % (payload, slack_incoming_webhook_url))
    raise

# get latest dump
cmd = 's3cmd -r get s3://%s/dump/ dump/' % (s3_bucket_name)
print cmd
exitcode = os.system(cmd)
if exitcode != 0:
    payload = json.dumps({'text': 'Command failed: %s' % (cmd)})
    os.system("curl -s -X POST --data-urlencode 'payload=%s' %s" % (payload, slack_incoming_webhook_url))
    raise

# mongorestore
target_dir = os.listdir('dump')[0]
dump_dir = 'dump/%s' % (target_dir)
cmd = 'mongorestore --drop -h %s -d %s -u %s -p %s %s' % (host_port, database, user, password, dump_dir)
print cmd
exitcode = os.system(cmd)
if exitcode != 0:
    payload = json.dumps({'text': 'Command failed: mongorestore'})
    os.system("curl -s -X POST --data-urlencode 'payload=%s' %s" % (payload, slack_incoming_webhook_url))
    raise

# notify to slack
payload = json.dumps({'text': 'mongorestore Success %s' % job_url})
os.system("curl -s -X POST --data-urlencode 'payload=%s' %s" % (payload, slack_incoming_webhook_url))
