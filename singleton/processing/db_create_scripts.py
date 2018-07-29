__author__ = 'Evan'

#db create scripts using MYSQLdb library
#http://www.tutorialspoint.com/python/python_database_access.htm


from . import db_connect

if __name__ == "__main__":
    db = db_connect.db_connect()

    cursor = db.cursor()

    cursor.execute("DROP TABLE IF EXISTS dataset_access")
    cursor.execute("DROP TABLE IF EXISTS group_info")
    cursor.execute("DROP TABLE IF EXISTS dataset")
    cursor.execute("DROP TABLE IF EXISTS password")
    cursor.execute("DROP TABLE IF EXISTS registered_user")
    cursor.execute("DROP TABLE IF EXISTS user_group")
    cursor.execute("DROP TABLE IF EXISTS privilege")
    cursor.execute("DROP TABLE IF EXISTS sector")

    sector = """CREATE TABLE sector
                            (
                            id VARCHAR(32) PRIMARY KEY,
                            name VARCHAR(45) NOT NULL,
                            description VARCHAR(255) NOT NULL
                            )"""

    privilege = """CREATE TABLE privilege
                            (
                            id VARCHAR(32) PRIMARY KEY,
                            name VARCHAR(45) NOT NULL,
                            description VARCHAR(255) NOT NULL
                            )"""

    group_info = """CREATE TABLE group_info
                            (
                            id VARCHAR(32) PRIMARY KEY,
                            name VARCHAR(100) NOT NULL,
                            organisation VARCHAR(100)
                            )"""

    user = """CREATE TABLE registered_user
                            (
                            id VARCHAR(32) PRIMARY KEY,
                            privilege_id VARCHAR(32) NOT NULL DEFAULT 'standard',
                            sector_id VARCHAR(32),
                            first_name VARCHAR(100) NOT NULL,
                            email_address VARCHAR(100) NOT NULL,
                            secret_question VARCHAR(100) NOT NULL,
                            secret_answer VARCHAR(200) NOT NULL,
                            last_name VARCHAR(100),
                            organisation VARCHAR(100),
                            gender ENUM('male', 'female', 'other'),
                            date_of_birth DATE,
                            signup_date DATETIME DEFAULT NOW(),

                            FOREIGN KEY fk_users_privilege_id (privilege_id) REFERENCES privilege (id) ON UPDATE CASCADE ON DELETE RESTRICT,
                            FOREIGN KEY fk_user_sector_id (sector_id) REFERENCES sector (id) ON UPDATE CASCADE ON DELETE RESTRICT
                            )"""

    password = """CREATE TABLE password
                            (
                            id VARCHAR(32) PRIMARY KEY,
                            user_id VARCHAR(32) NOT NULL,
                            password_hash VARCHAR(200) NOT NULL,
                            replacement_date DATETIME,

                            FOREIGN KEY fk_password_user_id (user_id) REFERENCES registered_user (id) ON UPDATE CASCADE ON DELETE CASCADE
                            )"""

    dataset = """CREATE TABLE dataset
                            (
                            id VARCHAR(32) PRIMARY KEY,
                            user_id VARCHAR(32) NOT NULL,
                            name VARCHAR(255) NOT NULL,
                            description VARCHAR(2000),
                            public_access BOOL NOT NULL,
                            upload_date DATETIME NOT NULL,
                            short_url VARCHAR(100) UNIQUE,

                            FOREIGN KEY fk_dataset_user_id (user_id) REFERENCES registered_user (id) ON UPDATE CASCADE ON DELETE RESTRICT
                            )"""

    user_group = """CREATE TABLE user_group
                            (
                            id VARCHAR(32) PRIMARY KEY,
                            user_id VARCHAR(32) NOT NULL,
                            group_id VARCHAR(32) NOT NULL,
                            privilege_id VARCHAR(32) NOT NULL,

                            FOREIGN KEY fk_user_group_user_id (user_id) REFERENCES registered_user (id) ON UPDATE CASCADE ON DELETE RESTRICT,
                            FOREIGN KEY fk_user_group_group_id (group_id) REFERENCES group_info (id) ON UPDATE CASCADE ON DELETE CASCADE,
                            FOREIGN KEY fk_user_group_privilege_id (privilege_id) REFERENCES privilege (id) ON UPDATE CASCADE ON DELETE RESTRICT
                            )"""

    dataset_access = """CREATE TABLE dataset_access
                            (
                            id VARCHAR(32) PRIMARY KEY,
                            user_id VARCHAR(32) NOT NULL,
                            group_id VARCHAR(32) NOT NULL,
                            privilege_id VARCHAR(32) NOT NULL,

                            FOREIGN KEY fk_dataset_access_user_id (user_id) REFERENCES registered_user (id) ON UPDATE CASCADE ON DELETE RESTRICT,
                            FOREIGN KEY fk_dataset_access_group_id (group_id) REFERENCES group_info (id) ON UPDATE CASCADE ON DELETE CASCADE,
                            FOREIGN KEY fk_dataset_access_privilege_id (privilege_id) REFERENCES privilege (id) ON UPDATE CASCADE ON DELETE RESTRICT
                            )"""

    cursor.execute(sector)
    cursor.execute(privilege)
    cursor.execute(group_info)
    cursor.execute(user)
    cursor.execute(password)
    cursor.execute(dataset)
    cursor.execute(user_group)
    cursor.execute(dataset_access)
