#!/bin/python

# import code
# code.interact(local=locals())
import os
import requests
import sys
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from configparser import ConfigParser


class HqApi(object):
    def __init__(self, base_url, domain, version, username, password):
        self._username = username
        self._password = password
        self._api_version = version
        self._domain = domain
        self._base_url = base_url
        self._domain_url = "{0}/a/{1}/api/{2}".format(base_url,
                                                      domain, version)

    # None -> [List-of JSON]
    def get_cases(self):
        cases = self.get_request(self._domain_url, "case")
        return cases["objects"]

    # String -> JSON
    def get_case(self, case_id):
        return self.get_request(self._domain_url, "case/{}".format(case_id))

    # None -> [List-of JSON]
    def get_forms(self):
        forms = self.get_request(self._domain_url, "form")
        return forms["objects"]

    # String -> JSON
    def get_form(self, form_id):
        return self.get_request(self._domain_url, "form/{}".format(form_id))

    # None -> [List-of JSON]
    def get_groups(self):
        forms = self.get_request(self._domain_url, "group")
        return forms["objects"]

    # None -> [List-of JSON]
    def get_mobile_workers(self):
        return self.get_request(self._domain_url, "user")

    # String -> JSON
    def get_mobile_worker(self, user_id):
        return self.get_request(self._domain_url, "user/{}".format(user_id))

    # None -> [List-of JSON]
    def get_web_users(self):
        return self.get_request(self._domain_url, "web-user")

    # String -> JSON
    def get_web_user(self, user_id):
        return self.get_request(self._domain_url,
                                "web-user/{}".format(user_id))

    # None -> JSON
    def get_application_structure(self):
        return self.get_request(self._domain_url, "application")

    # None -> JSON
    def get_fixtures(self):
        return self.get_request(self._domain_url, "fixture")

    # String -> JSON
    def get_fixture(self, fixture_type):
        # TODO
        print(fixture_type)
        return self.get_request(self._domain_url, "fixture")

    # None -> JSON
    def get_fixture_item(self, fixture_id):
        return self.get_request(self._domain_url,
                                "fixture/{}".format(fixture_id))

    # Filename -> None
    def upload_fixture(self, filename):
        file_data = {'file-to-upload':
                     (filename, open(filename, 'rb'), 'multipart/form-data')}
        url = "{0}/a/{1}/fixtures/fixapi/".format(self._base_url, self._domain)
        r = requests.post(
            url=url,
            files=file_data,
            data={'replace': 'true'},
            auth=HTTPDigestAuth(self._username, self._password)
        )
        return r

    # String -> JSON
    def get_request(self, domain, action):
        url = "{0}/{1}/".format(domain, action)
        r = requests.get(
            url=url,
            auth=HTTPBasicAuth(self._username, self._password))

        if r.status_code == 200:
            return r.json()
        else:
            error_msg = "Request {0} failed (code {1})".format(url,
                                                               r.status_code)
            raise Exception(error_msg)


# None -> String
def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def main():
    config = ConfigParser()
    config.read(get_script_path() + "/auth.conf")

    BASE_URL = config.get('Server', 'url')
    DOMAIN = config.get('Server', 'project_space')
    USERNAME = config.get('Server', 'user')
    PASSWORD = config.get('Server', 'password')

    VERSION = "v0.5"
    hq_api = HqApi(BASE_URL, DOMAIN, VERSION, USERNAME, PASSWORD)
    if len(sys.argv) > 3:
        filename = sys.argv[0]
        arg_count = len(sys.argv) - 1
        print("{} only accepts one argument, {} provided".format(filename,
                                                                 arg_count))
        sys.exit(0)

    dispatch_command(sys.argv[1:], hq_api)


# [List-of String] HqApi -> None
def dispatch_command(args, hq_api):
    command = args[0]

    if command == 'upload_fixture':
        filename = args[1]
        print(filename)
        if hq_api.upload_fixture(filename).status_code != 200:
            sys.exit(1)
    elif command == 'cases':
        print(hq_api.get_cases())
    elif command == 'case':
        case_id = args[1]
        print(hq_api.get_case(case_id))
    elif command == 'forms':
        hq_api.get_forms()
    elif command == 'form':
        form_id = args[1]
        print(hq_api.get_form(form_id))
    elif command == 'help':
        print("")
    sys.exit(0)

if __name__ == "__main__":
    main()
