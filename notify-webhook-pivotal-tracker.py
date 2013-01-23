#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import urllib, urllib2
import re
import os
import subprocess
from dict2xml2 import dict2xml2
from datetime import datetime


def git(args):
    args = ['git'] + args
    git = subprocess.Popen(args, stdout = subprocess.PIPE)
    details = git.stdout.read()
    details = details.strip()
    return details

def get_config(key):
    details = git(['config', '%s' % (key)])
    if len(details) > 0:
        return details
    else:
        return None

def get_repo_name():
    if git(['rev-parse','--is-bare-repository']) == 'true':
        name = os.path.basename(os.getcwd())
        if name.endswith('.git'):
            name = name[:-4]
        return name
    else:
        return os.path.basename(os.path.dirname(os.getcwd()))

POST_URL = get_config('hooks.webhookurl')
REPO_URL = get_config('meta.url')
authtok = get_config('meta.apikey')
COMMIT_URL = get_config('meta.commiturl')
if COMMIT_URL == None and REPO_URL != None:
    COMMIT_URL = REPO_URL + r'/commit/%s'
REPO_NAME = get_repo_name()
REPO_DESC = ""
try:
    REPO_DESC = get_config('meta.description') or open('description', 'r').read()
except Exception:
    pass
REPO_OWNER_NAME = get_config('meta.ownername')
REPO_OWNER_EMAIL = get_config('meta.owneremail')
if REPO_OWNER_NAME is None:
    REPO_OWNER_NAME = git(['log','--reverse','--format=%an']).split("\n")[0]
if REPO_OWNER_EMAIL is None:
    REPO_OWNER_EMAIL = git(['log','--reverse','--format=%ae']).split("\n")[0]

EMAIL_RE = re.compile("^(.*) <(.*)>$")

def get_revisions(old, new):
    git = subprocess.Popen(['git', 'rev-list', '--pretty=medium', '--reverse', '%s..%s' % (old, new)], stdout=subprocess.PIPE)
    sections = git.stdout.read().split('\n\n')[:-1]

    revisions = []
    s = 0
    while s < len(sections):
        lines = sections[s].split('\n')

        # first line is 'commit HASH\n'
        props = {'id': lines[0].strip().split(' ')[1]}

        # read the header
        for l in lines[1:]:
            key, val = l.split(' ', 1)
            props[key[:-1].lower()] = val.strip()

        # read the commit message
        props['message'] = sections[s+1]

        # use github time format
        basetime = datetime.strptime(props['date'][:-6], "%a %b %d %H:%M:%S %Y")
        tzstr = props['date'][-5:]
        props['date'] = basetime.strftime('%Y-%m-%dT%H:%M:%S') + tzstr

        # split up author
        m = EMAIL_RE.match(props['author'])
        if m:
            props['name'] = m.group(1)
            props['email'] = m.group(2)
        else:
            props['name'] = 'unknown'
            props['email'] = 'unknown'
        del props['author']

        revisions.append(props)
        s += 2

    return revisions

def make_json(old, new, ref, POST_URL, authtok):
    data = {
        'before': old,
        'after': new,
        'ref': ref,
        'repository': {
            'url': REPO_URL,
            'name': REPO_NAME,
            'description': REPO_DESC,
            'owner': {
                'name': REPO_OWNER_NAME,
                'email': REPO_OWNER_EMAIL
                }
            }
        }

    revisions = get_revisions(old, new)
    
    for r in revisions:
        url = None
        if COMMIT_URL != None:
            url = COMMIT_URL % r['id']
      
	commits = {
	     'source_commit': {
	     'message': r['message'],
	     'author': r['name'],
	     'commit_id': r['id'],
	     'url' : url
		}
	     }
	    
	if POST_URL:
	  post(POST_URL, dict2xml2(commits, False, False),authtok)
 


def post(url, data,authtok):
#    request = urllib2.Request(headers={"X-TrackerToken": authtok})
#    u = urllib2.urlopen(request, urllib.urlencode({'payload': data}))

    request = urllib2.Request(POST_URL, data=data, headers={'Content-Type':'application/xml'})
    request.add_header('X-TrackerToken',authtok)
    request.add_header('Content-Type','application/xml')
    request.headers


    u = urllib2.urlopen(request)
    u.read()
    u.close()






if __name__ == '__main__':
    for line in sys.stdin.xreadlines():
        old, new, ref = line.strip().split(' ')
        data = make_json(old, new, ref, POST_URL, authtok)
