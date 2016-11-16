#!/bin/python

# import code
# code.interact(local=locals())
import os
import requests
import sys
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from configparser import ConfigParser
import json

HELP_MSG = """
cases: show the most 20 recent cases
case id: get the case associated with the given id
forms: show the most recent forms
form id: get the form associated with the given id
attachment form_id attachment_id: downloads the form attachment
upload_fixture fixture.xls: uploads the excel file as a fixutre
users: gets mobile workers
user user_id: gets mobile worker associated with the given id
user_delete user_id: delete the mobile worker
change_password user_id new_password: update password for mobile worker
help: show this message
"""


class HqApi(object):
    def __init__(self, base_url, domain, version, username, password):
        self._username = username
        self._password = password
        self._api_version = version
        self._domain = domain
        self._base_url = base_url
        self._domain_url = "{0}/a/{1}/api".format(base_url, domain)

    # None -> [List-of JSON]
    def get_cases(self, params={}):
        cases = self.get_request(self._domain_url, "case", query_params=params)
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

    # String -> ?
    def get_attachment(self, form_id, attachment_name):
        attachment_url = "form/attachment/{}/{}".format(form_id,
                                                        attachment_name)
        return self.get_request(self._domain_url, attachment_url,
                                include_version=False,
                                unpack_fn=lambda r: r.content)

    # None -> [List-of JSON]
    def get_groups(self):
        forms = self.get_request(self._domain_url, "group")
        return forms["objects"]

    # None -> [List-of JSON]
    def get_mobile_workers(self):
        return self.get_request(self._domain_url, "user")

    # String -> JSON
    def get_mobile_worker(self, user_id):
        return self.get_request(self._domain_url,
                                "user/{}/?format=json".format(user_id))

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

    def update_mobile_worker(self, user_id, payload):
        url = "{0}/{1}/user/{2}/".format(self._domain_url,
                                         self._api_version,
                                         user_id)
        response = requests.put(
            url=url,
            data=payload,
            headers={'content-type': 'application/json'},
            auth=HTTPBasicAuth(self._username, self._password))
        return response

    def create_mobile_worker(self, username, password):
        url = "{0}/{1}/user/".format(self._domain_url,
                                     self._api_version)
        domained_username = "{0}@{1}.commcarehq.org".format(username,
                                                            self._domain)
        data = {
            "username": domained_username,
            "password": password,
            "first_name": "Temporary",
            "last_name": "User",
        }
        response = requests.post(
            url=url,
            json=data,
            headers={'content-type': 'application/json'},
            auth=HTTPBasicAuth(self._username, self._password))
        if response.status_code >= 200 and response.status_code < 300:
            print("Sucessfully created worker with username ", username)
            return response
        else:
            raise Exception("Unable to create worker with username ", username)

    def delete_mobile_worker(self, user_id):
        url = "{0}/{1}/user/{2}/".format(self._domain_url,
                                         self._api_version,
                                         user_id)
        response = requests.delete(
            url=url,
            auth=HTTPBasicAuth(self._username, self._password))
        if response.status_code >= 200 and response.status_code < 300:
            print("Successfully deleted worker with user_id ", user_id)
            return response
        else:
            raise Exception("Unable to delete worker with user_id ", user_id)

    def delete_worker_named(self, username):
        workers = self.get_mobile_workers()
        domained_username = "{0}@{1}.commcarehq.org".format(username,
                                                            self._domain)
        matching_ids = [worker.get('id') for worker in workers.get('objects') if worker.get('username') == domained_username]
        if len(matching_ids) != 1:
            raise Exception("Username {0} matched {1} workers".format(domained_username, matching_ids))
        user_id = matching_ids[0]
        return self.delete_mobile_worker(user_id)


    def password_update(self, user_id, new_password):
        password_payload = '{"password": "' + new_password + '"}'
        return self.update_mobile_worker(user_id, password_payload)

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
    def get_request(self, domain, action,
                    query_params={},
                    include_version=True,
                    unpack_fn=lambda r: r.json()):
        if include_version:
            url = "{0}/{1}/{2}".format(domain, self._api_version, action)
        else:
            url = "{0}/{1}".format(domain, action)
        query = "&".join([k + "=" + v for k, v in query_params.items()])
        if query is not "":
            url += "?" + query

        r = requests.get(
            url=url,
            auth=HTTPBasicAuth(self._username, self._password))

        if r.status_code == 200:
            return unpack_fn(r)
        else:
            error_msg = "Request {0} failed (code {1})".format(url,
                                                               r.status_code)
            raise Exception(error_msg)


# None -> String
def get_script_path():
    base_path = os.path.realpath(sys.argv[0])
    if os.path.isdir(base_path):
        return base_path
    else:
        return os.path.dirname(base_path)


def build():
    config = ConfigParser()
    config_file = os.path.join(get_script_path(), "auth.conf")
    config.read(config_file)

    BASE_URL = config.get('Server', 'url')
    DOMAIN = config.get('Server', 'project_space')
    USERNAME = config.get('Server', 'user')
    PASSWORD = config.get('Server', 'password')

    VERSION = "v0.5"
    return HqApi(BASE_URL, DOMAIN, VERSION, USERNAME, PASSWORD)


def main():
    if len(sys.argv) > 4:
        filename = sys.argv[0]
        arg_count = len(sys.argv) - 1
        print("{} only accepts one argument, {} provided".format(filename,
                                                                 arg_count))
        sys.exit(0)
    hq_api = build()

    dispatch_command(sys.argv[1:], hq_api)


# [List-of String] HqApi -> None
def dispatch_command(args, hq_api):
    command = args[0]

    def upload_fixture_and_exit(filename):
        sys.exit(int(hq_api.upload_fixture(filename).status_code != 200))

    def download_attachment(form_id, attachment_name):
        attachment_bytes = hq_api.get_attachment(form_id, attachment_name)
        with open(attachment_name, 'wb') as f:
            f.write(attachment_bytes)

    dispatch = {'case': lambda: hq_api.get_case(args[1]),
                'cases': lambda: hq_api.get_cases(),
                'forms': lambda: hq_api.get_forms(),
                'form': lambda: hq_api.get_form(args[1]),
                'attachment': lambda: download_attachment(args[1], args[2]),
                'upload_fixture': lambda: upload_fixture_and_exit(args[1]),
                'user_create': lambda: hq_api.create_mobile_worker(args[1], args[2]),
                'user_delete': lambda: hq_api.delete_mobile_worker(args[1]),
                'change_password': lambda: hq_api.password_update(*args[1:]),
                'users': lambda: hq_api.get_mobile_workers(),
                'user': lambda: hq_api.get_mobile_worker(args[1]),
                'help': lambda: HELP_MSG,
                'delete_worker_named': lambda: hq_api.delete_worker_named(args[1])}

    print(dispatch[command]())

    sys.exit(0)


if __name__ == "__main__":
    main()
