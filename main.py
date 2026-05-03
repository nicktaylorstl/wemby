from flask import Flask, render_template, abort, request
import requests
import random
import time
from functools import lru_cache

app = Flask(__name__, template_folder='templates')

WEMBY_ID = 1641705
DEFAULT_SEASON = '2025-26'

NBA_HEADERS = {
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
    'Cache-Control': 'no-cache',
}

# (EVENTMSGTYPE, keyword that must appear in description alongside "Wembanyama")
# EVENTMSGTYPE: 1=made shot, 2=missed shot, 4=rebound, 5=turnover, 10=jump ball
CATEGORIES = {
    'dunk':     (1,  'Dunk'),
    '3pt':      (1,  '3PT'),
    'block':    (2,  'BLK'),
    'layup':    (1,  'Layup'),
    'rebound':  (4,  None),
    'steal':    (5,  'Steal'),
    'assist':   (1,  'AST'),
    'jumpball': (10, None),
}

LABELS = {
    'dunk':     'Dunk',
    '3pt':      '3-Pointer',
    'block':    'Block',
    'layup':    'Layup',
    'rebound':  'Rebound',
    'steal':    'Steal',
    'assist':   'Assist',
    'jumpball': 'Jump Ball',
}


_session = requests.Session()
_session.headers.update(NBA_HEADERS)


def nba_get(url, timeout=12, retries=2):
    last_err = None
    for attempt in range(retries + 1):
        try:
            r = _session.get(url, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
            last_err = e
            if attempt < retries:
                time.sleep(1 + attempt)
    raise last_err


@lru_cache(maxsize=1)
def get_seasons():
    """All NBA seasons Wembanyama has played, newest first."""
    try:
        data = nba_get(
            f'https://stats.nba.com/stats/playercareerstats'
            f'?PlayerID={WEMBY_ID}&PerMode=PerGame'
        )
        rows = data['resultSets'][0]['rowSet']
        hdrs = data['resultSets'][0]['headers']
        idx = hdrs.index('SEASON_ID')
        return tuple(sorted({row[idx] for row in rows}, reverse=True))
    except Exception:
        return (DEFAULT_SEASON,)


@lru_cache(maxsize=20)
def get_game_ids(season):
    """Game IDs for a specific season, or all career if season='all'."""
    if season == 'all':
        ids = []
        for s in get_seasons():
            ids.extend(get_game_ids(s))
        return tuple(ids)

    data = nba_get(
        f'https://stats.nba.com/stats/playergamelog'
        f'?PlayerID={WEMBY_ID}&Season={season}&SeasonType=Regular+Season'
    )
    rows = data['resultSets'][0]['rowSet']
    hdrs = data['resultSets'][0]['headers']
    idx = hdrs.index('Game_ID')
    return tuple(row[idx] for row in rows)


@lru_cache(maxsize=300)
def get_game_plays(game_id):
    data = nba_get(
        f'https://stats.nba.com/stats/playbyplayv2'
        f'?GameID={game_id}&StartPeriod=0&EndPeriod=10'
    )
    rows = data['resultSets'][0]['rowSet']
    hdrs = data['resultSets'][0]['headers']

    ei  = hdrs.index('EVENTNUM')
    eti = hdrs.index('EVENTMSGTYPE')
    hdi = hdrs.index('HOMEDESCRIPTION')
    vdi = hdrs.index('VISITORDESCRIPTION')

    plays = []
    for row in rows:
        desc = (row[hdi] or '') + (row[vdi] or '')
        plays.append((row[ei], row[eti], desc))
    return tuple(plays)


def get_video_url(game_id, event_id):
    data = nba_get(
        f'https://stats.nba.com/stats/videoeventsasset'
        f'?GameEventID={event_id}&GameID={game_id}'
    )
    video_url = data['resultSets']['Meta']['videoUrls'][0]['lurl']
    desc = data['resultSets']['playlist'][0]['dsc']
    return video_url, desc


def find_random_play(category, season):
    event_type, keyword = CATEGORIES[category]
    game_ids = list(get_game_ids(season))
    random.shuffle(game_ids)

    for game_id in game_ids[:25]:
        try:
            plays = get_game_plays(game_id)
        except Exception:
            continue
        matching = [
            (game_id, eid) for eid, etype, desc in plays
            if etype == event_type
            and 'Wembanyama' in desc
            and (keyword is None or keyword in desc)
        ]
        if matching:
            return random.choice(matching)

    return None


@app.route('/')
def index():
    seasons = list(get_seasons())
    return render_template('index.html', categories=LABELS, seasons=seasons)


@app.route('/highlight/<category>')
def highlight(category):
    if category not in CATEGORIES:
        abort(404)

    season = request.args.get('season', 'all')
    label = LABELS[category]

    try:
        play = find_random_play(category, season)
    except Exception as e:
        return render_template('highlight.html', error=f'NBA API error: {e}',
                               category=category, label=label, season=season)

    if not play:
        return render_template('highlight.html', error='No matching plays found.',
                               category=category, label=label, season=season)

    game_id, event_id = play
    try:
        video_url, desc = get_video_url(game_id, event_id)
    except Exception as e:
        return render_template('highlight.html', error=f'Could not load video: {e}',
                               category=category, label=label, season=season)

    return render_template('highlight.html', video_url=video_url, desc=desc,
                           category=category, label=label, season=season)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
