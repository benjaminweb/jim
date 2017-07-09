jim
***

.. image:: https://img.shields.io/travis/benjaminweb/jim.svg?style=flat-square
  :target: https://travis-ci.org/benjaminweb/jim
  :alt: Linux Built Status

.. image:: https://img.shields.io/appveyor/ci/hyllos/jim/default.svg?style=flat-square
  :target: https://ci.appveyor.com/project/hyllos/jim
  :alt: Windows Built Status

.. image:: https://img.shields.io/codecov/c/bitbucket/hyllos/jim/default.svg?style=flat-square
  :target: https://codecov.io/bb/hyllos/jim/branch/default
  :alt: Code coverage

The German railways system at your fingertips.

Install
=======

.. code-block:: bash

    pip3 install jim

Quick Start
===========

To get all currently running trains:

.. code-block:: python

    >>> from jim.trains import RailGrid
    >>> bahn = RailGrid()
    >>> bahn
    <2195 trains>

You can filter for specific trains::

    >>> regs = bahn.filter(regional=True)
    >>> nats = bahn.filter(national=True)
    >>> ices = bahn.filter('ICE')

Let's pick an ICE::

    >>> an_ice = ices[-1]
    >>> an_ice
    <ICE 1086 to Berlin Südkreuz>

Each train is a `Train` class.
You can retrieve its next station like::

    >>> an_ice.next_station
    <20:26 -> Hamburg Dammtor [+0]>

Similarly goes the previous station::

    >>> an_ice.previous_station
    <20:24 -> Berlin-Spandau>
 
If delay data is available, it will be stored here::

    >>> an_ice.delay
    0

.. note::

    Be aware many trains have a delay setting of `None`. Then, no data is available.
    Further, the delay of the next station `next_station.delay` is distinct from
    the general delay (as shown before).

Advanced
========

You can refresh a `jim.trains.RailGrid` class::

    >>> bahn.refresh()
    >>> bahn
    <2260 trains>

Credits
=======

 * https://github.com/makujaho/trainspotter/blob/master/trainspotter/train.py
   https://media.ccc.de/v/MRMCD15-6986-i_like_trains#video&t=1454
 * https://github.com/derhuerst/db-zugradar-client

