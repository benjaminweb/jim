import pendulum
import requests
import regex


def split_name(name):
    splits = regex.findall(r'([A-Za-z]+)(?:\ *)(\d+)', name)
    if len(splits) > 0:
        return (splits[0][0], int(splits[0][1]))
    else:
        return (name, None)


def sanitise_name(name):
    """Fill train name with right amount of whitespace."""
    splitted = split_name(name)
    # train name with number
    if splitted[1]:
        whitespace = 8-len(splitted[0])-len(str(splitted[1]))
        return '{}{}{:d}'.format(splitted[0], whitespace*' ', splitted[1])
    # train name without number
    else:
        return name


def hmins2epoch(hours, mins):
    """Returns epoch for hours, mins."""
    timing = pendulum.now(tz='Europe/Berlin').replace(hour=hours, minute=mins)
    return timing.format('X', formatter='alternative')


def get_delay(string):
    """Convert anything to `int` or `None`."""
    if string is None:
        return
    try:
        return int(string)
    except ValueError:
        return


class Station:
    def __init__(self, station_id, name, previous,
                 arrival=None, departure=None, delay=None):
        """Initialises a stop of a train.

        Args:
            station_id (int): The station's id.
            name (str): The station's name.
            arrival (str, default None): Arrival time in HH:MM
              format, may be `None`.
            departure (str, default None): Departure time in HH:MM
              format, may be `None`.
            delay (int, default None): Delay in minutes.
              `None` means not available.
            previous (bool): `True` if previous station, else `False`.

        Attributes:
            station_id (int): The station's id.
            name (str): The station's name.
            arrival (str): Arrival time in HH:MM format, may be `None`.
            departure (str): Departure time in HH:MM format, may be `None`.
            delay (int): Delay in minutes. `None` means not available.
            previous (bool): `True` if previous station, else `False`.
        """
        self.station_id = int(station_id)
        self.name = name
        self.arrival = arrival
        self.departure = departure
        self.delay = delay
        self.previous = previous

    def __repr__(self):
        template = ''
        if self.arrival:
            template += '{} -> '.format(self.arrival)
        template += '{}'.format(self.name)
        if self.departure:
            template += ' -> {}'.format(self.departure)
        if self.delay is not None:
            template += ' [{:+d}]'.format(self.delay)
        return '<{}>'.format(template)


class Train:
    def __init__(self, connection):
        """Initialises a train connection.

        Args:
            connection (list): List of information bits
              of train connection from parsed JSON (DB's own format).

        Attributes:
            name (str): The train's name.
            train_link (str): The train's id.
            previous_station (Station): The previous station, may be `None`.
            next_station (Station): The next station, may be `None`.
            delay (int): Delay in minutes. `None` means not available.
            direction (str): Final station's name.
        """
        regional = {8: 'RB / RE', 16: 'S', 16392: 'RB / RE/ NEG'}
        national = {1: 'ICE', 2: 'IC / EC / CNL', 4: 'EN', 16386: 'EC', 16388: 'EC'}

        self.train_class = connection[5]
        self.regional = self.train_class in regional
        self.national = self.train_class in national

        self.name = connection[0]
        self.train_link = connection[3]
        self.lat = connection[1]
        self.lon = connection[2]
        self.previous_station = Station(connection[10],
                                        connection[9],
                                        previous=True,
                                        departure=connection[17])
        self.next_station = Station(connection[12],
                                    connection[11],
                                    previous=True,
                                    arrival=connection[16],
                                    delay=get_delay(connection[18]))
        self.delay = get_delay(connection[6])
        self.direction = connection[7]

    def __repr__(self):
        if self.delay:
            return '<{} to {} [{:+d}]>'.format(self.name,
                                               self.direction,
                                               self.delay)
        else:
            return '<{} to {}>'.format(self.name, self.direction)

    def details(self):
        """Retrieve details for train."""
        return get_train_details(self.train_link)


def get_train_details(train_link):
    """Get information for train_link."""
    url = ('http://www.apps-bahn.de/bin/livemap/query-livemap.exe/dny'
           '?L=vs_livefahrplan&tpl=singletrain2json&performLocating=8'
           '&look_nv=get_rtmsgstatus|yes|get_rtfreitextmn|yes|get_rtstoptimes'
           '|yes|get_fstop|yes|get_pstop|yes|get_nstop|yes|get_lstop|yes|'
           'zugposmode|2|&look_trainid={}&'.format(train_link))
    return requests.get(url).json()['look']['singletrain'][0]


def uniq(trains):
    """Returns only uniq trains."""
    seen = set()
    result = []
    for train in trains:
        if train.train_link not in seen:
            seen.add(train.train_link)
            result.append(train)
    return result


# FIXME: WRITE TEST
def calc_ckv(tile_count):
    """Returns CKV for tile.
    
    Args:
        tile_count (int): Count of entries in tile JSON (without last item).
    """
    ymd = int(pendulum.now(tz='Europe/Berlin').format('%Y%m%d'))
    return 22222 + ((ymd+tile_count) % 22222)


# FIXME: WRITE TEST
def sign(val, ckv):
    return ckv * (val % ckv) + int(val/ckv)


def to_coord(val):
    return val/1000000
