from pyHRV import DataSeries
from pyHRV.indexes.TDIndexes import Mean, SD
from pyHRV.windowing.WindowsBase import Window
from pyHRV.windowing.WindowsGenerators import LinearWinGen
from pyHRV.windowing.WindowsMapper import WindowsMapper

__author__ = 'AleB'

data = DataSeries([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

## Index class usage
# This is the simplest way to extract an index
value1 = Mean(data).value

## Index class usage with a window
# This is the simplest way to calculate an index on a window
win = Window(1, 5)
value2 = Mean(data[win]).value

## WindowsMapper usage
# This is the minimal structure of the code needed to calculate the indexes on each window
# Creating the windows (the data parameter is needed to know the total length)
win_gen = LinearWinGen(0, 2, 4, data)
# The mapper initialization (it will compute the mean and the standard deviation of each window
win_mapper = WindowsMapper(data, win_gen, [Mean, SD])
# The core work (here all the work is done)
win_mapper.compute_all()
# The results usage
results = win_mapper.results
# For the computing of both the Mean and the SD the mean value is needed so the cache will save it to avoid the multiple
# computation of the same value.