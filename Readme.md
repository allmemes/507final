Instruction:

----------------------------------------------------------------------------------------------------------------
The program is designed in a way that if your query (like common insects in a state, or information about a certain insect) is in the database ("USinsect.sqlite"), it will directly output related results. If it is not in the database, it will go fetch the html response from the webesite, cache the html response, parse it, store it into the database, and finally output your query in the flask app.

However, I am encountering this 503 status quite often recently, which only returns an html response that does not make sense (full of a bunch of random divs that contains weird digits). Thus, functions like ".find()" in the progam basically fail and return "None". But sometimes I can also successfuly obtain the request (otherwise the database and cache files that created will not exist). Such issue DID NOT happen earlier in the draft proposal and data checkpoint, where I can normally obtain request just like usual, and it only happened near the end of my project. I have already communicated this issue with the professor, and he says at least I should request the insect info for the Michigan state and cache as more states as possible, which I did. Sorry for the inconvenience.

Thus, there are two versions of the app: with cache files/database and without cache files/database. Note, in either version, html pages in template folder are always used.

-----------------------------------------------------------------------------------------------------------------
Version 1: It is highly recommended to use this version.
Test the app with final.py, all three cache files (state_cache.json, state_insects_cache.json, and insect_info_cache.json), and the database (USinsect.sqlite).

1, Open final.py in vscode and click run. You will see a link in the output window. Click it to open the first page.

2, In the first page, it asks you to input a state name. Note spellings and captilization matters. If you input something weird, it will direct you to an error page, where you can try again.

3, In this version, I only cached the common 30 insects in Michigan, Alabama, and Alaska (Update: Hawaii is also added through the uncached demo). Thus, state name you can input will have to be one of those three (four) states.

4, If you input Michigan, then you will see 30 insects in Michigan, click on the radio button, hit continue, and then you will see the information about that insect. You can click the default return button (comes with the browser) or hit the "back to main page" link to start the state query again.

5, If you input the other two of the states, like Alaska, you will also be directed to a similar page, where you can see the common insects. But, for those insects, only if they are also within the common insects in Michigan can you click on and see the information. This is because I only cached the scientific information about those 30 insects in Michigan, and insects in other states but not in Michigan will need to go through the html request, parse, and store process, which may fail as mentioned above due to 503 error. Essentially, in this test version, only the Michigan state works smoothly without error, since all the information has been cached.

6, If you clicked on one insect that is within Alabama or Alaska but not in Michigan, and the website returns a page with no information, it means that the 503 error occurs, and the error html response has been cached into the json files (hence polluted the cache), and functions like ".find()" fail to find the target information and thus return None. In this case, you may want to use the function below to remove the polluted html response from cache files and save the cache again.

'''
def clean_cache(cache_to_be_clean, error_url)
    del cache_to_be_clean[error_url]
    with open("name of the cache", 'w') as data_file:
        json.dump(cache_to_be_clean, data_file, indent = 2)
'''

7, When clikcing on the insect picture link for a certain insect, it may fail and show some error like "the webiste does not allow images to be hotlinked". But if I put the same link into a separate html file and run it, it will work. After that, the image link in the flask app will also work accordinly. Not sure if this is because I am using a vpn. If this happens, go to the test.html in template folder, open it with browswer, and click on the insect link (only for Michigan) you want to know. You should see the picture, and the link itself should turn into purple (as if being visiteed already). Then same link will work in the flask app. This issue will be included in the demo.

-----------------------------------------------------------------------------------------------------------------
Version 2: Try this version with caution!
Test the app with only final.py (include html pages in template folder of course).

1, Open final.py in vscode and click run. It might take a while for you to see the flask app link. Because it is requesting state urls from the website. Then the program will create related cache files, the database, and three tables.

2, Later, you will see a link in the output window. Click it to open the first page.

3, From here, the app will work just like version 1, except in that it may encounter the 503 error from the source website. If you input a state name or click on an insect and see nothing in the next page, it indicates that the 503 error occurs. Error html response has been cached into the json files (hence polluted the cache), and functions like ".find()" fail to find the target information and thus return None.

4, If this happen, remove all the cache files and database created and try again, until the 503 error goes away.

5, If this error does not happen, the website will start to show a progress bar at the top, and it will take a while (maybe quite a while) for you to see your query at the next page. After this, if you send the same query again, the progress will work much faster, as the information has been cached and stored. If you open the USinsect.sqlite, you can also see that new information has been added into the database as well. I successfully initiated this uncached version of the app during the implementation of this project. I will try to add a video demo about this version, if the 503 error goes away (Update: the uncached version demo is up!)

----------------------------------------------------------------------------------------------------------------
Possible bugs for the program:
Aside from the 503 error, if the program still fails in some way, it may be caused by some pages having different html tags format, like some insects may miss some information, or they do not have any images in the website.

END----------------------------------------------------------------------------------------------------------END