import pytest

from pkg_resources import resource_filename
import json

import requests
import responses

from jim.trains import (get_tile, list_append, TileError, RailGrid,
                        search_train, get_train_link, get_train_info)


def mock(tile):
    mock_path = resource_filename(__name__, 'mocks/{}.json'.format(tile))
    with open(mock_path) as mock_file:
        mock = json.load(mock_file)
    return mock


def tile_url(no):
    return ('http://www.apps-bahn.de/bin/livemap/query-livemap.exe/'
            'dny?L=vs_livefahrplan&performLocating=1&'
            'performFixedLocating={}'.format(no))


def test_TileError():
    assert TileError('bla').__str__() == 'bla'


@pytest.fixture
def train_search():
    with open(resource_filename(__name__, 'mocks/search_train.json')) as f:
        mock = f.read()
    return mock


@pytest.fixture
def train_link():
    with open(resource_filename(__name__, 'mocks/train_link.json')) as f:
        mock = f.read()
    return mock


@responses.activate
@pytest.mark.parametrize('tile', range(1, 24))
def test_get_tile(tile):
    responses.add(responses.GET, tile_url(tile), json=mock(tile),
                  match_querystring=True)
    trains = get_tile(tile)
    assert len(trains) > 0


@responses.activate
@pytest.mark.parametrize('tile', [0, 25])
def test_get_tile_invalid(tile):
    responses.add(responses.GET, tile_url(tile), json={'error': '2'},
                  match_querystring=True)
    with pytest.raises(TileError):
        get_tile(tile)

@responses.activate
def test_get_tile_fix_escape():
    with open(resource_filename(__name__, 'mocks/18_escape.json')) as f:
        the_escaped = f.read()
    responses.add(responses.GET, tile_url(18), body=the_escaped,
                  match_querystring=True)
    # should not raise an error
    assert get_tile(18)


@responses.activate
def test_get_tile_conn_err():
    responses.add(responses.GET, tile_url(1), body='TSLs = {}',
                  match_querystring=True)
    with pytest.raises(json.decoder.JSONDecodeError):
        get_tile(1)


def test_list_append():
    out_list = []
    list_append(1, out_list)
    assert len(out_list) > 0


RailGrid_data = [
    [True, False, 2368],
    [False, True, 298],
    [True, True, 2369]
]


@responses.activate
@pytest.mark.parametrize('regional, national, count',
                         RailGrid_data)
def test_RailGrid(regional, national, count):
    for tile in range(1, 24):
        responses.add(responses.GET, tile_url(tile), json=mock(tile),
                      match_querystring=True)
    rg = RailGrid(regional, national)
    assert len(rg.trains) == count

    # to test refresh, change input
    responses.add(responses.GET, tile_url(1), json=mock('1_later'),
                  match_querystring=True)
    rg.refresh()
    assert len(rg.trains) == count
    rg.refresh(regional=False, national=True)
    assert len(rg.trains) == 298

    # test filter
    assert len(rg.filter('IC 2045')) == 1
    assert len(rg.filter('IC')) == 270

    # test repr
    assert rg.__repr__() == '<298 trains>'


@responses.activate
def test_search_train(train_search):
    train_search_url = ('http://www.apps-bahn.de/bin/livemap/'
                        'trainsearch-livemap.exe/dny?L=vs_livefahrplan&'
                        'livemapTrainfilter=yes&jetztInlandOnly=yes&'
                        'combineMode=5&productClassFilter=15&'
                        'trainname=ICE%209557')
    responses.add(responses.GET, train_search_url, body=train_search,
                  match_querystring=True)
    assert search_train('ICE 9557') == \
        [{'arr': 'Frankfurt(Main)Hbf',
          'arrTime': '23:19:00+02:00',
          'cycle': '0',
          'dep': 'Paris Est',
          'depDate': '05.07.2017',
          'depTime': '19:06:00+02:00',
          'id': '187927',
          'journParam': 'identifiedByjourneyID=ICE 9557'
            ':Paris Est:05.07.2017:19:06:00+02:00&externalID=187927NULLNULL&'
            'lineName=187927&administration=NULL&direction=NULL&'
            'internalID=187927&cycle=0&poolUIC=80&trainName=ICE 9557&'
            'trainType=&trainClass=0&firstStationName=Paris Est&'
            'firstStationEvaID=&firstStationDep=05.07.2017 19:06:00+02:00',
          'pool': '80',
          'pubTime': '21:09',
          'trainClass': '0',
          'trainLink': '221658/261813/991658/421943/80',
          'value': 'ICE 9557',
          'vt': '1-5-7'}]


@responses.activate
def test_get_train_link(train_search):
    url = ('http://www.apps-bahn.de/bin/livemap/trainsearch-livemap.exe/'
           'dny?L=vs_livefahrplan&livemapTrainfilter=yes&jetztInlandOnly=yes'
           '&combineMode=5&productClassFilter=15&trainname=ICE%209557')
    responses.add(responses.GET, url, body=train_search,
                  match_querystring=True)
    assert get_train_link('ICE 9557') == '221658/261813/991658/421943/80'


@responses.activate
def test_get_train_info(train_search, train_link):
    train_search_url = ('http://www.apps-bahn.de/bin/livemap/'
                        'trainsearch-livemap.exe/dny?L=vs_livefahrplan&'
                        'livemapTrainfilter=yes&jetztInlandOnly=yes&'
                        'combineMode=5&productClassFilter=15&'
                        'trainname=ICE%209557')
    train_link_url = ('http://www.apps-bahn.de/bin/livemap/query-livemap.exe/'
                      'dny?L=vs_livefahrplan&tpl=singletrain2json&'
                      'performLocating=8&look_nv=get_rtmsgstatus'
                      '|yes|get_rtfreitextmn|yes|get_rtstoptimes'
                      '|yes|get_fstop|yes|get_pstop|yes|'
                      'get_nstop|yes|get_lstop|yes|zugposmode|'
                      '2|&look_trainid=221658/261813/991658/421943/80&')
    responses.add(responses.GET, train_search_url, body=train_search,
                  match_querystring=True)
    responses.add(responses.GET, train_link_url, body=train_link,
                  match_querystring=True)
    assert get_train_info('ICE 9557') == {
       'delay': '1',
       'edgeid': '5',
       'fdep': '19:06',
       'fstopname': 'Paris Est',
       'fstopno': '8700011',
       'larr': '23:19',
       'larr_d': '0',
       'lstopname': 'Frankfurt(Main)Hbf',
       'lstopno': '8000105',
       'name': 'ICE 9557',
       'narr': '22:17',
       'narr_d': '1',
       'ndep': '22:19',
       'ndep_d': '1',
       'nstopname': 'Mannheim Hbf',
       'nstopno': '8000244',
       'parr': '21:35',
       'parr_d': '0',
       'pass': '4',
       'passproc': '50',
       'pdep': '21:37',
       'pdep_d': '0',
       'pstopname': 'Kaiserslautern Hbf',
       'pstopno': '8000189',
       'trainid': '84/187955/18/19/80',
       'x': '8106131',
       'y': '49360092'}
