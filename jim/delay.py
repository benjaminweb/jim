from jim.trains import RailGrid


def delay_segments(regional=True, national=True,
                   thresholds=[5, 15, 30, 60]):
    """Returns `dict` with delay thresholds mapping to share of trains with
    delay equal or more than that.

    Args:
        regional (bool, default True): Include regional trains if `True`.
        national (bool, default True): Include national trains if `True`.
        thresholds (list[int]): Delay minutes threshold to count trains for.
    """
    trains = RailGrid(regional=regional, national=national).trains
    with_data = list(filter(lambda t: t.delay, trains))
    delayed = {threshold: list(filter(lambda t: t.delay >= threshold,
                                      with_data)) for threshold in thresholds}
    shares = {threshold: len(delayed[threshold])/len(with_data)
              for threshold in delayed.keys()}
    shares['coverage'] = len(with_data)/len(trains)
    shares['trains'] = len(trains)
    return shares


def to_increments(shares):
    """Converts absolute shares into increments (of preceding groups).

    Args:
        shares (dict): Maps delay minutes to share
          (including bigger groups).
    """
    result = {}
    thresholds = get_thresholds(shares)
    rev_thresholds = list(reversed(thresholds))
    for no, key in enumerate(rev_thresholds):
        # last has no greater one
        if no == 0:
            result[key] = shares[key]
        # all those having a greater one
        else:
            result[key] = shares[key]-shares[rev_thresholds[no-1]]
    return result


def get_thresholds(keys):
    """Return non-str thresholds of iterable.

    Args:
        keys (iterable): Iterable, that is the result of
          :func:`delay_segments.keys()`.
    """
    return list(filter(lambda x: not isinstance(x, str), keys))
