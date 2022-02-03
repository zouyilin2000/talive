from basic import *


class Aroon(Indicator):
    time_period: datetime.timedelta
    _high: High
    _low: Low

    def __init__(self, time_period: datetime.timedelta):
        self.time_period = time_period
        self._high = High(time_period)
        self._low = Low(time_period)

    def insert(self, data: TimedFloat) -> TimedFloat:
        high = self._high.insert(data)
        low = self._low.insert(data)
        aroon_up = 100. - (data.time - high.time) / self.time_period * 100.
        aroon_down = 100. - (data.time - low.time) / self.time_period * 100.
        return TimedFloat(data.time, aroon_up - aroon_down)


class MACD(Indicator):  # Normalized
    fast_period: datetime.timedelta
    slow_period: datetime.timedelta
    _fast_ema: EMA
    _slow_ema: EMA

    def __init__(self, fast_period: datetime.timedelta, slow_period: datetime.timedelta):
        self.fast_period = fast_period
        self.slow_period = slow_period

    def insert(self, data: TimedFloat) -> TimedFloat:
        fast_ema = self._fast_ema.insert(data)
        slow_ema = self._slow_ema.insert(data)
        return TimedFloat(data.time, fast_ema.value - slow_ema.value)


class MACD_n(Indicator):  # Normalized
    fast_period: datetime.timedelta
    slow_period: datetime.timedelta
    _fast_ema: EMA
    _slow_ema: EMA

    def __init__(self, fast_period: datetime.timedelta, slow_period: datetime.timedelta):
        self.fast_period = fast_period
        self.slow_period = slow_period

    def insert(self, data: TimedFloat) -> TimedFloat:
        fast_ema = self._fast_ema.insert(data)
        slow_ema = self._slow_ema.insert(data)
        return TimedFloat(data.time, (fast_ema.value - slow_ema.value) / slow_ema.value)


class TRIX(Indicator):
    '''time_period: timedelta, time constant, i.e. decay to 1/e'''
    time_period: datetime.timedelta
    _ema1: EMA
    _ema2: EMA
    _ema3: EMA
    _prev: TimedFloat

    def __init__(self, time_period: datetime.timedelta):
        self.time_period = time_period
        self._ema1 = EMA(time_period)
        self._ema2 = EMA(time_period)
        self._ema3 = EMA(time_period)
        self._prev = TimedFloat()

    def insert(self, data: TimedFloat) -> TimedFloat:
        ema1 = self._ema1.insert(data)
        ema2 = self._ema2.insert(ema1)
        ema3 = self._ema3.insert(ema2)
        if not self._prev or self._prev.time == data.time:
            self._prev = ema3
            return TimedFloat()
        value = (ema3.value - self._prev.value) / self._prev.value * 100.
        self._prev = ema3
        return TimedFloat(data.time, value)


class TRIX_n(Indicator):
    '''time_period: timedelta, time constant, i.e. decay to 1/e'''
    time_period: datetime.timedelta
    _ema1: EMA
    _ema2: EMA
    _ema3: EMA
    _prev: TimedFloat
    _time_unit: datetime.timedelta

    def __init__(self, time_period: datetime.timedelta, time_unit: datetime.timedelta = datetime.timedelta(seconds=1.)):
        self.time_period = time_period
        self._ema1 = EMA(time_period)
        self._ema2 = EMA(time_period)
        self._ema3 = EMA(time_period)
        self._prev = TimedFloat()
        self._time_unit = time_unit

    def insert(self, data: TimedFloat) -> TimedFloat:
        ema1 = self._ema1.insert(data)
        ema2 = self._ema2.insert(ema1)
        ema3 = self._ema3.insert(ema2)
        if not self._prev or self._prev.time == data.time:
            self._prev = ema3
            return TimedFloat()
        value = (ema3.value - self._prev.value) / self._prev.value / \
            ((data.time - self._prev.time) / self._time_unit) * 100.
        self._prev = ema3
        return TimedFloat(data.time, value)


class MASS_n(Indicator):  # Normalized
    fast_period: datetime.timedelta
    slow_period: datetime.timedelta
    bar_period: datetime.timedelta
    _high: High
    _low: Low
    _ema1: EMA
    _ema2: EMA
    _sum: Sum

    def __init__(self, fast_period: datetime.timedelta, slow_period: datetime.timedelta, bar_period: datetime.timedelta):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.bar_period = bar_period
        self._high = High(bar_period)
        self._low = Low(bar_period)
        self._ema1 = EMA(fast_period)
        self._ema2 = EMA(fast_period)
        self._sum = Sum(slow_period)

    def insert(self, data: TimedFloat) -> TimedFloat:
        high = self._high.insert(data)
        low = self._low.insert(data)
        diff = TimedFloat(data.time, high.value - low.value)
        ema1 = self._ema1.insert(diff)
        ema2 = self._ema2.insert(ema1)
        diff2 = TimedFloat(data.time,
                           (ema1.value - ema2.value) / (high.value + low.value))
        return self._sum.insert(diff2)


class DPO(Indicator):
    time_period: datetime.timedelta
    _ma: MA
    _deque: collections.deque[TimedFloat]

    def __init__(self, time_period: datetime.timedelta):
        self.time_period = time_period
        self._ma = MA(time_period)
        self._deque = collections.deque()

    def insert(self, data: TimedFloat) -> TimedFloat:
        self._deque.append(data)
        while self._deque and self._deque[0].time < data.time - self.time_period / 2.:
            self._deque.popleft()
        mid = self._deque[0]
        ma = self._ma.insert(data)
        return TimedFloat(data.time, mid.value - ma.value)


class DPO_n(Indicator):  # Normalized
    time_period: datetime.timedelta
    _ma: MA
    _deque: collections.deque[TimedFloat]

    def __init__(self, time_period: datetime.timedelta):
        self.time_period = time_period
        self._ma = MA(time_period)
        self._deque = collections.deque()

    def insert(self, data: TimedFloat) -> TimedFloat:
        self._deque.append(data)
        while self._deque and self._deque[0].time < data.time - self.time_period / 2.:
            self._deque.popleft()
        mid = self._deque[0]
        ma = self._ma.insert(data)
        return TimedFloat(data.time, (mid.value - ma.value) / ma.value)
