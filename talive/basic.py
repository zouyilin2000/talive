import datetime
import abc
import collections
import math


class TimedFloat:
    time: datetime.datetime
    value: float

    def __init__(self, time: datetime.datetime = datetime.datetime.min, value: float = math.nan):
        self.time = time
        self.value = value

    def __nonzero__(self):
        return not math.isnan(self.value)


class Indicator(abc.ABC):
    @abc.abstractmethod
    def insert(self, data: TimedFloat) -> TimedFloat:
        pass

    def batch_insert(self, data_list: list[TimedFloat]) -> list[TimedFloat]:
        return [self.insert(data) for data in data_list]


class High(Indicator):
    time_period: datetime.timedelta
    _monotonic_queue: collections.deque[TimedFloat]

    def __init__(self, time_period: datetime.timedelta):
        self.time_period = time_period
        self._monotonic_queue = collections.deque()

    def insert(self, data: TimedFloat) -> TimedFloat:
        while (self._monotonic_queue and self._monotonic_queue[-1].value <= data.value):
            self._monotonic_queue.pop()
        while (self._monotonic_queue and self._monotonic_queue[0].time <= data.time - self.time_period):
            self._monotonic_queue.popleft()
        return TimedFloat(data.time, self._monotonic_queue[0].value)


class Low(Indicator):
    time_period: datetime.timedelta
    _monotonic_queue: collections.deque[TimedFloat]

    def __init__(self, time_period: datetime.timedelta):
        self.time_period = time_period
        self._monotonic_queue = collections.deque()

    def insert(self, data: TimedFloat) -> TimedFloat:
        while self._monotonic_queue and self._monotonic_queue[-1].value >= data.value:
            self._monotonic_queue.pop()
        while self._monotonic_queue and self._monotonic_queue[0].time <= data.time - self.time_period:
            self._monotonic_queue.popleft()
        return TimedFloat(data.time, self._monotonic_queue[0].value)


class Sum(Indicator):
    time_period: datetime.timedelta
    _total: float
    _active: collections.deque

    def __init__(self, time_period: datetime.timedelta):
        self.time_period = time_period
        self._total = 0.
        self._active = collections.deque()

    def insert(self, data: TimedFloat) -> TimedFloat:
        self._active.append(data)
        self._total += data.value
        while self._active and self._active[0].time <= data.time - self.time_period:
            left = self._active.popleft()
            self._total -= left.value
        return TimedFloat(data.time, self._total)


class MA(Indicator):
    time_period: datetime.timedelta
    _total: float
    _active: collections.deque

    def __init__(self, time_period: datetime.timedelta):
        self.time_period = time_period
        self._total = 0.
        self._active = collections.deque()

    def insert(self, data: TimedFloat) -> TimedFloat:
        self._active.append(data)
        self._total += data.value
        while self._active and self._active[0].time <= data.time - self.time_period:
            left = self._active.popleft()
            self._total -= left.value
        return TimedFloat(data.time, self._total / len(self._active))


class EMA(Indicator):
    '''timeperiod: timedelta, time constant, i.e. decay to 1/e'''
    time_period: datetime.timedelta
    _prev: TimedFloat

    def __init__(self, time_period: datetime.timedelta):
        self.time_period = time_period
        self._prev = TimedFloat()

    def insert(self, data: TimedFloat) -> TimedFloat:
        if not self._prev:
            self._prev = data
            return self._prev
        factor = math.exp(-(data.time - self._prev.time) / self.time_period)
        value = factor * self._prev.value + (1. - factor) * data.value
        self._prev = TimedFloat(data.time, value)
        return self._prev


class MAD(Indicator):
    '''Mean Deviation'''
    time_period: datetime.timedelta
    _ma1: MA
    _ma2: MA

    def __init__(self, time_period: datetime.timedelta):
        self.time_period = time_period
        self._ma1 = MA(time_period)
        self._ma2 = MA(time_period)

    def insert(self, data: TimedFloat) -> TimedFloat:
        ma1 = self._ma1.insert(data)
        new = abs(data.value - ma1.value)
        return self._ma2.insert(TimedFloat(data.time, new))


class TR(Indicator):
    '''True range'''
    bar_period: datetime.timedelta
    _high: High
    _low: Low
    _prev: TimedFloat

    def __init__(self, bar_period: datetime.timedelta):
        self.bar_period = bar_period
        self._high = High(bar_period)
        self._low = Low(bar_period)
        self._prev = TimedFloat()

    def insert(self, data: TimedFloat) -> TimedFloat:
        high = self._high.insert(data)
        low = self._low.insert(data)
        if not self._prev:
            self._prev = data
            return TimedFloat(data.time, high.value - low.value)
        tr = max(high.value - low.value,
                 abs(high.value - self._prev.value),
                 abs(low.value - self._prev.value))
        self._prev = data
        return TimedFloat(data.time, tr)
