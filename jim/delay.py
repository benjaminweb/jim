from jim.trains import RailGrid


def get_delay_share(trains, threshold):
    """Returns share of trains with delay greater or equal `threshold`.

    Args:
        trains (iterable[Connection]): Iterable holding trains.
        threshold (number): Threshold greater or equal a delay must be
          to be considered.
    """
    delayed = 0
    with_data = 0
    for train in trains:
        if train.delay and train.delay >= threshold:
            delayed += 1
        with_data += 1
    return delayed/with_data
            
   


def delay_segments(GridObject, thresholds=[5, 15, 30, 60]):
    """Returns `dict` with delay thresholds mapping to share of trains with
    delay equal or more than that.

    Args:
        GridObject (RailGrid): Object carrying trains.
        thresholds (list[int]): Delay minutes threshold to count trains for.
    """
    trains = GridObject.trains
    delays = list(get_delays(trains))
    ge_threshold = {threshold: list(filter(lambda d: d >= threshold,
                                           delays))
                    for threshold in thresholds}
    shares = {threshold: len(ge_threshold[threshold])
              for threshold in ge_threshold.keys()}
    shares['coverage'] = len(delays)/len(trains)
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
    """Returns non-str thresholds of iterable.

    Args:
        keys (iterable): Iterable, that is the result of
          :func:`delay_segments.keys()`.
    """
    return sorted(list(filter(lambda x: not isinstance(x, str), keys)))


def get_subset(values, lower=None, upper=None):
    """Returns subset of values greater or equal `lower` and smaller `upper`.

    Args:
        values (iterable): Iterable of numeric values.
        lower (number, default None): Lower bound (including) to filter values.
        upper (number, default None): Upper bound (excluding) to filter values.
    """
    if lower is None and upper is not None:
        subset = filter(lambda v: v < upper, values)
    elif lower is not None and upper is None:
        subset = filter(lambda v: v >= lower, values)
    elif lower is not None and upper is not None:
        subset = filter(lambda v: v >= lower and v < upper, values)
    else:
        subset = values
    return list(subset)


def get_delays(trains):
    """Yields delays of trains where it is not `None`.

    Args:
        trains (iterable[Connection]): Iterable holding trains.
    """
    for train in trains:
        if train.delay:
            yield train.delay
