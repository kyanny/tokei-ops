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

now = datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')
archive_dir = 'archive/%s' % (now)

# Create archive directory
cmd = 'mkdir -p %s' % (archive_dir)
print cmd
exitcode = os.system(cmd)
if exitcode != 0:
    payload = json.dumps({'text': 'Command failed: %s' % (cmd)})
    os.system("curl -s -X POST --data-urlencode 'payload=%s' %s" % (payload, slack_incoming_webhook_url))
    raise

# mongodump
cmd = 'mongodump -h %s -d %s -u %s -p %s' % (host_port, database, user, password)
print cmd
exitcode = os.system(cmd)
if exitcode != 0:
    payload = json.dumps({'text': 'Command failed: mongodump'})
    os.system("curl -s -X POST --data-urlencode 'payload=%s' %s" % (payload, slack_incoming_webhook_url))
    raise

# copy dump to archive directory
cmd = 'cp -a dump %s' % (archive_dir)
print cmd
exitcode = os.system(cmd)
if exitcode != 0:
    payload = json.dumps({'text': 'Command failed: %s' % (cmd)})
    os.system("curl -s -X POST --data-urlencode 'payload=%s' %s" % (payload, slack_incoming_webhook_url))
    raise

# put latest dump
cmd = 's3cmd -r put dump/ s3://%s/dump/' % (s3_bucket_name)
print cmd
exitcode = os.system(cmd)
if exitcode != 0:
    payload = json.dumps({'text': 'Command failed: %s' % (cmd)})
    os.system("curl -s -X POST --data-urlencode 'payload=%s' %s" % (payload, slack_incoming_webhook_url))
    raise

# put archive directory
cmd = 's3cmd -r put %s/ s3://%s/%s/' % (archive_dir, s3_bucket_name, archive_dir)
print cmd
exitcode = os.system(cmd)
if exitcode != 0:
    payload = json.dumps({'text': 'Command failed: %s' % (cmd)})
    os.system("curl -s -X POST --data-urlencode 'payload=%s' %s" % (payload, slack_incoming_webhook_url))
    raise

# notify to slack
payload = json.dumps({'text': 'mongodump Success %s'% job_url})
os.system("curl -s -X POST --data-urlencode 'payload=%s' %s" % (payload, slack_incoming_webhook_url))
