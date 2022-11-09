import os
from dotenv import load_dotenv

import requests

load_dotenv()
base_url = os.environ.get('VERIFIED_API_BASE_URL')
headers = {
    "accept": "application/json",
    "userid": os.environ.get('VERIFIED_API_ID'),
    "apiKey": os.environ.get('VERIFIED_API_KEY'),
    "content-type": "application/json"
}

payload = {
    "searchParameter": "",
    "verificationType": ""
}

verification_types = {
    "national_id_number": "NIN-SEARCH",
    "international_id": "PASSPORT-FULL-DETAILS",
    "bank_verification_num": "BVN-BOOLEAN-MATCH"
}


def verify_ids(id_type: str, identities: dict[str], last_name=None,
               first_name=None, phone=None, dob=None, email=None) -> tuple[bool, str]:
    """Check if user is verified.
    :param email:  email
    :param dob:  date of birth
    :param phone:  phone number
    :param first_name:  first name
    :param identities: dict of identities
    :param id_type: type of id to verify
    :param last_name: last name of user -only for international id
    :return: True if user is verified, False otherwise
    """
    if id_type == "national_id_number":
        return is_verified_national_id(identities)
    elif id_type == "international_id":
        return is_verified_international_id(identities, last_name)
    elif id_type == "bank_verification_num":
        return is_verified_bank_verification_num(identities=identities, first_name=first_name,
                                                 last_name=last_name, phone=phone,
                                                 dob=dob, email=email)
    return False, "not verified"


def is_verified_national_id(identities: dict[str]) -> tuple[bool, str]:
    """Check if user is verified.
    :param identities: dict of identities
    :return: True if user is verified, False otherwise
    """
    new_payload = {**payload, "searchParameter": identities["national_id_number"],
                   "verificationType": verification_types["national_id_number"]}

    response = requests.post(base_url, json=new_payload, headers=headers)
    print(response.json())
    if response.status_code == 200:
        if response.json()["verificationStatus"] == "VERIFIED":
            return True, "success"
        return False, "pending, please try again later"
    return False, "not verified"


def is_verified_international_id(identities: dict[str], last_name) -> tuple[bool, str]:
    """Check if user is verified.
    :param identities: dict of identities
    :return: True if user is verified, False otherwise
    """

    new_payload = {**payload, "searchParameter": identities["international_id"],
                   "verificationType": verification_types["international_id"], "lastName": last_name}
    headers["apiKey"] = os.environ.get('VERIFIED_API_INT_PASS')

    response = requests.post(base_url, json=new_payload, headers=headers)
    if response.status_code == 200:
        if response.json()["verificationStatus"] == "VERIFIED":
            return True, "success"
        return False, "pending, please try again later"
    return False, "not verified"


def is_verified_bank_verification_num(identities: dict[str],
                                      first_name, last_name, email, phone, dob) -> tuple[
                                                                                bool, str]:
    """Check if user is verified.
    :param dob:  date of birth
    :param phone:  phone number
    :param email:   email
    :param last_name:  last name
    :param first_name:  first name
    :param identities: dict of identities
    :return: True if user is verified, False otherwise
    """

    print("verifying bvn")
    new_payload = {**payload, "searchParameter": identities["bank_verification_num"],
                   "verificationType": verification_types["bank_verification_num"], "firstName": first_name,
                   "lastName": last_name, "email": email, "phone": phone, "dob": dob}

    headers["apiKey"] = os.environ.get('VERIFIED_API_BVN_KEY')
    response = requests.post(base_url, json=new_payload, headers=headers)
    print(response.json())
    if response.status_code == 200:
        if response.json()["verificationStatus"] == "VERIFIED":
            return True, "success"
        return False, "pending, please try again later"
    return False, "not verified"
