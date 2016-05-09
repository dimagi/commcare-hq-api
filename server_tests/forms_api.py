import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from config import BASE_URL, DOMAIN, \
    USERNAME, PASSWORD

DOMAIN_URL = "{0}/a/{1}".format(BASE_URL, DOMAIN)
FORMS_URL = "{0}/api/v0.5/form/".format(DOMAIN_URL)

# A FormId is a String


# FormId -> String
def get_form_url(form_id):
    return "{0}/{1}/".format(FORMS_URL, form_id)


# None -> [List-of FormId]
def get_latest_forms():
    forms = make_api_request(FORMS_URL)

    # TODO PLM: filter forms
    latest_forms = forms["objects"]

    return map(lambda form: form["id"], latest_forms)


def get_form_attachments(form_id):
    return


# String -> JSON
def make_api_request(url):
    r = requests.get(
        url=url,
        auth=HTTPBasicAuth(USERNAME, PASSWORD))

    if r.status_code == 200:
        return r.json()
    else:
        raise Exception("Request {0} failed (code {1})".format(url,
                                                               r.status_code))

def upload_fixture(url, filename):
    file_data = {'file-to-upload': (filename, open(filename, 'rb'), 'multipart/form-data')}
    r = requests.post(
        url=url,
        files=file_data,
        data={'replace': 'true'},
        auth=HTTPDigestAuth(USERNAME, PASSWORD)
    )
    return r

filename = "../test.xlsx"
url = "https://www.commcarehq.org/a/esoergel/fixtures/fixapi/"
r = upload_fixture(url, filename)
