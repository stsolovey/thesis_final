from fastapi import FastAPI, HTTPException

import uuid
import datetime
import json
import bcrypt
import datetime


import model, ydb_proc, ydb_educ, exer_proc


app = FastAPI()

@app.get("/")
async def index():
    return {'greeting': 'Hello. How are you?',
            'message': 'Glad to see you!',
            'possible ways':['/register','/login','/get_courses','/choose_course']}


@app.post("/register")
async def register(user: model.UserCreate):
    user_in_db = ydb_proc.check_if_username_is_in_database(user.login)
    if user_in_db:
        raise HTTPException(status_code=400, detail="User already registered")

    user_id = uuid.uuid4().hex
    username = user.login
    email = user.email
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    registration_date = datetime.date.today()
    last_seen = int(int(datetime.datetime.now().timestamp()))
    education = json.dumps({"current_course": "none"})

    db_user = model.User(user_id, username, email, hashed_password, registration_date, last_seen, education)

    ydb_proc.add_user(db_user)
    
    access_token = ydb_proc.create_access_token({"user_id": db_user.user_id, "education": db_user.user_id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login")
async def login(user: model.UserLogin):
    user_in_db = ydb_proc.check_if_username_is_in_database(user.login)
    if not user_in_db:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    db_user = ydb_proc.get_db_user_by_username(user.login)
    if not bcrypt.checkpw(user.password.encode('utf-8'), db_user.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token = ydb_proc.create_access_token({"user_id": db_user.user_id, "education": db_user.user_id})

    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/get_courses")
async def login(token: model.Token):

    return ydb_educ.get_courses()

@app.post("/choose_course")
async def login(token: model.Token, course_id):
    user_id = ydb_proc.get_user_id_from_access_token(access_token=token.access_token)
    user_db = ydb_proc.get_db_user_by_user_id(user_id=user_id)
    

    education_dict = json.loads(user_db.education)
    education_dict["current_course"] = course_id
    updated_education = json.dumps(education_dict, indent = 4)
    user_db.education = updated_education

    ydb_educ.update_education(user_db)

    return ydb_educ.get_categories(course_id)

@app.post("/get_exercise")
async def login(token: model.Token, category_id):
    user_id = ydb_proc.get_user_id_from_access_token(access_token=token.access_token)
    #user_db = ydb_proc.get_db_user_by_user_id(user_id=user_id)
    
    random_sentence = ydb_educ.get_random_sentence(category_id)
    #sentence = model.Sentence(sentence_id=random_sentence["sentence_id"], exercise=random_sentence["exercise"])

    #education_dict = json.loads(user_db.education)
    #education_dict["current_categorie"] = category_id
    #updated_education = json.dumps(education_dict, indent = 4)
    #user_db.education = updated_education

    #ydb_educ.update_education(user_db)

    #print(random_sentence)

    excercise_id = uuid.uuid4().hex
    exercise_timestamp = int(datetime.datetime.now().timestamp())

    ydb_educ.add_new_exercise(excercise_id, user_id, random_sentence["sentence_id"], exercise_timestamp)

    distractors = exer_proc.get_distractors_from_exercise(random_sentence["exercise"])
    argument = exer_proc.get_argument_from_exercise(random_sentence["exercise"])

    return {"excercise_id" : excercise_id, "argument" : argument, "distractors": distractors}

@app.post("/send_answer")
async def login(token: model.Token, excercise_id, user_input):
    #user_id = ydb_proc.get_user_id_from_access_token(access_token=token.access_token)
    
    sentence_id = ydb_educ.get_sentence_id_by_exrecise_id(excercise_id)
    sentence = ydb_educ.get_sentence_by_id(sentence_id)
    exercise = sentence['exercise']

    correct_translations = exer_proc.get_variables_from_exercise(exercise)

    answer_result, edit_distance = exer_proc.check_answer(correct_translations, user_input)
    expected = exer_proc.get_expected_sentence_from_exercise(exercise)

    response_timestamp = int(datetime.datetime.now().timestamp())
    ydb_educ.update_exercise(excercise_id, user_input, response_timestamp, answer_result)

    return {"answer_result":answer_result, "edit_distance":edit_distance, "expected": expected}


