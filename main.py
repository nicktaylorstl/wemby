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

    data =[]
    with open('data/wemby_blocks.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)

    rando = random.randint(0,200)
    id = data[rando]
    video_info = [(id[0],id[1])]
    

    # Render the template with the query results
    return render_template('wemby.html',video_info=video_info)


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
