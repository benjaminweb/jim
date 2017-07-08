import pytest
from pytest import approx

from pkg_resources import resource_filename
import json

import responses

from jim import RailGrid
from jim.delay import (get_delay_share, get_thresholds, to_increments,
                       delay_segments, get_subset, get_delays)

from tests.test_trains import tile_url, mock

get_delay_share_data = [
    [5, 0.09962009286618827],
    [10, 0.03630223723089911],
    [30, 0.007598142676234698]
]

@responses.activate
@pytest.mark.parametrize('threshold, share', get_delay_share_data)
def test_get_delay_share(threshold, share):
    for tile in range(1, 24):
        responses.add(responses.GET, tile_url(tile), json=mock(tile),
                      match_querystring=True)
    with open(resource_filename(__name__, 'raw_trains.json')) as f:
        raw_trains = json.load(f)
    GridObject = RailGrid(raw_trains)
    assert get_delay_share(GridObject.trains,
                           threshold) == approx(share)
 

@responses.activate
def test_delay_segments():
    for tile in range(1, 24):
        responses.add(responses.GET, tile_url(tile), json=mock(tile),
                      match_querystring=True)
    GridObject = RailGrid()
    assert delay_segments(GridObject) == approx(
      {5: 0.22540592168099333,
       15: 0.05253104106972302,
       30: 0.017191977077363897,
       60: 0.0057306590257879654,
       'coverage': 0.44195863233431826,
       'trains': 2369})


def test_get_thresholds():
    shares = {5: 0.21671258034894397,
              15: 0.046831955922865015,
              30: 0.028466483011937556,
              60: 0.008264462809917356,
              'coverage': 0.4861607142857143,
              'trains': 2240}
    assert get_thresholds(shares) == [5, 15, 30, 60]


def test_to_increments():
    shares = {5: 0.21671258034894397,
              15: 0.046831955922865015,
              30: 0.028466483011937556,
              60: 0.008264462809917356,
              'coverage': 0.4861607142857143,
              'trains': 2240}
    increments = {5: 0.16988062442607896,
                  15: 0.01836547291092746,
                  30: 0.0202020202020202,
                  60: 0.008264462809917356}
    assert to_increments(shares) == increments


get_subset_data = [
    [[1, 2, 3, 4, 5, 6, 7, 8, 9], 4, 7, [4, 5, 6]],
    [[1, 2, 3, 4, 5, 6, 7, 8, 9], None, 9, [1, 2, 3, 4, 5, 6, 7, 8]],
    # tricky: 0 is false
    [[1, 2, 3, 4, 5, 6, 7, 8, 9], 0, 2, [1]],
    [[1, 2, 3, 4, 5, 6, 7, 8, 9], 1, 8, [1, 2, 3, 4, 5, 6, 7]],
]


@pytest.mark.parametrize('values, lower, upper, subset',
                         get_subset_data)
def test_get_subset(values, lower, upper, subset):
    assert get_subset(values, lower, upper) == subset


@responses.activate
def test_get_delays():
    for tile in range(1, 24):
        responses.add(responses.GET, tile_url(tile), json=mock(tile),
                      match_querystring=True)
    with open(resource_filename(__name__, 'raw_trains.json')) as f:
        raw_trains = json.load(f)
    GridObject = RailGrid(raw_trains)
    trains = GridObject.filter(regional=True, national=True)
    delays = list(get_delays(trains))
    assert sum(delays) == 4410
