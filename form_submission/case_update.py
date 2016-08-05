#!/bin/python3

"""
Script for posting a form to CommCareHQ that updates a case.

example usage:
python3 submit_case_update.py your-commcare-domain mobile-user1 passwd 123-this-is-a-case-id-456 prop1=new-value prop2="value with spaces"
"""

import datetime
import uuid
import sys
from utils import submit_form

ISO_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
SYSTEM_FORM_XMLNS = 'http://commcarehq.org/case'
SYSTEM_USER_ID = 'system'
SUBMISSION_FILENAME = "submission.xml"

HELP_MESSAGE = """
Script has 4 required arguments and unlimited optional case property arguments:
  domain: the projects domain name on CommCareHQ
  username: the mobile worker's username, used to submit the form
  password: the mobile worker's password
  case_id: id of case being updated
  key=value: case property added or updated (there can be multiple of these)
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
      <update>
{case_properties_block}
      </update>
    </case>
</system>
"""


# String String String String [Dict-of String String] -> None
def create_submission_file(filename, case_id, username,
                           user_id, case_properties):
    submission_contents = format_update_form(case_id, username,
                                             user_id, case_properties)
    with open(filename, "w") as f:
        f.write(submission_contents)


# String String String [Dict-of String String] -> String
def format_update_form(case_id, username, user_id, case_properties):
    """
    Fill-in the case update form template to create a valid xml form
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
        'case_properties_block': render_case_properties(case_properties)
    }

    return XML_TEMPLATE.format(**context)


# [Dict-of String String] -> String
def render_case_properties(case_properties):
    props = ""
    property_template = "        <{key}>{value}</{key}>\n"
    for key, value in case_properties.items():
        props += property_template.format(key=key, value=value)
    return props


# [List-of String] -> [Dict-of String String]
def parse_properties(args):
    """
    Parses strings of form "key=value" into a dictionary
    """
    props = {}
    for prop in args:
        index = prop.index("=")
        if index > 0 and index + 1 < len(prop):
            key = prop[:index]
            value = prop[index+1:]
            props[key] = value
        else:
            print("invalid case property '{}'".format(prop))
            sys.exit(1)

    return props


# String String String String [Dict-of String String] -> Integer
def submit_case_update(domain, username, password, case_id, props):
    """
    Posts a form to CommCareHQ that updates a case with provided properties
    """
    create_submission_file(SUBMISSION_FILENAME, case_id,
                           username, SYSTEM_USER_ID, props)
    response_code = submit_form(SUBMISSION_FILENAME, username,
                                password, domain)
    return response_code


def main():
    if len(sys.argv) < 5:
        print(HELP_MESSAGE)
        sys.exit(0)

    domain = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    case_id = sys.argv[4]
    props = parse_properties(sys.argv[5:])
    response_code = submit_case_update(domain, username,
                                       password, case_id, props)

    prop_key_str = ", ".join(props.keys())
    info_message = ("Updating {} as {}@{} with the following case properties" +
                    ": {}").format(case_id, username, domain, prop_key_str)

    if response_code >= 200 and response_code < 300:
        print(info_message)
        sys.exit(0)
    else:
        print("failed with HTTP code {}".format(response_code))
        sys.exit(1)


if __name__ == "__main__":
    main()
