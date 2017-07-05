import pytest

import pendulum
import responses

from jim.elements import (hmins2epoch, sanitise_name, split_name,
                          get_delay, Station, Connection, uniq)

from tests.test_trains import mock


split_name_data = [
    ['ICE729', ('ICE', 729)],
]


@pytest.mark.parametrize('name, splitted', split_name_data)
def test_split_name_data(name, splitted):
    assert split_name(name) == splitted


sanitise_data = [
    ['ICE729', 'ICE  729'],
    ['ICE     729', 'ICE  729'],
    ['ICE 30077', 'ICE30077'],
    ['EN 420', 'EN   420'],
    ['IC 1926', 'IC  1926'],
    ['ICE', 'ICE']
]


@pytest.mark.parametrize('unclean, sanitised', sanitise_data)
def test_sanitise_name(unclean, sanitised):
    assert sanitise_name(unclean) == sanitised


@pytest.mark.parametrize('hours, mins', [[1, 2], [23, 10]])
def test_hmins2epoch(hours, mins):
    now = pendulum.now(tz='Europe/Berlin').replace(hour=hours, minute=mins)
    assert hmins2epoch(hours, mins) == now.format('X', formatter='alternative')


@pytest.mark.parametrize('string, delay', [['', None], ['0', 0], ['1', 1]])
def test_get_delay(string, delay):
    assert get_delay(string) == delay


connections = [
                [['IC 31080', 672208342, 862880166, '84/330741/18/19/80', '14',
                  2, '0', 'Basel SBB', [], 'Zürich HB', '8503000',
                  'Basel SBB', '8500010', '01.07.17', '-1', None, '19:32',
                  '18:34', None, '0', '4', None, None],
                 0, None],
                [['ICE  376', 1411364960, 720056790, '84/330686/18/19/80', '7',
                  1, '0', 'Frankfurt(Main)Hbf',
                  [
                   [-2211, -3245, -4300, '5', '163', None, None],
                   [-1088, -1600, 112, '5', '163', None, None],
                   [27, 45, 4524, '5', '163', None, None],
                   [1151, 1681, 8914, '5', '161', None, None],
                   [1744, 2499, 11142, '5', '163', None, None],
                   [2346, 3308, 13348, '5', '161', None, None],
                   [2967, 4108, 15553, '5', '163', None, None],
                   [3605, 4908, 17759, '5', '163', None, None],
                   [4261, 5690, 19943, '5', '161', None, None],
                   [4935, 6481, 22171, '5', '162', None, None],
                   [6284, 8045, 26583, '5', '162', None, None],
                   [7632, 9609, 30995, '5', '162', None, None],
                   [8989, 11174, 35407, '', '0', None, None]
                  ],
                  'Karlsruhe Hbf', '8000191', 'Mannheim Hbf',
                  '8000244', '01.07.17', '147', None,
                  '19:10', '18:48', '0', '0', '2', None, None],
                 0, 0],
                [['ICE  729', 23526725, 764310905,
                  '84/122384/18/19/80', '28', 1, '', 'München Hbf',
                  [
                   [-134425, 71230, -465, '27', '260', None, None],
                   [-133544, 70529, 901, '27', '263', None, None],
                   [-132690, 69810, 2267, '27', '261', None, None],
                   [-131863, 69082, 3632, '26', '263', None, None],
                   [-131072, 68336, 4998, '26', '258', None, None],
                   [-130695, 67958, 5681, '26', '258', None, None],
                   [-130317, 67572, 6377, '26', '260', None, None],
                   [-129598, 66808, 7730, '26', '263', None, None],
                   [-128888, 66026, 9095, '26', '262', None, None],
                   [-127521, 64453, 11827, '26', '263', None, None],
                   [-126146, 62879, 14558, '26', '263', None, None],
                   [-125445, 62097, 15924, '26', '263', None, None],
                   [-124717, 61333, 17276, '26', '258', None, None],
                   [-124339, 60947, 17973, '26', '258', None, None],
                   [-123962, 60569, 18655, '26', '263', None, None],
                   [-123171, 59823, 20021, '27', '263', None, None],
                   [-122353, 59095, 21373, '27', '263', None, None],
                   [-121499, 58376, 22739, '27', '260', None, None],
                   [-120618, 57675, 24105, '27', '261', None, None],
                   [-119701, 56992, 25470, '27', '260', None, None],
                   [-118748, 56326, 26836, '27', '263', None, None],
                   [-117777, 55670, 28202, '28', '260', None, None],
                   [-116770, 55041, 29568, '28', '261', None, None],
                   [-115736, 54430, 30933, '28', '263', None, None],
                   [-115215, 54124, 31616, '28', '263', None, None],
                   [-114676, 53827, 32299, '28', '262', None, None],
                   [-112509, 52686, 35017, '', '0', None, None]
                  ],
                  'Köln Messe/Deutz Gl.11-12', '8073368',
                  'Frankfurt(M) Flughafen Fernbf',
                  '8070003', '01.07.17', '-1', None, '19:33', '18:44',  None,
                 None, '4', None, None],
                 None, None]
]


@pytest.mark.parametrize('connection, delay, next_station_delay', connections)
def test_connection(connection, delay, next_station_delay):
    the_conn = Connection(connection)
    assert the_conn.delay == delay
    assert the_conn.next_station.delay == next_station_delay
    assert the_conn.train_link == connection[3]


@responses.activate
def test_connection_details():
    url = ('http://www.apps-bahn.de/bin/livemap/query-livemap.exe/dny?'
           'L=vs_livefahrplan&tpl=singletrain2json&performLocating=8&'
           'look_nv=get_rtmsgstatus|yes|get_rtfreitextmn|yes|get_rtstoptimes'
           '|yes|get_fstop|yes|get_pstop|yes|get_nstop|yes|get_lstop|yes|'
           'zugposmode|2|&look_trainid=84/225078/18/19/80&')
    responses.add(responses.GET, url, json=mock('en50466'),
                  match_querystring=True)
    connection = ['EN 50466', 1025153148, 878390967,  '84/225078/18/19/80',
                  '18',  4,  '0', 'Zürich HB', [], 'Linz Hbf', '8100013',
                  'Salzburg Hbf', '8100002', '05.07.17', '-1', None,
                  '2:10', '1:05',  '0', '0',  '4', None, None]
    the_conn = Connection(connection)
    print(the_conn.details())
    assert the_conn.details() == {
       'trainid': '84/225078/18/19/80', 'x': '14292129', 'y': '48290178',
       'name': 'EN 50466', 'pstopname': 'Linz Hbf', 'pstopno': '8100013',
       'pdep': '1:05', 'parr': '22:07', 'pdep_d': '0', 'parr_d': '11',
       'nstopname': 'Salzburg Hbf', 'nstopno': '8100002', 'ndep': '2:30',
       'ndep_d': '0', 'narr': '2:10', 'narr_d': '0',
       'fstopname': 'Praha hl.n.', 'fstopno': '5400014', 'fdep': '18:02',
       'lstopname': 'Zürich HB', 'lstopno': '8503000', 'larr': '8:20',
       'larr_d': '0', 'pass': '12', 'edgeid': '13', 'passproc': '0',
       'delay': '0'}


connection_repr = [
    # without delay
    [['EC   258', 717899315, 695891371, '84/104456/18/19/80', '10', 2, '',
      'Decin hl.n.', [], 'Praha-Holesovice', '5400201', 'Usti nad Labem hl.n.',
      '5400019',  '01.07.17',  '-1',  None,  '19:40',  '18:37',  None,  None,
      '4',  None,  None],
     '<EC   258 to Decin hl.n.>'],
    # with 3 mins delay
    [['EC   258', 717899315, 695891371, '84/104456/18/19/80', '10', 2, '3',
      'Decin hl.n.', [], 'Praha-Holesovice', '5400201', 'Usti nad Labem hl.n.',
      '5400019',  '01.07.17',  '-1',  None,  '19:40',  '18:37',  None,  None,
      '4',  None,  None],
     '<EC   258 to Decin hl.n. [+3]>']
]


@pytest.mark.parametrize('connection, the_repr', connection_repr)
def test_connection_repr(connection, the_repr):
    assert Connection(connection).__repr__() == the_repr


Station_data = [
    [8400747, 'Zwolle', True, None, '19:50', None, '<Zwolle -> 19:50>'],
    [8400747, 'Zwolle', True, None, '19:50', 3, '<Zwolle -> 19:50 [+3]>'],
    [8400747, 'Zwolle', True, '19:47', None, None, '<19:47 -> Zwolle>'],
    [8400747, 'Zwolle', True, '19:47', None, 4, '<19:47 -> Zwolle [+4]>'],
    [8400747, 'Zwolle', True, '19:47', '19:50', None,
     '<19:47 -> Zwolle -> 19:50>'],
    [8400747, 'Zwolle', True, '19:47', '19:50', 0,
     '<19:47 -> Zwolle -> 19:50 [+0]>'],
    [8400747, 'Zwolle', True, '19:47', '19:50', 2,
     '<19:47 -> Zwolle -> 19:50 [+2]>']
]


@pytest.mark.parametrize('id, name, previous, arrival,'
                         'departure, delay, the_repr', Station_data)
def test_Station(id, name, previous, arrival,
                 departure, delay, the_repr):
    the_station = Station(id, name, previous, arrival, departure, delay)
    assert the_station.station_id == id
    assert the_station.name == name
    assert the_station.previous == previous
    assert the_station.arrival == arrival
    assert the_station.departure == departure
    assert the_station.delay == delay
    assert the_station.__repr__() == the_repr


def test_uniq():
    train1 = Connection(['IC 31080', 672208342, 862880166,
                         '84/330741/18/19/80', '14', 2, '0',
                         'Basel SBB', [], 'Zürich HB', '8503000',
                         'Basel SBB', '8500010', '01.07.17', '-1',
                         None, '19:32', '18:34', None, '0', '4', None, None])
    train2 = Connection(['EC   258', 717899315, 695891371,
                         '84/104456/18/19/80', '10', 2, '3',
                         'Decin hl.n.', [], 'Praha-Holesovice', '5400201',
                         'Usti nad Labem hl.n.', '5400019',  '01.07.17',
                         '-1',  None,  '19:40',  '18:37',  None,  None,
                         '4',  None,  None])
    trains = [train1, train2, train1, train1]
    expected = [train1, train2]
    assert uniq(trains) == expected
