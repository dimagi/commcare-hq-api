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

    if command == 'store_latest_form':
        with open(LATEST_FORM_FILE, 'w') as form_file:
            form_file.write(str(get_latest_form_time(hq_api)))
    elif command == 'assert_newer_form':
        if not os.path.exists(LATEST_FORM_FILE):
            print("Couldn't find {} file".format(LATEST_FORM_FILE))
            sys.exit(1)
        else:
            with open(LATEST_FORM_FILE, 'r') as form_file:
                old_form_submit_time = int(form_file.readline())
                if old_form_submit_time >= get_latest_form_time(hq_api):
                    print("No new forms submitted since last check")
                    sys.exit(1)

    elif command == 'help':
        print("")
    sys.exit(0)

if __name__ == "__main__":
    main()
