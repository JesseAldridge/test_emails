import os, subprocess, json, glob, shutil

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import config

# It's an invalid ssl cert, but we're just testing locally so it's fine
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

headers = {'content-type': 'application/json'}

responses_dir = os.path.expanduser('~/Desktop/responses')
if not os.path.exists(responses_dir):
  os.makedirs(responses_dir)

for test_dict in [
  {'endpoint': 'send_reminders', 'filename': 'confirmed_no_timezone.json'},
  {'endpoint': 'send_reminders', 'filename': 'confirmed_no_phone.json'},
  {'endpoint': 'send_reminders', 'filename': 'confirmed.json'},
  {'endpoint': 'created', 'filename': 'confirmed.json'},
  {'endpoint': 'canceled_by_host', 'filename': 'confirmed.json'},
  {'endpoint': 'canceled_by_partner', 'filename': 'confirmed.json'},
]:
  filename = test_dict.get('filename')
  endpoint = test_dict.get('endpoint')

  with open(os.path.join('timekit_data', filename)) as f:
    json_text = f.read()
  data = json.loads(json_text)

  url = '{}/collections_application/booking/{}'.format(config.base_url, endpoint)
  print 'posting to: {} with test file: {}'.format(url, filename)
  resp = requests.post(url, json=data, headers=headers, verify=False)
  with open(os.path.join(responses_dir, endpoint) + '.html', 'w') as f:
    f.write(resp.content)
  assert resp.status_code == 200

print 'rsyncing emails...'

local_emails_path = os.path.expanduser(config.local_emails_path)
remote_emails_path = config.remote_emails_path
if not remote_emails_path.endswith('/'):
  remote_emails_path += '/'

command_line = 'rsync -t {}@{}:{}* {}'.format(
  config.user_name, config.host_name, remote_emails_path, local_emails_path)
command_list = command_line.split()
subprocess.call(command_list)

for old_path in glob.glob(os.path.join(local_emails_path, '*.eml')):
  new_path = old_path.rsplit('.', 1)[0] + '.html'
  shutil.move(old_path, new_path)
