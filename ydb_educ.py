import os
import ydb
import posixpath

from dotenv import load_dotenv

from ydb_conn import ensure_path_exists


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

endpoint = os.getenv("YDB_ENDPOINT")
database = os.getenv("YDB_DATABASE")
path = os.getenv("YDB_PATH")



def get_courses():
        
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
                        course_id, course_name, course_description, from_language, 
                 learning_language, course_weight, creation_date, created_by
                    FROM courses
                    ORDER BY
                           course_weight,
                           creation_date,
                           created_by;
                    """.format(
                        full_path
                    ),
                    commit_tx=True,
                )
              
                # if there is no courses
                if len(result_sets[0].rows)==0:
                    return False
                return result_sets[0].rows

            return pool.retry_operation_sync(callee)

def update_education(user):
    with ydb.Driver(endpoint=endpoint, database=database) as driver:
        
        driver.wait(timeout=5, fail_fast=True)
        
        with ydb.SessionPool(driver) as pool:
            
            ensure_path_exists(driver, database, path)
            full_path = posixpath.join(database, path)
            

            def callee(session):
                query = """
                PRAGMA TablePathPrefix("{}");
                DECLARE $USERID AS Utf8;
                DECLARE $EDUCATION AS Json;
                UPDATE users
                SET education = $EDUCATION
                WHERE user_id = $USERID;
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
                    {"$USERID": user.user_id, "$EDUCATION": user.education},
                )


                # Commit active transaction(tx)
                tx.commit()

            return pool.retry_operation_sync(callee)
        

def get_categories(course_id):
        
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
                        category_id, course_id, category_name, category_description, 
                 category_weight, creation_date, created_by
                    FROM categories
                    ORDER BY
                           category_weight,
                           creation_date,
                           created_by;
                    """.format(
                        full_path
                    ),
                    commit_tx=True,
                )
                    
                # if there is no categories
                if len(result_sets[0].rows)==0:
                    return False
                
                return result_sets[0].rows

            return pool.retry_operation_sync(callee)
        
def get_random_sentence(categorie_id):
        
    with ydb.Driver(endpoint=endpoint, database=database) as driver:
        
        driver.wait(timeout=5, fail_fast=True)
        
        with ydb.SessionPool(driver) as pool:
            
            ensure_path_exists(driver, database, path)
            full_path = posixpath.join(database, path)
            
        
            def callee(session):
                result_sets = session.transaction(ydb.SerializableReadWrite()).execute(
                    """
                    PRAGMA TablePathPrefix("{}");
                    SELECT sentence_id, exercise FROM sentences
                    WHERE category_id = "{}"
                    ORDER BY RANDOM(sentence_id)
                    LIMIT 1
                    """.format(
                        full_path, categorie_id
                    ),
                    commit_tx=True,
                )
                    
                # if there is no sentences
                if len(result_sets[0].rows)==0:
                    return False
                return result_sets[0].rows[0]

            return pool.retry_operation_sync(callee)
        

def add_new_exercise(excercise_id, user_id, sentence_id, exercise_timestamp):
    
    with ydb.Driver(endpoint=endpoint, database=database) as driver:
        
        driver.wait(timeout=5, fail_fast=True)
        
        with ydb.SessionPool(driver) as pool:
            
            ensure_path_exists(driver, database, path)
            full_path = posixpath.join(database, path)
            
            excercise_id, user_id, sentence_id, exercise_timestamp,
            
            def callee(session):
                query = """
                PRAGMA TablePathPrefix("{}");
                DECLARE $exerciseId AS Utf8;
                DECLARE $userId AS Utf8;
                DECLARE $sentenceId AS Utf8;
                DECLARE $exerciseTimestamp AS Datetime;
                UPSERT INTO exercises (excercise_id, user_id, sentence_id, exercise_timestamp) 
                    VALUES
                        ($exerciseId, $userId, $sentenceId, $exerciseTimestamp)
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
                    {"$exerciseId": excercise_id,
                     "$userId": user_id,
                     "$sentenceId": sentence_id,
                     "$exerciseTimestamp": exercise_timestamp,
                    },
                )
                # Commit active transaction(tx)
                tx.commit()

            return pool.retry_operation_sync(callee)

def update_exercise(excercise_id, user_response, response_timestamp, is_correct):
    with ydb.Driver(endpoint=endpoint, database=database) as driver:
        
        driver.wait(timeout=5, fail_fast=True)
        
        with ydb.SessionPool(driver) as pool:
            
            ensure_path_exists(driver, database, path)
            full_path = posixpath.join(database, path)
            

            def callee(session):
                query = """
                PRAGMA TablePathPrefix("{}");
                DECLARE $excerciseId AS Utf8;
                DECLARE $userResponse AS Utf8;
                DECLARE $responseTimestamp AS Datetime;
                DECLARE $isCorrect AS BOOL;
                UPDATE exercises
                SET user_response = $userResponse,
                    response_timestamp = $responseTimestamp, 
                    is_correct = $isCorrect
                WHERE excercise_id = $excerciseId;
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
                    {"$excerciseId": excercise_id, 
                     "$userResponse": user_response,
                     "$responseTimestamp": response_timestamp, 
                     "$isCorrect": is_correct,},
                )


                # Commit active transaction(tx)
                tx.commit()

            return pool.retry_operation_sync(callee)

def get_sentence_id_by_exrecise_id(excercise_id):
        
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
                        sentence_id
                    FROM exercises
                    WHERE excercise_id = "{}";
                    """.format(
                        full_path, excercise_id
                    ),
                    commit_tx=True,
                )

                    
                # if there is no exercises
                if len(result_sets[0].rows)==0:
                    return False
                return result_sets[0].rows[0]["sentence_id"]

            return pool.retry_operation_sync(callee)
        
def get_sentence_by_id(sentence_id):
        
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
                        sentence_id, exercise
                    FROM sentences
                    WHERE sentence_id = "{}";
                    """.format(
                        full_path, sentence_id
                    ),
                    commit_tx=True,
                )
                print("\n> select_simple_transaction:")
                for row in result_sets[0].rows:
                    print(
                       row
                    )
                    
                # if there is no sentences
                if len(result_sets[0].rows)==0:
                    return False
                return result_sets[0].rows[0]

            return pool.retry_operation_sync(callee)