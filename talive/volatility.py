from basic import *


class ULCER(Indicator):
    _time_period: datetime.timedelta
    _high: High
    _ma: MA

    def __init__(self, time_period: datetime.timedelta):
        self._time_period = time_period
        self._high = High(time_period)
        self._ma = MA(time_period)

    def insert(self, data: TimedFloat) -> TimedFloat:
        high = self._high.insert(data)
        diff = (data.value - high.value) / high.value * 100.
        ma = self._ma.insert(TimedFloat(data.time, diff * diff))
        if ma.value <= 0.:
            return TimedFloat(data.time, 0.)
        return TimedFloat(data.time, math.sqrt(ma.value))
