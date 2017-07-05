jim
***

The German railways system at your fingertips.

Install
=======

.. code-block:: bash

    pip3 install jim

Quick Start
===========

To get all currently running national trains:

.. code-block:: python

    >>> from jim.trains import RailGrid
    >>> bahn = RailGrid
    >>> bahn
    <263 trains>

You can filter for specific trains::

    >>> ices = bahn.filter('ICE')

Let's pick an ICE::

    >>> an_ice = ices[-1]
    >>> an_ice
    <ICE 1701 to Berlin Südkreuz>

Each train is a :class:`Connection` class.
You can retrieve it's next station like::

    >>> an_ice.next_station
    <20:26 -> Hamburg Dammtor>

Similarly goes the previous station::

    >>> an_ice.previous_station
    <Hamburg-Altona -> 20:20>
 
If delay data is available, it will be stored here::

    >>> an_ice.delay

.. note::

    Be aware many trains have a delay setting of `None`. Then, no data is available.
    Further, the delay of the next station `next_station.delay` is distinct from
    the general delay.

Advanced
========

You can refresh a :class:`jim.trains.RailGrid` class::

    >>> bahn.refresh()
    >>> bahn
    <254 trains>

To enable regional trains::

    >>> bahn.refresh(regional=True)
    >>> bahn
    <3956 trains>

You can do that right away from the beginning with::

    >>> bahn = RailGrid(regional=True)
