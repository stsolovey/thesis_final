import os
import ydb
import posixpath
from datetime import datetime, timedelta
import jwt
from typing import Optional

from dotenv import load_dotenv

from ydb_conn import ensure_path_exists

import model

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))



load_dotenv()
endpoint = os.getenv("YDB_ENDPOINT")
database = os.getenv("YDB_DATABASE")
path = os.getenv("YDB_PATH")

def check_if_username_is_in_database(username):
        
    with ydb.Driver(endpoint=endpoint, database=database) as driver:
        
        driver.wait(timeout=5, fail_fast=True)
        
        with ydb.SessionPool(driver) as pool:
            
            ensure_path_exists(driver, database, path)
            full_path = posixpath.join(database, path)
            
            def callee(session):
                result_sets = session.transaction(ydb.SerializableReadWrite()).execute(
                    """
                    PRAGMA TablePathPrefix("{}");
                    SELECT
                        user_id,
                        username,
                        registration_date,
                    FROM users
                    WHERE username = "{}";
                    """.format(
                        full_path, username
                    ),
                    commit_tx=True,
                )

                if len(result_sets[0].rows)>0:
                    return True
                else:
                    return False

            return pool.retry_operation_sync(callee)

def add_user(user):
    with ydb.Driver(endpoint=endpoint, database=database) as driver:
        
        driver.wait(timeout=5, fail_fast=True)
        
        with ydb.SessionPool(driver) as pool:
            
            ensure_path_exists(driver, database, path)
            full_path = posixpath.join(database, path)
            
            
            def callee(session):
                query = """
                PRAGMA TablePathPrefix("{}");
                DECLARE $USER_ID AS Utf8;
                DECLARE $USERNAME AS Utf8;
                DECLARE $EMAIL AS Utf8;
                DECLARE $HASH_PASS AS Utf8;
                DECLARE $REG_DATE AS Date;
                DECLARE $LAST_SEEN AS Datetime;
                DECLARE $EDUCATION AS Json;
                UPSERT INTO users (user_id, username, email, hashed_password, 
                                          registration_date, last_seen, education) 
                    VALUES
                        ($USER_ID, $USERNAME, $EMAIL, $HASH_PASS, $REG_DATE, $LAST_SEEN, $EDUCATION )
                    """.format(
                        full_path
                )
                prepared_query = session.prepare(query)

                # Get newly created transaction id
                tx = session.transaction(ydb.SerializableReadWrite()).begin()

                # Execute data query.
                # Transaction control settings continues active transaction (tx)
                tx.execute(
                    prepared_query,
                    {"$USER_ID": user.user_id,
                     "$USERNAME": user.username,
                     "$EMAIL": user.email,
                     "$HASH_PASS": user.hashed_password, 
                     "$REG_DATE": user.registration_date,
                     "$LAST_SEEN": user.last_seen,
                     "$EDUCATION": user.education,},
                )


                # Commit active transaction(tx)
                tx.commit()

            return pool.retry_operation_sync(callee)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expires_date = datetime.utcnow() + expires_delta
    else:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        expires_date = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expires_date})
    encoded_jwt = jwt.encode(
        to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_id_from_access_token(access_token):
    decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = decoded_token["user_id"]
    return user_id

def get_db_user_by_username(username):
        
    with ydb.Driver(endpoint=endpoint, database=database) as driver:
        
        driver.wait(timeout=5, fail_fast=True)
        
        with ydb.SessionPool(driver) as pool:
            
            ensure_path_exists(driver, database, path)
            full_path = posixpath.join(database, path)
            
            def callee(session):
                result_sets = session.transaction(ydb.SerializableReadWrite()).execute(
                    """
                    PRAGMA TablePathPrefix("{}");
                    SELECT
                        user_id, username, email, hashed_password, registration_date, last_seen, education
                    FROM users
                    WHERE username = "{}";
                    """.format(
                        full_path, username
                    ),
                    commit_tx=True,
                )
                    
                # if there is no username
                if len(result_sets[0].rows)==0:
                    print("there is no user")
                    return False
                db_user = result_sets[0].rows[0]
                return model.User(db_user["user_id"], db_user["username"], db_user["email"], 
                                  db_user["hashed_password"], db_user["registration_date"], 
                                  db_user["last_seen"], db_user["education"])

            return pool.retry_operation_sync(callee)
        
def get_db_user_by_user_id(user_id):
        
    with ydb.Driver(endpoint=endpoint, database=database) as driver:
        
        driver.wait(timeout=5, fail_fast=True)
        
        with ydb.SessionPool(driver) as pool:
            
            ensure_path_exists(driver, database, path)
            full_path = posixpath.join(database, path)
            
            def callee(session):
                result_sets = session.transaction(ydb.SerializableReadWrite()).execute(
                    """
                    PRAGMA TablePathPrefix("{}");
                    SELECT
                        user_id, username, email, hashed_password, registration_date, last_seen, education
                    FROM users
                    WHERE user_id = "{}";
                    """.format(
                        full_path, user_id
                    ),
                    commit_tx=True,
                )
                    
                # if there is no username
                if len(result_sets[0].rows)==0:
                    return False
                
                db_user = result_sets[0].rows[0]
                return model.User(db_user["user_id"], db_user["username"], db_user["email"], 
                                  db_user["hashed_password"], db_user["registration_date"], 
                                  db_user["last_seen"], db_user["education"])

            return pool.retry_operation_sync(callee)