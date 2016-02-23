# coding=utf-8
__author__ = 'AleB'
import numpy as np
from scipy import interpolate


def derive(data, labels):
    ll = []
    tt = []
    ii = []
    ts = 0
    pre = None
    for i in xrange(len(labels)):
        if pre != labels[i]:
            ll.append(labels[i])
            tt.append(ts)
            ii.append(i)
            ts += data[i]
            pre = labels[i]
    return ll, tt, ii


def power(spec, freq, min_freq, max_freq):
    """
    Returns the power calculated in the specified band of the spec-freq spectrum
    """
    band = np.array([spec[i] for i in range(len(spec)) if min_freq <= freq[i] < max_freq])
    return np.sum(band) / len(spec)


def interpolate_ibi(rr, interp_freq):
    """
    Returns as a tuple the interpolated RR and BT arrays
    """
    step = 1.0 / interp_freq
    rr /= 1000
    rr = np.array(rr)
    bt = np.cumsum(rr)
    x_min = bt[0]
    x_max = bt[-1]
    bt = np.insert(bt, 0, 0)
    bt = np.append(bt, bt[-1] + 1)
    rr = np.insert(rr, 0, 0)
    rr = np.append(rr, rr[-1])
    tck = interpolate.splrep(bt, rr)
    bt_interp = np.arange(x_min, x_max, step)
    rr_interp = interpolate.splev(bt_interp, tck)
    return rr_interp, bt_interp


def template_interpolation(x, t, step, template=None):
    if template is None:
        template = np.square(np.cos(np.arange(0, 0.505, 0.005) * np.pi))

    x_old = x[0]
    t_old = t[0]

    x_out = np.array([])
    t_out = np.array([])

    for i in xrange(1, len(x)):
        x_curr = x[i]
        t_curr = t[i]

        x_template = template * (x_old - x_curr) + x_curr
        t_template = np.linspace(t_old, t_curr, 101)

        x_out = np.hstack((x_out, x_template, x_curr))
        t_out = np.hstack((t_out, t_template, t_curr))

        t_old = t_curr
        x_old = x_curr

    t_output = np.arange(t[0], t[-1], step)

    f = interpolate.interp1d(t_out, x_out, 'linear')
    x_output = f(t_output)
    return x_output, t_output