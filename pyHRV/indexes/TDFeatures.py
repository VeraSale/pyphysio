__author__ = 'AleB'
__all__ = ['Mean', 'Median', 'SD', 'SDSD', 'NN10', 'NN25', 'NN50', 'NNx', 'PNN10', 'PNN25', 'PNN50', 'PNNx', 'RMSSD',
           'HRMean', 'HRMedian', "Triang", "TINN"]

import numpy as np

from pyHRV.indexes.CacheOnlyFeatures import CacheableDataCalc, Diff, Histogram, HistogramMax
from pyHRV.indexes.BaseFeatures import TDFeature
from pyHRV.PyHRVSettings import MainSettings as Sett
from pyHRV.indexes.SupportValues import SumSV, LengthSV, DiffsSV, MedianSV


class Mean(TDFeature, CacheableDataCalc):
    """
    Calculates the average of the data.
    """
    # PyPhysio ready

    def __init__(self, data=None):
        super(Mean, self).__init__(data)
        self._value = Mean.get(self._data)

    @classmethod
    def _calculate_data(cls, data, params):
        return np.mean(data)

    @classmethod
    def required_sv(cls):
        return [SumSV, LengthSV]

    @classmethod
    def calculate_on(cls, state):
        return state[SumSV].value / float(state[LengthSV].value)


class Median(TDFeature, CacheableDataCalc):
    """
    Calculates the median of the data series.
    """
    # PyPhysio ready

    def __init__(self, data=None):
        super(Median, self).__init__(data)
        self._value = Median.get(self._data)

    @classmethod
    def _calculate_data(cls, data, params):
        return np.median(data)

    @classmethod
    def required_sv(cls):
        return [MedianSV]

    @classmethod
    def calculate_on(cls, state):
        return state[MedianSV].value


class SD(TDFeature, CacheableDataCalc):
    """
    Calculates the standard deviation of the data series.
    """
    # PyPhysio ready

    def __init__(self, data=None):
        super(SD, self).__init__(data)
        self._value = SD.get(self._data)

    @classmethod
    def _calculate_data(cls, data, params):
        return np.std(data)


class HRSD(TDFeature, CacheableDataCalc):
    """
    Calculates the average of the data series and converts it into Beats per Minute.
    """

    def __init__(self, data=None):
        super(HRSD, self).__init__(data)
        self._value = HRSD.get(self._data)

    @classmethod
    def _calculate_data(cls, data, params):
        return np.std(60 / data)


class PNNx(TDFeature):
    """
    Calculates the presence proportion (0.0-1.0) of pairs of consecutive IBIs in the data series
    where the difference between the two values is greater than the parameter (threshold).
    """

    def __init__(self, data=None, threshold=None):
        super(PNNx, self).__init__(data)
        self._xth = threshold if not threshold is None else self.threshold()
        self._value = NNx(data, self._xth).value / float(len(data))

    @staticmethod
    def threshold():
        return Sett.nnx_default_threshold

    @classmethod
    def required_sv(cls):
        return NNx.required_sv()

    @classmethod
    def calculate_on(cls, state):
        return NNx.calculate_on(state, cls.threshold()) / float(state[LengthSV].value)


class NNx(TDFeature):
    """
    Calculates the number of pairs of consecutive IBIs in the data series where the difference between
    the two values is greater than the parameter (threshold).
    """

    def __init__(self, data=None, threshold=None):
        super(NNx, self).__init__(data)
        self._xth = threshold if not threshold is None else self.threshold()
        diff = Diff.get(self._data)
        self._value = sum(1.0 for x in diff if x > self._xth)

    @staticmethod
    def threshold():
        return Sett.nnx_default_threshold

    @classmethod
    def required_sv(cls):
        return [DiffsSV]

    @classmethod
    def calculate_on(cls, state, threshold=None):
        if threshold is None:
            threshold = cls.threshold()

        return sum(1 for x in state[DiffsSV].value if x > threshold)


class PNN10(PNNx):
    """
    Calculates the presence proportion (0.0-1.0) in the data series of pairs of consecutive IBIs
    where the difference between the two values is greater than 10.
    """

    @staticmethod
    def threshold():
        return 10


class PNN25(PNNx):
    """
    Calculates the presence proportion (0.0-1.0) in the data series of pairs of consecutive IBIs
    where the difference between the two values is greater than 25.
    """

    @staticmethod
    def threshold():
        return 25


class PNN50(PNNx):
    """
    Calculates the presence proportion (0.0-1.0) in the data series of pairs of consecutive IBIs
    where the difference between the two values is greater than 50.
    """

    @staticmethod
    def threshold():
        return 50


class NN10(NNx):
    """
    Calculates number of pairs of consecutive IBIs in the data series where the difference between
    the two values is greater than 10.
    """

    @staticmethod
    def threshold():
        return 10


class NN25(NNx):
    """
    Calculates number of pairs of consecutive IBIs in the data series where the difference between
    the two values is greater than 25.
    """

    @staticmethod
    def threshold():
        return 25


class NN50(NNx):
    """
    Calculates number of pairs of consecutive IBIs in the data series where the difference between
    the two values is greater than 50.
    """

    @staticmethod
    def threshold():
        return 50


class SDSD(TDFeature):
    """Calculates the standard deviation of the differences between each value and its next."""

    def __init__(self, data=None):
        super(SDSD, self).__init__(data)
        diff = Diff.get(self._data)
        self._value = np.std(diff)


#TODO: fix documentation
class Triang(TDFeature):
    """Calculates the Triangular HRV index."""

    def __init__(self, data=None):
        super(Triang, self).__init__(data)
        h, b = Histogram.get(self._data)
        self._value = len(self._data) / np.max(h)


#TODO: fix documentation
class TINN(TDFeature):
    """Calculates the difference between two histogram-related indexes."""

    def __init__(self, data=None):
        super(TINN, self).__init__(data)
        hist, bins = Histogram.get(self._data)
        max_x = HistogramMax.get(self._data)
        hist_left = np.array(hist[0:np.argmax(hist)])
        ll = len(hist_left)
        hist_right = np.array(hist[np.argmax(hist):-1])
        rl = len(hist_right)

        y_left = np.array(np.linspace(0, max_x, ll))

        minx = np.Inf
        pos = 0
        for i in range(len(hist_left) - 1):
            curr_min = np.sum((hist_left - y_left) ** 2)
            if curr_min < minx:
                minx = curr_min
                pos = i
            y_left[i] = 0
            y_left[i + 1:] = np.linspace(0, max_x, ll - i - 1)

        n = bins[pos - 1]

        y_right = np.array(np.linspace(max_x, 0, rl))
        minx = np.Inf
        pos = 0
        for i in range(rl, 1, -1):
            curr_min = np.sum((hist_right - y_right) ** 2)
            if curr_min < minx:
                minx = curr_min
                pos = i
            y_right[i - 1] = 0
            y_right[0:i - 2] = np.linspace(max_x, 0, i - 2)

        m = bins[np.argmax(hist) + pos + 1]

        self._value = m - n