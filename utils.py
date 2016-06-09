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
        attachments_with_data += int(len(hq_api.get_attachment(form_id, attachment_name)) > 0)
    return attachments_with_data


def main():
    if len(sys.argv) > 3:
        filename = sys.argv[0]
        arg_count = len(sys.argv) - 1
        print("{} only accepts one argument, {} provided".format(filename,
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

    def assert_attachments(expected_count):
        attachment_count = get_latest_form_attachment_count(hq_api)
        if expected_count != attachment_count:
            print("{} attachments expected, {} found".format(expected_count,
                                                             attachment_count))
            sys.exit(1)

    dispatch = {'store_latest_form': lambda: store_latest_form_time(),
                'assert_newer_form': lambda: assert_new_form_on_hq(),
                'assert_attachments': lambda: assert_attachments(args[1]),
                'help': lambda: ""}
    print(dispatch[command]())

    sys.exit(0)

if __name__ == "__main__":
    main()
