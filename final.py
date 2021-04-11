###################################
##### Name: Hang Chen
##### Final project: Insects in US
###################################

from bs4 import BeautifulSoup
import requests
import json
import time
import sqlite3


'''About cache and database in general (state data may only need cache once)
If query is not in the database (SELECT key return None)
    request html
    cache to local json
    parse into database
    read the qeury out from database
else:
    read out from database directly.
'''


'''About database structure
Table 1:
Key: state name.
Url: statewise inset url.

Table 2:
Key: state name.
Inset: commen insect name.
Url: insect Url.

Table 3:
Key: commen insect name.
(for table)
Order: order.
Family: family.
Scientific name: binomial name.
Characteristics: Sting, posion, etc.
(for identification)
Photo Url: url.
(for description)
Description: insect description.
(for distribution)
Map: urls.
'''


def load_cache(cache_name):
    try:
        cache_file = open(cache_name, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache, cache_name):
    with open(cache_name, "w") as files:
        json.dump(cache, files, indent = 2)


def parse_state(request_response):
    state_dict = {}
    result = BeautifulSoup(request_response, "html.parser").find_all("div", class_="contentStripInner")[4]
    for i in result.find_all("a"):
        if i.text == "Alberta":
            break
        else:
            state_dict[i.text.strip()] = "https://www.insectidentification.org/" + i["href"]
    return state_dict


def get_state_dict():
    if state_cache != {}:
        print("Using cache")
        return parse_state(state_cache["main"])
    else:
        print("Fetching")
        response = requests.get("https://www.insectidentification.org/insects-by-state-listing.php")
        state_cache["main"] = response.text
        save_cache(state_cache, "state_cache.json")
        return parse_state(state_cache["main"])


def create_state_table(state_dict):
    connection = sqlite3.connect("USinsect.sqlite")
    cur = connection.cursor()
    create_table = '''
    CREATE TABLE IF NOT EXISTS "states" (
        "state" TEXT PRIMARY KEY UNIQUE,
        "url" TEXT NOT NULL
    )
    '''
    cur.execute(create_table)
    connection.commit()

    if cur.execute('''SELECT * FROM states''').fetchall() == []:
        insert_states = '''
        INSERT INTO "states"
        VALUES (?, ?)
        '''
        for i in state_dict.keys():
            cur.execute(insert_states, [i, state_dict[i]])
        connection.commit()
    else:
        return None


if __name__ == "__main__":
    state_cache = load_cache("state_cache.json")
    state_dict = get_state_dict()
    create_state_table(state_dict)