Introduction
============

Installation
------------
Install using ``pip``::

   pip install talive

Features
--------
Talive is a python library for using *Technical Analysis* in *LIVE trading*. We have the following features

* Accept for non-time-uniform data.
* Online operation.
* Efficient in time & space.


Non-time-uniform data
^^^^^^^^^^^^^^^^^^^^^
In usual TA libraries, inputs are supposed to be uniform in time. e.g. price per minute/day.
In talive, we extend the definition of indicators to accept non-uniform inputs.
Here, each input is a tuple (t, v) (wrapped in class :code:`TimedFloat`), where t is a python :code:`datetime.datetime` instance and v is the input value.
In financial markets, transactions occur naturally in a non-time-uniform way.
This feature allows you to use *tick* rather than *bar* data, which makes computation more accurate & in time.

More specificially

* For *Moving Average* type indicators, a **fixed number** of values is adapted to **fixed time intervals**.
  When initializing such an indicator, you specify a :code:`datetime.timedelta` t, and we yield the average in the last t time, no matter how much values were ingested.
* For *exponential Moving Average* type indicators, we adapt indicators so that the previous value decays exponentially as time passed by.
When initializing such an indicator, you specify a :code:`datetime.timedelta` t as the *time constant*, a term adapted from physics and engineering, to mark the time for the information to decay to 1/e.

Online operation
^^^^^^^^^^^^^^^^
In normal TA libraries, you have to provide batch input, which is known as *offline computing*.
We revised algorithms to make the entire computing *online*.
Each indicator has an :code:`insert` method, which accepts a :code:`TimedFloat` input.
When live data flows in, you digest the live tick data into indicators and get outputs instantaneously.

Relatively fast
^^^^^^^^^^^^^^^
| Proper data structures and algorithms are used to make time and memory consumption reasonable.
| However, we state that this library is only suitable for *live trading* (with delay measured in ms). If you are doing what is called *High-frequency trading* (with delay measured in us or below), a certain amount of adaption should be required. Since I, the author of this library, do not have access to such HFT devices, extremely low latency will not be officially supported.

Contributing
------------
* Bug fix. Tests
* For any suggestions, please open a Github issue.
