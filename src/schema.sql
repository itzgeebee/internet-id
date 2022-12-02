DROP TABLE IF EXISTS identity;
DROP TABLE IF EXISTS business;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS blacklisted_tokens;



CREATE TABLE user(
    user_id INT NOT NULL AUTO_INCREMENT,
    first_name varchar(30) NOT NULL,
    last_name varchar(30) NOT NULL,
    email varchar(100) NOT NULL UNIQUE,
    password varchar(500) NOT NULL,
    phone_number varchar(15) NOT NULL,
    date_of_birth date NOT NULL,
    internet_id varchar(200) UNIQUE NOT NULL,
    country varchar(50) NOT NULL,
    gender varchar(30) NOT NULL,
    verified boolean DEFAULT false,
    is_dev boolean DEFAULT false NOT NULL,
    private_key varchar(500),
    PRIMARY KEY(user_id),
    INDEX (internet_id, private_key)
);

CREATE TABLE identity(
    id int NOT NULL AUTO_INCREMENT,
    user_id int NOT NULL,
    international_id boolean DEFAULT false NOT NULL,
    image_id varchar(200) UNIQUE,
    bank_verification_num boolean DEFAULT false NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX (user_id)
);

CREATE TABLE business(
    id int NOT NULL AUTO_INCREMENT,
    user_id int NOT NULL,
    company_name varchar(300) NOT NULL,
    business_type varchar(100) NOT NULL,
    website_url varchar(100) UNIQUE,
    project_description text NOT NULL,
    company_mail varchar(100) UNIQUE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX (user_id)
);

CREATE TABLE blacklisted_token(
    id int NOT NULL AUTO_INCREMENT,
    token varchar(500) NOT NULL,
    PRIMARY KEY (id)
);

