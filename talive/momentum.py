from basic import *


class RSI(Indicator):
    _time_period: datetime.timedelta
    _up_ema: EMA
    _down_ema: EMA
    _prev: TimedFloat

    def __init__(self, time_period: datetime.timedelta):
        self._time_period = time_period
        self._prev = TimedFloat()
        self._up_ema = EMA(time_period)
        self._down_ema = EMA(time_period)

    def insert(self, data: TimedFloat) -> TimedFloat:
        if not self._prev:
            self._prev = data
            return TimedFloat()
        diff = data.value - self.prev.value
        self.prev = data
        if diff > 0:
            up = self._up_ema.insert(TimedFloat(data.time, diff))
            down = self._down_ema.insert(TimedFloat(data.time, 0.))
        else:
            up = self._up_ema.insert(TimedFloat(data.time, 0.))
            down = self._down_ema.insert(TimedFloat(data.time, -diff))
        if down.value == 0.:
            return TimedFloat(data.time, 100.)
        return TimedFloat(data.time, 100. - 100. / (1. + up.value / down.value))


class TSI(Indicator):
    _fast_period: datetime.timedelta
    _slow_period: datetime.timedelta
    _prev: TimedFloat
    _ema_diff_fast: EMA
    _ema_diff_slow: EMA
    _ema_abs_fast: EMA
    _ema_abs_slow: EMA

    def __init__(self, fast_period: datetime.timedelta, slow_period: datetime.timedelta):
        self._fast_period = fast_period
        self._slow_period = slow_period
        self._prev = TimedFloat()
        self._ema_diff_slow = EMA(slow_period)
        self._ema_diff_fast = EMA(fast_period)
        self._ema_abs_slow = EMA(slow_period)
        self._ema_abs_fast = EMA(fast_period)

    def insert(self, data: TimedFloat) -> TimedFloat:
        if not self._prev:
            self._prev = data
            return TimedFloat()
        diff = data.value - self._prev.value
        diff_abs = abs(diff)
        self._prev = data
        ema_diff_slow = self._ema_diff_slow.insert(TimedFloat(data.time, diff))
        ema_abs_slow = self._ema_abs_slow.insert(
            TimedFloat(data.time, diff_abs))
        ema_diff_fast = self._ema_diff_fast.insert(ema_diff_slow)
        ema_abs_fast = self._ema_abs_fast.insert(ema_abs_slow)
        if ema_abs_fast == 0.:
            return TimedFloat()
        return TimedFloat(data.time, ema_diff_fast.value / ema_abs_fast.value * 100.)


class Stoch(Indicator):
    _time_period: datetime.timedelta
    _high: High
    _low: Low

    def __init__(self, time_period: datetime.timedelta):
        self._time_period = time_period
        self._high = High(time_period)
        self._low = Low(time_period)

    def insert(self, data: TimedFloat) -> TimedFloat:
        high = self._high.insert(data)
        low = self._low.insert(data)
        if high == low:
            return TimedFloat()
        return TimedFloat(data.time, (data.value - low.value) / (high.value - low.value))


class ROC(Indicator):
    _time_period: datetime.timedelta
    _deque: collections.deque[TimedFloat]

    def __init__(self, time_period: datetime.timedelta):
        self._time_period = time_period
        self._deque = collections.deque()

    def insert(self, data: TimedFloat) -> TimedFloat:
        self._deque.append(data)
        while self._deque and self._deque[0].time <= data.time - self._time_period:
            self._deque.popleft()
        return TimedFloat(data.time, (data.value - self._deque[0].value) / self._deque[0].value * 100.)


class WILLIAMSR(Indicator):
    _time_period: datetime.timedelta
    _high: High
    _low: Low

    def __init__(self, time_period: datetime.timedelta):
        self._time_period = time_period
        self._high = High(time_period)
        self._low = Low(time_period)

    def insert(self, data: TimedFloat) -> TimedFloat:
        high = self._high.insert(data)
        low = self._low.insert(data)
        if data.value == low.value:
            return TimedFloat(data.time, -100.)
        if high.value == low.value:
            return TimedFloat()
        value = -100. * (high.value - data.value) / (high.value - low.value)
        return TimedFloat(data.time, value)


class StochRSI(Indicator):
    _time_period: datetime.timedelta
    _rsi: RSI
    _stoch: Stoch

    def __init__(self, time_period: datetime.timedelta):
        self._time_period = time_period
        self._rsi = RSI(time_period)
        self._stoch = Stoch(time_period)

    def insert(self, data: TimedFloat) -> TimedFloat:
        rsi = self._rsi.insert(data)
        if not rsi:
            return TimedFloat()
        return self._stoch.insert(rsi)


class PPO(Indicator):
    _fast_period: datetime.timedelta
    _slow_period: datetime.timedelta
    _ema_fast: EMA
    _ema_slow: EMA

    def __init__(self, fast_period: datetime.timedelta, slow_period: datetime.timedelta):
        self._fast_period = fast_period
        self._slow_period = slow_period
        self._ema_fast = EMA(fast_period)
        self._ema_slow = EMA(slow_period)

    def insert(self, data: TimedFloat) -> TimedFloat:
        ema_fast = self._ema_fast.insert(data)
        ema_slow = self._ema_slow.insert(data)
        if ema_slow.value == 0.:
            return TimedFloat()
        return TimedFloat(data.time, (ema_fast.value - ema_slow.value) / ema_slow.value * 100.)
