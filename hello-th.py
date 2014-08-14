#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Hello, Treeherder!"""

from ConfigParser import ConfigParser
import hashlib
import json
import os
import sys
import time
import uuid

from thclient import TreeherderJobCollection
from thclient import TreeherderRequest
from thclient import TreeherderResultSetCollection


def get_config_filename():
    NAME = 'config.ini'

    if sys.argv[0]:
        my_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    else:
        # in interpreter
        my_dir = '.'

    return os.path.join(my_dir, NAME)


def get_oauth_creds():
    SECTION = 'Credentials'

    cfg = ConfigParser()
    cfg.read(get_config_filename())
    key = cfg.get(SECTION, 'key')
    secret = cfg.get(SECTION, 'secret')

    return (key, secret)


def get_repo_details():
    SECTION = 'Repo'

    cfg = ConfigParser()
    cfg.read(get_config_filename())
    project = cfg.get(SECTION, 'project')
    host = cfg.get(SECTION, 'host')

    return (project, host)


def create_revision_hash():
    sha = hashlib.sha1()
    sha.update(str(uuid.uuid4()))

    return sha.hexdigest()


def main():
    result_revision_hash = create_revision_hash()

    trsc = TreeherderResultSetCollection()

    trs = trsc.get_resultset()

    # self.required_properties = {
    #     'revision_hash':{ 'len':50, 'cb':self.validate_existence },
    #     'revisions':{ 'type':list, 'cb':self.validate_existence },
    #     'author':{ 'len':150, 'cb':self.validate_existence }
    #     }

    trs.add_revision_hash(result_revision_hash)
    trs.add_author('WebRTC QA Tests')
    trs.add_push_timestamp(int(time.time()))

    tr = trs.get_revision()

    # self.required_properties = {
    #     'revision':{ 'len':50, 'cb':self.validate_existence },
    #     'repository':{ 'cb':self.validate_existence },
    #     'files':{ 'type':list, 'cb':self.validate_existence },
    #     }

    tr.add_revision(create_revision_hash()[:12])
    tr.add_author('Firefox Nightly')
    tr.add_comment('firefox-33.0a1.en-US')
    tr.add_files(['firefox-33.0a1.en-US.linux-i686.tar.bz2',
                  'firefox-33.0a1.en-US.linux-x86_64.tests.zip'])
    tr.add_repository(
        'ftp://ftp.mozilla.org/pub/firefox/nightly/latest-mozilla-central/')
    trs.add_revision(tr)

    trsc.add(trs)

    tjc = TreeherderJobCollection()
    tj = tjc.get_job()

    # self.required_properties = {
    #     'revision_hash':{ 'len':50, 'cb':self.validate_existence },
    #     'project':{ 'cb':self.validate_existence },
    #     'job':{ 'type':dict, 'cb':self.validate_existence },
    #     'job.job_guid':{ 'len':50, 'cb':self.validate_existence }
    # }

    tj.add_revision_hash(result_revision_hash)
    tj.add_project('qa-try')
    tj.add_job_guid(str(uuid.uuid4()))

    tj.add_build_info('linux', 'linux64', 'x86_64')
    tj.add_description('WebRTC Sunny Day')
    tj.add_machine_info('linux', 'linux64', 'x86_64')
    tj.add_end_timestamp(int(time.time()) - 5)
    tj.add_start_timestamp(int(time.time()) - 3600 * 3 - 5)
    tj.add_submit_timestamp(int(time.time()) - 3600 * 3 - 10)
    tj.add_state('completed')
    tj.add_machine('webrtc-server')
    tj.add_option_collection({'opt': True})  # must not be {}!
    tj.add_reason('testing')
    tj.add_result('success')  # must be success/testfailed/busted
    tj.add_who('gmealer@mozilla.com')
    tj.add_group_name('WebRTC QA Tests')
    tj.add_group_symbol('WebRTC')
    tj.add_job_symbol('end')
    tj.add_job_name('Endurance')

    tj.add_artifact('Job Info', 'json', {
        "job_details": [
            {
                'title': 'Iterations:',
                'value': '10782',
                'content_type': 'text'
            },
            {
                'title': 'Errors:',
                'value': '5',
                'content_type': 'text'
            },
            {
                'title': 'Longest Pass Duration:',
                'value': '2:58:36.5',
                'content_type': 'text'
            }
        ],
    })

    tjc.add(tj)

    key, secret = get_oauth_creds()
    project, host = get_repo_details()

    req = TreeherderRequest(
        protocol='http',
        host=host,
        project=project,
        oauth_key=key,
        oauth_secret=secret
    )

    print 'trsc = ' + json.dumps(json.loads(trsc.to_json()), sort_keys=True,
                                 indent=4, separators=(',', ': '))

    print 'tjc = ' + json.dumps(json.loads(tjc.to_json()), sort_keys=True,
                                indent=4, separators=(',', ': '))

    # print 'req.oauth_key = ' + req.oauth_key
    # print 'req.oauth_secret = ' + req.oauth_secret

    # uri = req.get_uri(trsc)
    # print 'req.get_uri() = ' + uri
    # print 'req.oauth_client.get_signed_uri() = ' +
    # req.oauth_client.get_signed_uri(trsc.to_json(), uri)

    req.post(trsc)
    req.post(tjc)


if __name__ == '__main__':
    main()
