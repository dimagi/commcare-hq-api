#!/bin/python3

"""
Script for posting a case close form to CommCareHQ.

example usage:
python3 submit_case_close.py your-commcare-domain mobile-user1 passwd case-id
"""

import datetime
import uuid
import sys
from form_submission.utils import submit_form

ISO_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
SYSTEM_FORM_XMLNS = 'http://commcarehq.org/case'
SYSTEM_USER_ID = 'system'
SUBMISSION_FILENAME = "case_close.xml"

HELP_MESSAGE = """
Script has 4 required arguments:
  domain: the projects domain name on CommCareHQ
  username: the mobile worker's username, used to submit the form
  password: the mobile worker's password
  case_id: id of case being updated
"""

XML_TEMPLATE = """<?xml version='1.0' ?>
<system version="1" uiVersion="1" xmlns="{xmlns}"
        xmlns:orx="http://openrosa.org/jr/xforms">
    <orx:meta xmlns:cc="http://commcarehq.org/xforms">
        <orx:deviceID />
        <orx:timeStart>{time}</orx:timeStart>
        <orx:timeEnd>{time}</orx:timeEnd>
        <orx:username>{username}</orx:username>
        <orx:userID>{user_id}</orx:userID>
        <orx:instanceID>{uid}</orx:instanceID>
        <cc:appVersion />
    </orx:meta>
    <case case_id="{case_id}"
          date_modified="{date_modified}"
          user_id="{user_id}"
          xmlns="http://commcarehq.org/case/transaction/v2">
          <close/>
    </case>
</system>
"""


# String String String String -> None
def create_submission_file(filename, case_id, username, user_id):
    submission_contents = format_update_form(case_id, username, user_id)
    with open(filename, "w") as f:
        f.write(submission_contents)


# String String String -> String
def format_update_form(case_id, username, user_id):
    """
    Fill-in the case close form template to create a valid xml form
    """
    now = datetime.datetime.utcnow().strftime(ISO_DATETIME_FORMAT)
    form_id = uuid.uuid4().hex
    context = {
        'xmlns': SYSTEM_FORM_XMLNS,
        'time': now,
        'uid': form_id,
        'username': username,
        'user_id': user_id,
        'case_id': case_id,
        'date_modified': now,
        'user_id': SYSTEM_USER_ID,
    }

    return XML_TEMPLATE.format(**context)


# String String String String -> Integer
def submit_case_close(domain, username, password, case_id):
    """
    Posts a form to CommCareHQ that closes a case
    """
    create_submission_file(SUBMISSION_FILENAME, case_id,
                           username, SYSTEM_USER_ID)
    response_code = submit_form(SUBMISSION_FILENAME, username,
                                password, domain)

    return response_code


def main():
    if len(sys.argv) < 4:
        print(HELP_MESSAGE)
        sys.exit(0)

    domain = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    case_id = sys.argv[4]
    response_code = submit_case_close(domain, username, password, case_id)

    if response_code >= 200 and response_code < 300:
        info_message = "Closing {} as {}@{}".format(case_id, username, domain)
        print(info_message)
        sys.exit(0)
    else:
        print("failed with HTTP code {}".format(response_code))
        sys.exit(1)


if __name__ == "__main__":
    main()
