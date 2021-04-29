###################################
##### Name: Hang Chen
##### Final project: Insects in US
###################################

from bs4 import BeautifulSoup
import requests
import json
import time
import sqlite3
from flask import Flask, render_template, request


#Two functions below are used to load and save cache.

def load_cache(cache_name):
    '''Function 1
    If there is no cache file with such cache_name, then create and return an empty dictionary.
    If there is a cache file with such cahce_name, then load it in, assign it to a variable called cache, and return it.

    Parameters
    ----------
    cache_name: string
        the name of the cache, depending on what data this cache is for.

    Return
    ------
    cache: dictionary
        a dictionary that will be used to receive various form of cache data.
    '''
    try:
        cache_file = open(cache_name, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache, cache_name):
    '''Function 2
    This function save a certain data (usually a dictionary) into a json file called "cache_name"

    Parameters
    ----------
    cache: usually a dictionary
        the data to be saved

    cache_name: string
        the name of the cache file

    Return
    ------
    None
    '''
    with open(cache_name, "w") as files:
        json.dump(cache, files, indent = 2)


#Three functions below are used to parse and cache state related information. Then create state table in the sqlite.

def parse_state(request_response):
    '''Function 1
    This function parse the html text of the main state information into a dictionary.

    Parameters:
    -----------
    request_response: html reponse .text file
        This is what we will obtain if we apply request.get function and then add .text to the response.

    Return:
    ------
    state_dict: a parsed dictionary
        Key: state names. Values: state url that contains common insect species.
        Should be 50 states in total, loop stops when hit Alberta, which is the first province in Canada.
    '''
    state_dict = {}
    result = BeautifulSoup(request_response, "html.parser").find_all("div", class_="contentStripInner")[4]
    for i in result.find_all("a"):
        if i.text == "Alberta":
            break
        else:
            state_dict[i.text.strip()] = "https://www.insectidentification.org" + i["href"]
    return state_dict

def get_state_dict():
    '''Function 2
    This function applies to the "state_cache" (created in the "main" by the load in function) and modify it directly. We
    cache the state html reponse and then call the above function (function 1) to create a state dictionary.

    If the current state_cache is not empty, then we use the html response directly (since all the state info are stored
    on a single page, we only request once and store it), pass the reponse into the parse_state function (above) to create
    the final state dictionary.

    If the current state_cache is empty, then we first request once to obtain the full html reponse, save the .text version
    of the html response to the state_cache, and then pass the reponse to parse_state function (above) to create the final
    state dictionary.

    Parameters:
    ----------
    None

    Return:
    ------
    state_dict: a parsed dictionary
        Same as function 1. Key: state names. Values: state url that contains common insect species.
        Should be 50 states in total.
    '''
    if state_cache != {}:
        return parse_state(state_cache["main"])
    else:
        time.sleep(1)
        response = requests.get("https://www.insectidentification.org/insects-by-state-listing.php")
        state_cache["main"] = response.text
        save_cache(state_cache, "state_cache.json")
        return parse_state(state_cache["main"])

def create_state_table(state_dict):
    '''Function 3
    This function serves to create the project database (if not exist), connect to it, and create our first state table:

    Table 1: states
    "state": state name.
    "url": statewise inset url.

    Then, since all the state urls are obtained once on a single page, we insert all the state names and urls as well.
    To avoid inserting again when we run the program the second time, we return None when the query returns something.

    Parameters:
    ----------
    state_dict: a dictionary
        This will be created in the main by the cache load in function, and whatever inside will be loaded into the sqlite.

    Return:
    ------
    None
    '''
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


#Similar to the format above, 4 functions below parse and cache top 30 insects within a state.
#Then we create table in the database that contains common insects within a state and allow for query functionality.

def parse_insects(stateurl, request_response):
    '''Function 1
    This function parse the html response for common insects within a state into a dictionary.

    Parameters:
    ----------
    stateurl: string
        The url of a certain state that contains common insects.

    request_response: response.text file.
        This is what we will obtain if we apply request.get function and then add .text to the response.

    Return:
    ------
    state_insects_dict: a dictionary
        Key: url of a certain state that contains common insects.
        Values: a list contains two lists inside:
        The first list records the top 30 insects' names, and the second list records top 30 insects's urls. They are paired.
    '''
    state_insects_dict= {stateurl:[]}
    insect_name_list, insect_url_list = [],[]
    result = BeautifulSoup(request_response, "html.parser").find_all("div", class_="entriesContainer picTrans")
    for i in result[:30]:
        insect_name_list.append(i.find("span", class_="textWhite textBold textNormal").text)
        insect_url_list.append("https://www.insectidentification.org" + i.find_all("a")[0]["href"])
    state_insects_dict[stateurl].append(insect_name_list)
    state_insects_dict[stateurl].append(insect_url_list)
    return state_insects_dict

def get_state_insects(state_url):
    '''Function 2
    This function applies to the "state_insects_cache" (created in the "main" by the load in function) and modify it directly. We
    cache the html reponse that contains common insects for a state and then call the above function (function 1) to create a state
    _insects_dict file.

    If the state_url we input to this function is in the keys of the state_insects_cache, we pass the corresponding stateurl and
    html response to the parse_insects function (above) to create the state_insects_dict.

    If the state_url is not in the keys of the state_insect_cache, we apply the request function, cache the response.text, and pass
    the stateurl and response to the parse_insects function (above) to create the state_insects_dict.

    Parameters:
    ----------
    state_url: string
        the url of the common insects within a state.

    Return:
    ------
    state_insects_dict: a dictionary.
        Same as above. Key: url of a certain state that contains common insects. Values: a list contains two lists inside:
        The first list records the top 30 insects' names, and the second list records top 30 insects's urls. They are paired.
    '''
    if state_url in state_insects_cache.keys():
        return parse_insects(state_url, state_insects_cache[state_url])
    else:
        time.sleep(1)
        response = requests.get(state_url)
        state_insects_cache[state_url] = response.text
        save_cache(state_insects_cache, "state_insects_cache.json")
        return parse_insects(state_url, state_insects_cache[state_url])

def create_state_insect_table():
    '''Function 3
    This simply connects to the project sqlite database and create a second table:

    Table 2: StateInsects
    "StateUrl": state url, not unique, shared among all insects found within that state.
    "InsectName": insect's common name,
    "InsectUrl": url for this insect.

    Parameters:
    ----------
    None

    Return:
    ------
    None
    '''
    connection = sqlite3.connect("USinsect.sqlite")
    cur = connection.cursor()
    create_table = '''
    CREATE TABLE IF NOT EXISTS "StateInsects" (
        "StateUrl" TEXT NOT NULL,
        "InsectName" TEXT NOT NULL,
        "InsectUrl" TEXT NOT NULL
    )
    '''
    cur.execute(create_table)
    connection.commit()

def query_state_insect(state_url):
    '''Function 4
    This function serves to query the database according to a state url (or a state if combined with state dictionary).

    Referring to the table structure mentioned above, if we query all content (*) based on a state url and get nothing, then it
    means the top 30 insects within this state is not loaded into the database. Thus, we insert the common insects info into the
    database in the format of [state url(shared), common insect name, insect url]. Finally, we output the common insect list and urls.

    Else: if the query is not empty, then it means it already has the record within the database, we can directly output the common
    insect list and urls.

    Parameters:
    ----------
    state_url: string
        the url of the common insects within a state.

    Return:
    ------
    Query output: tuples within a list.
        Each tuple is a common insect and url pair, together they form a list.
    '''
    connection = sqlite3.connect("USinsect.sqlite")
    cur = connection.cursor()
    if cur.execute(f"SELECT * FROM StateInsects WHERE StateUrl == '{state_url}'").fetchall() == []:
        insert_states_insects = '''
        INSERT INTO "StateInsects"
        VALUES (?, ?, ?)
        '''
        for i in range(len(get_state_insects(state_url)[state_url][0])):
            cur.execute(insert_states_insects, [state_url, get_state_insects(state_url)[state_url][0][i], get_state_insects(state_url)[state_url][1][i]])
        connection.commit()
        return cur.execute(f"SELECT InsectName, InsectUrl FROM StateInsects WHERE StateUrl == '{state_url}'").fetchall()
    else:
        return cur.execute(f"SELECT InsectName, InsectUrl FROM StateInsects WHERE StateUrl == '{state_url}'").fetchall()


#Keep following such format. The below 4 functions will parse and cache the information about a certain insect.
#Then we create table for insect information within the database and allow for query functionality.

def parse_info(insect_url, request_response):
    '''Function 1
    This function will take in the url for an insect and cached html response, parse the html response, and create a dictionary for an insect.

    Parameters:
    ----------
    insect_url: string
        This is the first key of the dictionary that records the url for this insect.

    request_response: html reponse .text file
        This is what we will obtain if we apply request.get function and then add .text to the response.

    Return:
    ------
    insect_info_dict: a dictionary
        There are ten keys inside. Together they collect url, common insect name, scientific name, order,
        family, photo url, description, size, color, and characteristics of the insect.
    '''
    result = BeautifulSoup(request_response, "html.parser")
    insect_info_dict = {}
    insect_info_dict["Url"] = insect_url

    names = result.find("h1", class_="textBold textDkGray").text
    insect_info_dict["CommonName"] = names[:names.index("(")-1]
    insect_info_dict["ScientificName"] = names[names.index("(")+1:names.index(")")]
    taxonomy = result.find_all("div", class_="containerRows textLarge picTrans")
    insect_info_dict["Order"] = taxonomy[3].text.strip().split()[1]
    insect_info_dict["Family"] = taxonomy[4].text.strip().split()[1]

    for i in result.find_all("img"):
        if i['src'][:13] == "/imgs/insects":
            insect_info_dict["PhotoUrl"] = "https://www.insectidentification.org"+i['src']
            break
    description = result.find("span", class_="textLarge")
    insect_info_dict["Description"] = description.text.strip().split("\n")[0]

    summary = result.find_all("div", class_="containerRows textLarge picTrans")
    size = summary[-3].text.strip()
    insect_info_dict["Size"] = size[size.index(":")+2:]
    color = summary[-2].text.strip()
    insect_info_dict["Color"] = color[color.index(":")+2:]
    feature = summary[-1].text.strip()
    insect_info_dict["Characteristics"] = feature[feature.index(":")+2:]

    return insect_info_dict

def get_insect_info(insect_url):
    '''Function 2
    This function applies to the "insect_info_cache" (created in the "main" by the load in function) and modify it directly. We
    cache the html reponse that contains all the information about that insect and then call the above function (function 1) to
    create a insect_info_dict file.

    If the insect_url we input to this function is in the keys of the insects_info_cache, we pass the insect_url and corresponding
    html response to the parse_info function (above) to create the insect_info_dict.

    If the insect_url is not in the keys of the state_insect_cache, we apply the request function, cache the response.text, and pass
    the insect_url and response to the parse_info function (above) to create the insect_info_dict.

    Parameters:
    ----------
    insect_url: string
        the url that contains all the information about that insect.

    Return:
    ------
    insect_info_dict: a dictionary
        Same output as the function above, since we call the parse_info function to output the same dictionary with 10 keys.
    '''
    if insect_url in insect_info_cache.keys():
        return parse_info(insect_url, insect_info_cache[insect_url])
    else:
        time.sleep(1)
        response = requests.get(insect_url)
        insect_info_cache[insect_url] = response.text
        save_cache(insect_info_cache, "insect_info_cache.json")
        return parse_info(insect_url, insect_info_cache[insect_url])

def create_insect_info_table():
    '''Function 3
    This function connects to the project database and create the third table:

    Table 3: InsectInfo
    Url: insect url. This is the primary key that is unique.
    CommonName: insect's common name.
    ScientificName: binomial name.
    Order: order.
    Family: family.
    PhotoUrl: url.
    Description: insect description.
    Characteristics: Sting, posion, etc.
    Color: insect color.
    Size: how large the insect is.

    Parameters:
    ----------
    None

    Return:
    ------
    NOne
    '''
    connection = sqlite3.connect("USinsect.sqlite")
    cur = connection.cursor()
    create_table = '''
        CREATE TABLE IF NOT EXISTS "InsectInfo" (
        "Url" TEXT PRIMARY KEY UNIQUE,
        "CommonName" TEXT NOT NULL,
        "ScientificName" TEXT NOT NULL,
        "Order" TEXT NOT NULL,
        "Family" TEXT NOT NULL,
        "PhotoUrl" TEXT NOT NULL,
        "Description" TEXT NOT NULL,
        "Size" TEXT NOT NULL,
        "Color" TEXT NOT NULL,
        "Characteristics" TEXT NOT NULL
    )
    '''
    cur.execute(create_table)
    connection.commit()

def query_insect_info(insect_url):
    '''Function 4
    This function serves to query the database according to an insect url.

    Referring to the table structure mentioned above, if we query all content (*) based on an insect url and get nothing, then it
    means the info about this insect in not in the database. Thus, we insert the scraped info about this insect into the database
    in the format of insect_info_dict. Finally, we output the corresponding query.

    Else: if the query is not empty, then it means it already has the scraped info about this insect within the database, we can
    directly output the corresponding query.

    Parameters:
    ----------
    insect_url: string
        the url that contains all the information about that insect.

    Return:
    ------
    sql query result: combination of tuple and list.
        This mainly contains all the information about this insect.
    '''
    connection = sqlite3.connect("USinsect.sqlite")
    cur = connection.cursor()
    if cur.execute(f"SELECT * FROM InsectInfo WHERE Url == '{insect_url}'").fetchall() == []:
        insert_insect_info = '''
        INSERT INTO "InsectInfo"
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cur.execute(insert_insect_info, [
            get_insect_info(insect_url)["Url"],
            get_insect_info(insect_url)["CommonName"],
            get_insect_info(insect_url)["ScientificName"],
            get_insect_info(insect_url)["Order"],
            get_insect_info(insect_url)["Family"],
            get_insect_info(insect_url)["PhotoUrl"],
            get_insect_info(insect_url)["Description"],
            get_insect_info(insect_url)["Size"],
            get_insect_info(insect_url)["Color"],
            get_insect_info(insect_url)["Characteristics"]
        ])
        connection.commit()
        return cur.execute(f"SELECT * FROM InsectInfo WHERE Url == '{insect_url}'").fetchall()
    else:
        return cur.execute(f"SELECT * FROM InsectInfo WHERE Url == '{insect_url}'").fetchall()


#Functions and setups below are for the Flask framework.

app = Flask(__name__)

@app.route('/')
def mainpage():
    '''
    This function initiates the first page, where people will input a state name to start the query.

    Parameters:
    ----------
    None

    Return:
    -------
    An html template that contains a form that receives user input.
    '''
    return render_template("state.html")

@app.route('/insects', methods=['POST'])
def insects():
    '''
    This function follows the last one, and in the website, it records the input state name from the last page.
    Based on whether the input is a key of the state_dict or not, This page will direct users to different pages
    where users will find the first 30 insects in that state. Note, the resulting pages also include an error page.

    Parameters:
    ----------
    None

    Return:
    -------
    An html template that contains the first 30 insects for a state, where people can click on the choice box to
    continue the query.
    Or An html template that contains the error information and asks users to input again.
    '''
    state_name = request.form["state_name"]
    if state_name in state_dict.keys():
        state_url = state_dict[state_name]
        common_insects = query_state_insect(state_url)
        return render_template("state_insects.html", state_name = state_name, insect_list=common_insects)
    else:
        return render_template("404.html")

@app.route('/insects/info', methods=['POST'])
def insect_info():
    '''
    This function follows the last one, and in the website, it records the choice box that user clicked for a specific
    insect from the last page. Then it will direct user to a page that contains all the information about that insect.

    Parameters:
    ----------
    None

    Return:
    ------
    An html template that contains all the information about that insect, source url, and going-back function.
    '''
    insect_url = request.form["insect"]
    insect_information = query_insect_info(insect_url)
    insect_name = insect_information[0][1]
    scientific_name = insect_information[0][2]
    order = insect_information[0][3]
    family = insect_information[0][4]
    photo = insect_information[0][5]
    description = insect_information[0][6]
    size = insect_information[0][7]
    color = insect_information[0][8]
    characteristics = insect_information[0][9]
    return render_template(
        "insect.html",
        insect_name = insect_name,
        description = description,
        photo = photo,
        scientific_name = scientific_name,
        order = order,
        family = family,
        size = size,
        color = color,
        characteristics = characteristics,
        insect_url = insect_url)



if __name__ == "__main__":
    print("Initiating...")
    state_cache = load_cache("state_cache.json")
    state_insects_cache = load_cache("state_insects_cache.json")
    insect_info_cache = load_cache("insect_info_cache.json")

    state_dict = get_state_dict()
    create_state_table(state_dict)
    create_state_insect_table()
    create_insect_info_table()

    #Run the app:
    app.run(debug=True)