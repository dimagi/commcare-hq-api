from datetime import datetime
import commcare_hq_api
import sys
import os
from form_submission.case_close import submit_case_close

HELP_MSG = """
store_latest_form: Store the submission time of latest form in a text file
assert_newer_form: Assert that lastest form submission is newer than last call
                   to 'store_latest_form'
assert_attachments count: Assert latest form has the expected attachment count
assert_group_membership user_id group_id: Assert user is a member of a given
                                          group
set_user_group user_id group_id: Add a user to a group
close_case_named name: Close the first case with the provided name
help: show this message
"""

DATETIME_PATTERN = "%Y-%m-%dT%H:%M:%S.%fZ"
LATEST_FORM_FILE = "latest_form_time.txt"


# HqApi -> Integer
def get_latest_form_time(hq_api):
    date_str = hq_api.get_forms()[0]['received_on']
    return int(datetime.strptime(date_str, DATETIME_PATTERN).timestamp())


# HqApi -> Integer
def get_latest_form_attachment_count(hq_api):
    form = hq_api.get_forms()[0]
    form_id = form['id']
    attachments = form['attachments']
    attachments_with_data = 0
    for attachment_name in attachments:
        file_size = len(hq_api.get_attachment(form_id, attachment_name))
        attachments_with_data += int(file_size > 0)
    return attachments_with_data


# HqApi String -> None
def close_case_with_name(hq_api, name):
    """
    Close first case found in case list that satisfies the predicate.
    """
    cases_with_name = hq_api.get_cases(params={"name": name})
    if len(cases_with_name) != 0:
        case_id = cases_with_name[0]['case_id']
        response_code = submit_case_close(hq_api._domain, hq_api._username,
                                          hq_api._password, case_id)
        if response_code >= 200 and response_code < 300:
            print("Successfully closed {} case".format(case_id))
            sys.exit(0)
        else:
            print(("Unable to close {} case"
                   ", HTTP code {}").format(case_id, response_code))
            sys.exit(1)
    else:
        print("Couldn't find case that satisfies the predicate")
        sys.exit(1)


# String -> [String]
def get_groups_for_user(hq_api, USER_ID):
    user_json = hq_api.get_mobile_worker(USER_ID)
    return user_json['groups']


def assert_new_form_on_hq(hq_api):
    if not os.path.exists(LATEST_FORM_FILE):
        print("Couldn't find {} file".format(LATEST_FORM_FILE))
        sys.exit(1)
    else:
        with open(LATEST_FORM_FILE, 'r') as form_file:
            old_form_submit_time = int(form_file.readline())
            if old_form_submit_time >= get_latest_form_time(hq_api):
                print("No new forms submitted since last check")
                sys.exit(1)


def assert_group_membership(hq_api, user_id, group_id):
    if group_id not in get_groups_for_user(hq_api, user_id):
        sys.exit(1)


def set_user_group(hq_api, user_id, group_id):
    if group_id == "[]":
        hq_api.update_mobile_worker(user_id, '{"groups": []}')
    else:
        hq_api.update_mobile_worker(
            user_id,
            '{"groups": ["' + group_id + '"]}')


def dispatch_command(args, hq_api):
    command = args[0]

    def store_latest_form_time():
        with open(LATEST_FORM_FILE, 'w') as form_file:
            form_file.write(str(get_latest_form_time(hq_api)))

    # Integer -> None
    def assert_attachments(expected_count):
        attachment_count = get_latest_form_attachment_count(hq_api)
        if expected_count != attachment_count:
            print("{} attachments expected, {} found".format(expected_count,
                                                             attachment_count))
            sys.exit(1)

    dispatch = {
        'store_latest_form': lambda: store_latest_form_time(),
        'assert_newer_form': lambda: assert_new_form_on_hq(hq_api),
        'assert_attachments': lambda: assert_attachments(int(args[1])),
        'assert_group_membership': lambda: assert_group_membership(hq_api, args[1], args[2]),
        'set_user_group': lambda: set_user_group(hq_api, args[1], args[2]),
        'close_case_named': lambda: close_case_with_name(hq_api, args[1]),
        'help': lambda: HELP_MSG
    }
    print(dispatch[command]())

    sys.exit(0)


def main():
    if len(sys.argv) > 4:
        filename = sys.argv[0]
        arg_count = len(sys.argv) - 1
        print("{} only accepts 2 arguments, {} provided".format(filename,
                                                                arg_count))
        sys.exit(0)
    hq_api = commcare_hq_api.build()

    dispatch_command(sys.argv[1:], hq_api)


if __name__ == "__main__":
    main()
