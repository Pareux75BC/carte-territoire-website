# utils/constants.py

# Map Config
MAPBOX_STYLE = "mapbox/satellite-v9"
INITIAL_CENTER = [42.5471, 3.0362] # Pyrénées orientales
INITIAL_ZOOM = 6

# API Endpoints
API_ENDPOINT_INITIAL = 'https://carte-territoire-demo-24889736924.europe-west1.run.app/upload-and-process/' #"http://localhost:8000/upload-and-process/"
API_ENDPOINT_LATEST = 'https://carte-territoire-demo-24889736924.europe-west1.run.app/upload-and-process-reduced/' #"http://localhost:8000/upload-and-process-reduced/"

# Color/Label Dictionaries
FLAIR_CLASS_DATA = {
0  : ['other','#000000'],
1   : ['building','#db0e9a'] ,
2   : ['pervious surface','#938e7b'],
3   : ['impervious surface','#f80c00'],
4   : ['swimming_pool','#3de6eb'],
5   : ['bare_soil','#a97101'],
6   : ['water','#1553ae'],
7   : ['snow','#ffffff'],
8   : ['coniferous','#194a26'],
9  : ['deciduous','#46e483'],
10  : ['brushwood','#f3a60d'],
11  : ['vineyard','#660082'],
12  : ['herbaceous vegetation','#55ff00'],
13  : ['agricultural land','#fff30d'],
14  : ['plowed land','#e4df7c'],
15  : ['greenhouse','#9999ff']
}

REDUCED_7 = {
    0: ["other", "#000000"],
    1: ["building", "#db0e9a"],
    2: ["built surface", "#938e7b"],
    3: ["herbaceous vegetation", "#10cc1c"],
    4: ["water", "#1553ae"],
    5: ["vegetation", "#095b30"],
    6: ["agriculture", '#fff30d']
}
