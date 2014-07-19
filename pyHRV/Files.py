__all__ = ['load_pd_from_excel_column', 'load_ds_from_csv_column', 'load_ds_from_csv_column', 'save_ds_to_csv',
           'load_rr_from_bvp',
           'load_rr_from_ecg']

import numpy as np

import pandas as pd

from pyHRV.DataSeries import DataSeries
from pyHRV.utility import peak_detection
from pyHRV.PyHRVSettings import PyHRVDefaultSettings as Sett
from pyHRV.windowing.WindowsBase import Window
from pyHRV.windowing.WindowsGenerators import CollectionWinGen


def load_pd_from_excel_column(path, column, column_b=None, sheet_name=0):
    """Loads one or two columns as pandas.Series from an excel format file."""
    if column_b is None:
        a = pd.read_excel(path, sheet_name)
        return a[column] if isinstance(column, basestring) else a[a.columns[column]]
    else:
        a = pd.read_excel(path, sheet_name)
        b = pd.read_excel(path, sheet_name)
        a = a[column] if isinstance(column, basestring) else a[a.columns[column]]
        b = b[column_b] if isinstance(column_b, basestring) else b[b.columns[column_b]]
        return a, b


def load_ds_from_csv_column(path, column=Sett.load_rr_column_name, sep=Sett.load_csv_separator):
    """Loads a column from a csv file."""
    d = pd.read_csv(path, sep)
    if not column in d.columns:
        column = d.columns[0]
    inst = DataSeries(np.array(d[column]))
    inst.name = column
    return inst


def load_windows_gen_from_csv(path, column_begin=Sett.load_windows_col_begin, column_end=Sett.load_windows_col_end,
                              sep=Sett.load_csv_separator):
    """Loads a CollectionWinGen from a csv column"""
    d = pd.read_csv(path, sep=sep)
    assert len(d[column_begin]) == len(d[column_end])
    return CollectionWinGen(map((lambda x, y: Window(x, y)), d[column_begin], d[column_end]))


def save_ds_to_csv(data_series, path, sep=Sett.load_csv_separator, header=True):
    """Saves the DataSeries (rr) to a csv file."""
    assert isinstance(data_series, pd.Series)
    data_series.name = Sett.load_rr_column_name
    data_series.to_csv(path, sep=sep, header=header)


def load_rr_from_ecg(path, delta=Sett.import_ecg_delta, sep=Sett.load_csv_separator, *args):
    """Loads an IBI (RR) data series from an ECG data set and filters it with the specified filters list."""
    df = pd.read_csv(path, sep=sep, *args)
    max_tab, min_tab = peak_detection(df[Sett.load_ecg_column_name], delta,
                                      df[Sett.load_ecg_time_column_name])
    s = DataSeries(np.diff(max_tab))
    for f in Sett.import_ecg_filters:
        s = f(s)
    s.meta_tag['from_type'] = "csv_ecg"
    s.meta_tag['from_delta'] = delta
    s.meta_tag['from_filters'] = list(Sett.import_ecg_filters)
    return s


def load_rr_from_bvp(path, delta_ratio=Sett.import_bvp_delta_max_min_numerator, sep=Sett.load_csv_separator,
                     filters=Sett.import_bvp_filters, *args):
    """Loads an IBI (RR) data series from a BVP data set and filters it with the specified filters list."""
    df = pd.read_csv(path, sep=sep, *args)
    delta = (np.max(df[Sett.load_bvp_column_name]) - np.min(df[Sett.load_bvp_column_name])) / delta_ratio
    max_i, ii, iii, iij = peak_detection(df[Sett.load_bvp_column_name], delta,
                                         df[Sett.load_bvp_time_column_name])
    s = DataSeries(np.diff(max_i) * 1000)
    for f in filters:
        s = f(s)
    s.meta_tag['from_type'] = "csv_bvp"
    s.meta_tag['from_delta'] = delta
    s.meta_tag['from_filters'] = list(Sett.import_bvp_filters)
    return s
