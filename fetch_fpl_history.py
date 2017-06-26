import json
import os
import time
import warnings

import pandas as pd
import progressbar
import requests

from common import DATA_DIR


def fetch_player_history(player_id):
    """ Fetch JSON of a single player's FPL history. """
    url = 'https://fantasy.premierleague.com/drf/element-summary/{}'.format(player_id)
    r = requests.get(url)
    return r.json()['history_past']


def fetch_all_player_histories(max_id=1000):
    """ Fetch the histories of all players. """
    histories = []
    bar = progressbar.ProgressBar()
    for player_id in bar(range(1, max_id+1)):
        try:
            history = fetch_player_history(player_id)
            histories += history
        except json.decoder.JSONDecodeError:
            print('\nLast player found at id = {0}'.format(player_id - 1))
            return histories
        time.sleep(2.5)  # Don't overload their servers
    else:
        warnings.warn('Last player_id not reached. You ought to try again '
                      'with a higher max_id')
        return histories


def fetch_positions():
    """ Fetch table mapping position_ids to position names. """
    url = 'https://fantasy.premierleague.com/drf/bootstrap-static'
    r = requests.get(url)
    positions = r.json()['element_types']
    return positions


def fetch_player_info():
    """ Fetch player info for the most recent season. """
    url = 'https://fantasy.premierleague.com/drf/bootstrap-static'
    r = requests.get(url)
    positions = []
    for player in r.json()['elements']:
        positions.append({
            'position_id': player['element_type'],
            'player_id': player['code'],
            'team_id': player['team_code'],
            'full_name': player['first_name'] + ' ' + player['second_name']
        })
    return positions


def fetch_and_save_history(max_id=1000):
    """ Fetch and save all historical seasons. """
    scores = pd.DataFrame(fetch_all_player_histories(max_id))
    players = pd.DataFrame(fetch_player_info())
    positions = pd.DataFrame(fetch_positions())

    # Add position info and clean up columns
    history = scores.merge(players, left_on='element_code',
                           right_on='player_id')
    history = history.merge(positions, left_on='position_id',
                            right_on='id')

    history.to_csv(os.path.join(DATA_DIR, 'fpl_history.csv'), index=False)


if __name__ == '__main__':
    fetch_all_player_histories()