import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "https://www.commcarehq.org"


# Same as
#   curl --request POST -F xml_submission_file=@file.xml
#   /a/your-domain/receiver -v -u
#   username@your-domain.commcarehq.org:password
def submit_form(filename, username, password, domain):
    """
    Performs submission of xml file to CommCareHQ using basic auth
    """
    file_data = {'xml_submission_file':
                 (filename, open(filename, 'rb'), 'multipart/form-data')}
    url = "{0}/a/{1}/receiver/".format(BASE_URL, domain)
    if "@" not in username:
        # user is a web worker, so include proper domain
        username = "{}@{}.commcarehq.org".format(username, domain)
    r = requests.post(
        url=url,
        files=file_data,
        auth=HTTPBasicAuth(username, password)
    )
    return r.status_code


# Same as above, but submits to the url that includes app id, which is what usual form
# submissions from mobile use. This is probably preferable when app id is available
def submit_form_with_app_id(filename, username, password, domain, app_id):
    """
    Performs submission of xml file to CommCareHQ using basic auth
    """
    file_data = {'xml_submission_file':
                 (filename, open(filename, 'rb'), 'multipart/form-data')}
    url = "{0}/a/{1}/receiver/secure/{2}/".format(BASE_URL, domain, app_id)
    if "@" not in username:
        # user is a web worker, so include proper domain
        username = "{}@{}.commcarehq.org".format(username, domain)
    r = requests.post(
        url=url,
        files=file_data,
        auth=HTTPBasicAuth(username, password)
    )
    return r.status_code
