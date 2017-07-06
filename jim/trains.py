"""Provides main classes und functions."""

import requests
import json
import threading
import regex
import backoff

import urllib
from jim.elements import (Connection, split_name, sanitise_name, uniq,
                          get_train_details)


class TileError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

@backoff.on_exception(backoff.expo,
                      requests.exceptions.RequestException, max_tries=2)
def get_tile(tile=1):
    """Retrieve trains for tile no ranging from 1 through 23, including.

    Args:
        tile (int, default 1): 1 covers long distance trains only,
          2 through 23 includes trains for geographic subsets of Germany.
    """
    if tile < 1 or tile > 23:
        raise TileError('Valid tiles are in range of'
                        '1 through 23, including.')
    url = ('http://www.apps-bahn.de/bin/livemap/query-livemap.exe/'
           'dny?L=vs_livefahrplan&performLocating=1&'
           'performFixedLocating={}'.format(tile))
    trains = []
    rq = requests.get(url)
    connections = rq.content.decode('ISO-8859-1')
    print(connections[193920:193950])
    connections = connections.replace('\\x', '\\u00').replace("\\\'", "\'")
    for connection in json.loads(connections)[0][:-1]:
        try:
            trains.append(Connection(connection))
        # skip those (train) `Connections` without a valid
        # station_id (meta stuff?)
        except ValueError:
            pass
    return trains


def list_append(tile, out_list):
    """Helper to run in a thread."""
    out_list.extend(get_tile(tile))


class RailGrid:
    def __init__(self, regional=False, national=True):
        """Returns list of trains currently running with detailed information.

        Args:
            regional (bool, default True): Includes regional trains if `True`.
            national (bool, default True): Includes national,
              meaning long distance trains if `True`.
        """
        self.regional = regional
        self.national = national
        self.trains = self.pull_trains(self.regional,
                                       self.national)

    def __repr__(self):
        return '<{} trains>'.format(len(self.trains))

    def filter(self, name):
        splitted = split_name(name)
        # with number
        if splitted[1]:
            raw = r'{}\ *{}'.format(splitted[0], splitted[1])
        # without number
        else:
            raw = r'{}.*'.format(splitted[0])
        return list(filter(lambda t: regex.match(raw, t.name),
                           self.trains))

    def refresh(self, regional=None, national=None):
        """Refresh trains.

        Args:
            regional (bool, default self.regional): Includes
              regional trains if `True`.
            national (bool, default self.national): Includes
              national, meaning long distance trains if `True`.
        """
        self.regional = regional if regional is not None else self.regional
        self.national = national if national is not None else self.national
        self.trains = self.pull_trains(self.regional, self.national)

    def pull_trains(self, regional, national):
        """Returns train list.

        Args:
            regional (bool, default True): Includes regional trains if `True`.
            national (bool, default True): Includes national,
              meaning long distance trains if `True`.
        """
        trains = []
        national_trains = get_tile(1)
        regional_trains = []
        if regional:
            jobs = []
            for tile in range(2, 24):
                thread = threading.Thread(target=list_append,
                                          args=(tile, regional_trains))
                jobs.append(thread)
            # start the threads
            for j in jobs:
                j.start()
            # ensure all jobs to be finished
            for j in jobs:
                j.join()
            # pull regional trains in
            trains.extend(regional_trains)
        if national:
            trains.extend(national_trains)
        else:
            nationals_to_remove = map(lambda x: x.name, national_trains)
            for regional_train in regional_trains:
                if regional_train.name in nationals_to_remove:
                    regional_trains.remove(regional_train)
        return uniq(trains)


def search_train(name):
    """Get train link for a train name."""
    quoted_name = urllib.parse.quote(name)
    url = ('http://www.apps-bahn.de/bin/livemap/trainsearch-livemap.exe/'
           'dny?L=vs_livefahrplan&livemapTrainfilter=yes&jetztInlandOnly=yes&'
           'combineMode=5&productClassFilter=15&'
           'trainname={}'.format(quoted_name))
    rq = requests.get(url)
    raw_content = rq.content.decode(rq.encoding).replace('TSLs.sls =', '')
    print(raw_content)
    suggestions = json.loads(raw_content)['suggestions']
    # x[0] is 'value' like "EN   420"
    return suggestions


def get_train_link(name):
    name = sanitise_name(name)
    suggestions = search_train(name)
    return list(filter(lambda x: x['value'] == name,
                       suggestions))[0]['trainLink']


def get_train_info(name):
    """Get information for train name."""
    name = sanitise_name(name)
    return get_train_details(get_train_link(name))
