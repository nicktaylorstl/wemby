from flask import Flask, render_template, request
import sqlite3
from datetime import datetime, timedelta
import csv
import requests
import random


app = Flask(__name__,template_folder='templates')


def get_highlight_url(game_id, event_id):
    headers = {
        'Host': 'stats.nba.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'x-nba-stats-origin': 'stats',
        'x-nba-stats-token': 'true',
        'Connection': 'keep-alive',
        'Referer': 'https://stats.nba.com/',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }

    url = 'https://stats.nba.com/stats/videoeventsasset?GameEventID={}&GameID={}'.format(
                event_id, game_id)
    r = requests.get(url, headers=headers)
    json = r.json()
    video_urls = json['resultSets']['Meta']['videoUrls']
    playlist = json['resultSets']['playlist']
    video_event = {'video': video_urls[0]['lurl'], 'desc': playlist[0]['dsc']}
    return (video_event['video'],video_event['desc'])


@app.route('/')
def index():

    return render_template('index.html')

@app.route('/3pt')
def three_pt():

    data =[]
    with open('data/wemby_3pt.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)

    rando = random.randint(0,100)
    id = data[rando]
    video_info = [(id[0],id[1])]
    

    # Render the template with the query results
    return render_template('3pt.html',video_info=video_info)

@app.route('/assist')
def assist():

    data =[]
    with open('data/wemby_assist.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)

    rando = random.randint(0,220)
    id = data[rando]
    video_info = [(id[0],id[1])]
    

    # Render the template with the query results
    return render_template('assist.html',video_info=video_info)


@app.route('/block')
def block():

    data =[]
    with open('data/wemby_block.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)

    rando = random.randint(0,200)
    id = data[rando]
    video_info = [(id[0],id[1])]
    

    # Render the template with the query results
    return render_template('block.html',video_info=video_info)

@app.route('/dunk')
def dunk():

    data =[]
    with open('data/wemby_dunk.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)

    rando = random.randint(0,140)
    id = data[rando]
    video_info = [(id[0],id[1])]
    

    # Render the template with the query results
    return render_template('dunk.html',video_info=video_info)

@app.route('/jumpball')
def jumpball():

    data =[]
    with open('data/wemby_jumpball.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)

    rando = random.randint(0,75)
    id = data[rando]
    video_info = [(id[0],id[1])]
    

    # Render the template with the query results
    return render_template('jumpball.html',video_info=video_info)

@app.route('/layup')
def layup():

    data =[]
    with open('data/wemby_layup.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)

    rando = random.randint(0,110)
    id = data[rando]
    video_info = [(id[0],id[1])]
    

    # Render the template with the query results
    return render_template('layup.html',video_info=video_info)

@app.route('/rebound')
def rebound():

    data =[]
    with open('data/wemby_rebound.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)

    rando = random.randint(0,660)
    id = data[rando]
    video_info = [(id[0],id[1])]
    

    # Render the template with the query results
    return render_template('rebound.html',video_info=video_info)

@app.route('/steal')
def steal():

    data =[]
    with open('data/wemby_steal.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)

    rando = random.randint(0,75)
    id = data[rando]
    video_info = [(id[0],id[1])]
    

    # Render the template with the query results
    return render_template('steal.html',video_info=video_info)



@app.route('/oops')
def oops():
    # Read data from CSV file
    video_info = []
    with open('data/oops.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            video_info.append(row)

    # Render HTML template with video information
    return render_template('oops.html', video_info=video_info)


if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0')
