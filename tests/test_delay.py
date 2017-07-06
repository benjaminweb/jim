from pytest import approx

import responses

from jim import RailGrid
from jim.delay import get_thresholds, to_increments, delay_segments

from tests.test_trains import tile_url, mock


@responses.activate
def test_delay_segments():
    for tile in range(1, 24):
        responses.add(responses.GET, tile_url(tile), json=mock(tile),
                      match_querystring=True)
    GridObject = RailGrid(regional=True, national=True)
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
