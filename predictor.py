from tensorflow import keras
import numpy as np
import json
import sqlite3 as sql
from NEA import generate_id
import re


CATEGORIES = ['Mathematics', 'Physics', 'Biology', 'Chemistry', 'Medicine', 'Engineering', 'Computer']


def get_tags(array):
    tags = []
    array = array.tolist()
    for i in range(2):
        max_value = max(array[0])
        index = array[0].index(max_value)
        if CATEGORIES[index] == 'Computer': tags.append('Computer Science')
        else: tags.append(CATEGORIES[index])
        array[0][index] = 0
    return tags

def insertdata(type, file_data, model):
    for i in range(len(file_data['post type'][type]['url'])):
        post_id = generate_id('post')
        post_link = file_data['post type'][type]['url'].pop(0)
        post_title = file_data['post type'][type]['title'].pop(0)
        post_text = file_data['post type'][type]['synopsis'].pop(0)
        post_image_link = file_data['post type'][type]['image'].pop(0)
        prediction = model.predict(np.array([post_text]))
        tags = get_tags(prediction)
        with sql.connect('NEADatabase.db') as conn:
            c = conn.cursor()
            for tag in tags:
                c.execute('INSERT INTO post_tags (post_id, post_tag) VALUES (?,?)', (post_id, tag))
            c.execute('INSERT INTO posts (post_id, post_type, post_title, post_image_link, post_link, post_likes, post_text) VALUES (?,?,?,?,?,?,?)', 
                        (post_id, type, post_title, post_image_link, post_link, 0, ''.join(re.split('\. ', post_text)[:4])))
    file = open('C:/Users/Kasra Djadididan/OneDrive - Berkhamsted Schools Group/A-levels/Computer science/NEA/Scraping_cache.json', 'w+')
    return json.dump(file_data, file, indent=4)

def runpredictor():
    model = keras.models.load_model('complete_model/')
    file = open('C:/Users/Kasra Djadididan/OneDrive - Berkhamsted Schools Group/A-levels/Computer science/NEA/Scraping_cache.json', 'r') # read only mode 
    file_data = json.load(file)
    for type in file_data['post type']:
        x = insertdata(type, file_data, model)

runpredictor()