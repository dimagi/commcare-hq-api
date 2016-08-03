from datetime import datetime
import commcare_hq_api
import sys
import os

DATETIME_PATTERN = "%Y-%m-%dT%H:%M:%S.%f"
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


# String -> [String]
def get_groups_for_user(hq_api, USER_ID):
    user_json = hq_api.get_mobile_worker(USER_ID)
    return user_json['groups']


def main():
    if len(sys.argv) > 4:
        filename = sys.argv[0]
        arg_count = len(sys.argv) - 1
        print("{} only accepts 2 arguments, {} provided".format(filename,
                                                                 arg_count))
        sys.exit(0)
    hq_api = commcare_hq_api.build()

    dispatch_command(sys.argv[1:], hq_api)


def dispatch_command(args, hq_api):
    command = args[0]

    def store_latest_form_time():
        with open(LATEST_FORM_FILE, 'w') as form_file:
            form_file.write(str(get_latest_form_time(hq_api)))

    def assert_new_form_on_hq():
        if not os.path.exists(LATEST_FORM_FILE):
            print("Couldn't find {} file".format(LATEST_FORM_FILE))
            sys.exit(1)
        else:
            with open(LATEST_FORM_FILE, 'r') as form_file:
                old_form_submit_time = int(form_file.readline())
                if old_form_submit_time >= get_latest_form_time(hq_api):
                    print("No new forms submitted since last check")
                    sys.exit(1)

    # Integer -> None
    def assert_attachments(expected_count):
        attachment_count = get_latest_form_attachment_count(hq_api)
        if expected_count != attachment_count:
            print("{} attachments expected, {} found".format(expected_count,
                                                             attachment_count))
            sys.exit(1)
    

    def assert_group_membership(USER_ID, GROUP_ID):
        if GROUP_ID not in get_groups_for_user(hq_api, USER_ID):
            sys.exit(1)


    def set_user_group(USER_ID, GROUP_ID):
        if GROUP_ID == "[]":
            hq_api.update_mobile_worker(USER_ID, '{"groups": []}')
        else:
            hq_api.update_mobile_worker(USER_ID, '{"groups": ["' +  GROUP_ID + '"]}')
        

    dispatch = {'store_latest_form': lambda: store_latest_form_time(),
                'assert_newer_form': lambda: assert_new_form_on_hq(),
                'assert_attachments': lambda: assert_attachments(int(args[1])),
                'assert_group_membership': lambda: assert_group_membership(args[1], args[2]),
                'set_user_group': lambda: set_user_group(args[1], args[2]),
                'help': lambda: ""}
    print(dispatch[command]())

    sys.exit(0)

if __name__ == "__main__":
    main()
