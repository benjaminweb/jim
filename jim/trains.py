"""Provides main classes und functions."""

import requests
import json
import threading
import regex
import backoff

import urllib
from jim.elements import (Train, split_name, sanitise_name, uniq,
                          calc_ckv, sign, to_coord, get_train_details)


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
    raw_trains = []
    rq = requests.get(url)
    connections = rq.content.decode('ISO-8859-1')
    connections = connections.replace('\\x', '\\u00').replace("\\\'", "\'")
    # remove last item
    connections = json.loads(connections)[0][:-1]
    tile_count = len(connections)
    ckv = calc_ckv(tile_count)
    for connection in connections:
        try:
            # convert ordinal 1 and 2 to coords
            connection[1] = to_coord(sign(connection[1], ckv))
            connection[2] = to_coord(sign(connection[2], ckv))
            raw_trains.append(connection)
        # skip those (train) `Trains` without a valid
        # station_id (meta stuff?)
        except (TypeError, ValueError):
            pass
    return raw_trains


def list_append(tile, out_list):
    """Helper to run in a thread."""
    out_list.extend(get_tile(tile))


def collect_raw_trains():
    """Returns all raw trains."""
    raw_trains = []
    jobs = []
    for tile in range(1, 24):
        thread = threading.Thread(target=list_append,
                                  args=(tile, raw_trains))
        jobs.append(thread)

    # start the threads
    for j in jobs:
        j.start()

    # ensure all jobs to be finished
    for j in jobs:
        j.join()
    return raw_trains


class RailGrid:
    def __init__(self, raw_trains=None):
        """Returns list of trains currently running with detailed information.

        Args:
            raw_trains (list): Output of :func:`collect_raw_trains`.
        """
        self.trains = self.pull_trains(raw_trains)

    def __repr__(self):
        return '<{} trains>'.format(len(self.trains))

    def filter(self, pattern=None, national=None, regional=None):
        """Filter for `pattern` in trains.

        Args:
            pattern (str, default None): String to match train names.
            national (bool, default None): Includes national,
              meaning long distance trains if `True`.
            regional (bool, default None): Includes regional trains if `True`.
        """
        if pattern:
            splitted = split_name(pattern)
            # with number
            if splitted[1]:
                raw = r'{}\ *{}'.format(splitted[0], splitted[1])
            # without number
            else:
                raw = r'{}.*'.format(splitted[0])
            selection = list(filter(lambda t: regex.match(raw, t.name),
                                    self.trains))
        else:
            selection = list(self.trains)

        if national and regional:
            pass
        # filter nationals
        elif national is not None:
            selection = filter(lambda t: t.national is national, selection)
        # filter regionals
        elif regional is not None:
            selection = filter(lambda t: t.regional is regional, selection)

        return list(selection)

    def refresh(self):
        """Refresh trains."""
        self.trains = self.pull_trains()

    def pull_trains(self, raw_trains=None):
        """Returns train list.

        Args:
            raw_trains (list): Output of :func:`collect_raw_trains`.
        """
        trains = []
        raw_trains = raw_trains or collect_raw_trains()
        for raw_train in raw_trains:
            try:
                trains.append(Train(raw_train))
            # raised if station_id is non-numeric which
            # is the case for '' (those meta entries we
            # want to drop anyways
            except ValueError:
                pass
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
