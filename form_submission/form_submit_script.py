#!/bin/python3

"""
Script for submitting any form to CommCareHQ.
"""

from utils import submit_form, submit_form_with_app_id
import sys

def main():
    arg_count = len(sys.argv) - 1
    if arg_count == 4:
        response = submit_form(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    elif arg_count == 5:
        response = submit_form_with_app_id(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        print("Form Submission script accepts either 4 or 5 arguments: filename, username, password, domain, and optionally app_id")
        sys.exit(0)
    print(response)


if __name__ == "__main__":
    main()