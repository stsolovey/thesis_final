import json
import string
import itertools
import re
import editdistance

def get_distractors_from_exercise(exercise):
    exercise = json.loads(exercise)
    distractors = exercise["expected"]["distractors"] + exercise["expected"]["text"]
    distractors = [''.join(char for char in item
                        if char not in string.punctuation)
                    for item in distractors]
    distractors = [''.join(char for char in item
                        if char not in string.punctuation)
                       for item in distractors if item != '']
    return distractors

def get_argument_from_exercise(exercise):
    exercise = json.loads(exercise)
    return exercise["argument"]

def get_variables_from_exercise(exercise):
    exercise = json.loads(exercise)
    return exercise["expected"]["variables"]

def get_expected_sentence_from_exercise(exercise):
    exercise = json.loads(exercise)
    return exercise["expected"]["sentence"]


def normalize_string(s):
    # remove all punctuation and extraneous characters
    s = re.sub(r'[^\w\s]', '', s)
    # convert to lowercase
    s = s.lower()
    # remove extra spaces
    s = re.sub(r'\s+', ' ', s)
    # remove leading/trailing spaces
    s = s.strip()
    return s

def generate_possible_translations(sentence):
    # get all the interchangeable parts of the sentence
    pattern = r'\[(.*?)\]'
    parts = re.findall(pattern, sentence)
    # generate all possible combinations of the interchangeable parts
    replacements = [p.split('/') for p in parts]
    combinations = itertools.product(*replacements)
    # replace the interchangeable parts in the sentence with the possible combinations
    possible_translations = []
    for combination in combinations:
        possible_translation = sentence
        for part, replacement in zip(parts, combination):
            possible_translation = possible_translation.replace(part, replacement)
        possible_translations.append(possible_translation)
    return possible_translations

def check_answer(correct_translations, user_input):
    # normalize user input
    user_input = normalize_string(user_input)
    # generate all possible translations from correct translations
    possible_translations = []
    for translation in correct_translations:
        possible_translations.extend(generate_possible_translations(translation))
    # normalize possible translations
    possible_translations = [normalize_string(t) for t in possible_translations]
    # check if user input matches any of the possible translations
    for translation in possible_translations:
        distance = editdistance.distance(user_input, translation)
        if distance <= 2:
            return True, distance
    return False, distance