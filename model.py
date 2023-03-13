import json
from pydantic import BaseModel

class UserCreate(BaseModel):
    login: str
    password: str
    email: str

class UserLogin(BaseModel):
    login: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(object):
    __slots__ = ("user_id", "username", "email", "hashed_password", 
                 "registration_date", "last_seen", "education")

    def __init__(self, user_id, username, email, hashed_password, 
                 registration_date, last_seen, education):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.registration_date = registration_date
        self.last_seen = last_seen
        self.education = education

class Course(object):
    __slots__ = ("course_id", "course_name", "course_description", "from_language", 
                 "learning_language", "course_weight", "creation_date", "created_by")

    def __init__(self, course_id, course_name, course_description, from_language, 
                 learning_language, course_weight, creation_date, created_by):
        self.course_id = course_id
        self.course_name = course_name
        self.course_description = course_description
        self.from_language = from_language
        self.learning_language = learning_language
        self.course_weight = course_weight
        self.creation_date = creation_date
        self.created_by = created_by

class Category(object):
    __slots__ = ("category_id", "course_id", "category_name", "category_description", 
                 "category_weight", "creation_date", "created_by")

    def __init__(self, category_id, course_id, category_name, category_description, 
                 category_weight, creation_date, created_by):
        self.category_id = category_id
        self.course_id = course_id
        self.category_name = category_name
        self.category_description = category_description
        self.category_weight = category_weight
        self.creation_date = creation_date
        self.created_by = created_by

class Sentence(object):
    __slots__ = ("sentence_id", "course_id", "category_id", "exercise", "sentence_weight",
                 "creation_date", "created_by", "edited_datetime", "edited_by" )

    def __init__(self, sentence_id, course_id, category_id, exercise, sentence_weight,
                 creation_date, created_by, edited_datetime, edited_by):
        self.sentence_id = sentence_id
        self.course_id = course_id
        self.category_id = category_id
        self.exercise = exercise
        self.sentence_weight = sentence_weight
        self.creation_date = creation_date
        self.created_by = created_by
        self.edited_datetime = edited_datetime
        self.edited_by = edited_by

    def toDict(self):
        return {
            "sentence_id" : self.sentence_id,
            "course_id" : self.course_id,
            "category_id" : self.category_id,
            "exercise" : json.dumps(self.exercise),
            "sentence_weight" : self.sentence_weight,
            "creation_date" : self.creation_date,
            "created_by" : self.created_by,
            "edited_datetime" : self.edited_datetime,
            "edited_by" : self.edited_by,
        }
    
class Excercise(object):
    __slots__ = ("excercise_id", "user_id", "sentence_id", "exercise_timestamp",
                 "user_response", "response_timestamp", "is_correct")

    def __init__(self, excercise_id, user_id, sentence_id, exercise_timestamp,
                 user_response, response_timestamp, is_correct):
        self.excercise_id=excercise_id, 
        self.user_id=user_id, 
        self.sentence_id=sentence_id, 
        self.exercise_timestamp=exercise_timestamp,
        self.user_response=user_response, 
        self.response_timestamp=response_timestamp, 
        self.is_correct=is_correct