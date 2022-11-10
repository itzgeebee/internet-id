auth_schema = {
    "required": ['first_name', 'last_name',
                 'password', 'email', 'phone_number',
                 'date_of_birth',
                 'gender',
                 'country',
                 'bank_verification_num'
                 ],
    "properties": {
        "first_name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 50
        },
        "last_name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 50
        },
        "password": {
            "type": "string",
            "minLength": 8,
            "maxLength": 50
        },
        "email": {
            "type": "string",
            "minLength": 1,
            "maxLength": 50,
            "format": "email"
        },
        "phone_number": {
            "type": "string",
            "minLength": 8,
            "maxLength": 15
        },
        "date_of_birth": {
            "type": "string",
            "minLength": 5,
            "maxLength": 30,
            "format": "date"
        },
        "gender": {
            "type": "string",
            "minLength": 1,
            "maxLength": 30
        },
        "country": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100,
        },
        "national_id_number": {
            "type": "string",
            "minLength": 11,
            "maxLength": 11
        },
        "international_id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        },
        "image_id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        },
        "bank_verification_num": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        }
        ,
        "is_dev": {
            "type": "boolean"
        }
    },
    "additionalProperties": False
}

login_schema = {
    "required": ['internet_id', 'password'],
    "properties": {
        "internet_id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        },
        "password": {
            "type": "string",
            "minLength": 8,
            "maxLength": 50
        }
    },
    "additionalProperties": False,

}

add_product_schema = {
    "required": ['company_name', 'project_description',
                 'website_url', 'business_type',
                 'private_key', "company_mail"
                 ],
    "properties": {
        "company_name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        },
        "project_description": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        },
        "website_url": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        },
        "business_type": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        },
        "private_key": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        },
        "company_mail": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        }
    },
    "additionalProperties": False
}

verify_schema = {
    "required": ['internet_id', 'private_key'
                 ],
    "properties": {
        "internet_id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        },
        "private_key": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        }
    },
    "additionalProperties": False
}

update_product_schema = {
    "properties": {
        "company_name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        },
        "project_description": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        },
        "website_url": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        },
        "business_type": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        },
        "company_mail": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        }
    },
    "additionalProperties": False
}