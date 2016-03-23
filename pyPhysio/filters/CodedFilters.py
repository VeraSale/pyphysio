# coding=utf-8
# TODO: from __future__ import division
import numpy as _np
from scipy.signal import _gaussian, _filtfilt, _filter_design
from ..BaseFilter import Filter as _Filter
from ..PhUI import PhUI as _PhUI
from ..indicators.Indicators import Mean as _Mean, SD as _SD

__author__ = 'AleB'

"""
Filters are processing steps that take as input a SIGNAL and gives as output another SIGNAL of the SAME NATURE.
"""

class Normalize(_Filter):
    """
    Normalizes the series removing the mean (val-mean)
    """

    class Types(object):
        Same = -1
        Mean = 0
        MeanSd = 1
        Min = 2
        MaxMin = 3
        Custom = 4

    @classmethod
    def algorithm(cls, signal, params):
        if 'norm_type' not in params:
            _PhUI.i("Assuming Mean normalization.")
            return Normalize._mean(signal)
        else:
            if params['norm_type'] == Normalize.Types.Mean:
                return Normalize._mean(signal)
            elif params['norm_type'] == Normalize.Types.MeanSd:
                return Normalize._mean_sd(signal)
            elif params['norm_type'] == Normalize.Types.Min:
                return Normalize._min(signal)
            elif params['norm_type'] == Normalize.Types.MaxMin:
                return Normalize._max_min(signal)
            elif params['norm_type'] == Normalize.Types.Custom:
                return Normalize._custom(signal, params['norm_bias'], params['norm_range'])
            elif params['norm_type'] == Normalize.Types.Same:
                return signal
    
    @classmethod
    def _check_params(params):
        if (not 'norm_type' in params):
            # action_param(params, NORM_TYPE=-1, 'Normalization not computed')
            pass
        elif (params['norm_type'] == Normalize.Types.Custom) & ((not 'norm_bias' in params) | (not 'norm_range' in params)):
            # action_param(params) NO DEFAULT, STOP
            pass
        return params
        
    @staticmethod
    def _mean(signal):
        """
        Normalizes the signal removing the mean (val-mean)
        """
        return signal - _Mean.get(signal)

    @staticmethod
    def _mean_sd(signal):
        """
        Normalizes the signal removing the mean and dividing by the standard deviation (val-mean)/sd
        """
        return signal - _Mean.get(signal) / _SD.get(signal)

    @staticmethod
    def _min(signal):
        """
        Normalizes the signal removing the minimum value (val-min)
        """
        return signal - _np.min(signal)

    @staticmethod
    def _max_min(signal):
        """
        Normalizes the signal removing the min value and dividing by the range width (val-min)/(max-min)
        """
        return (signal - _np.min(signal)) / (np.max(signal) - _np.min(signal))

    @staticmethod
    def _custom(signal, bias, nrange):
        """
        Normalizes the signal considering two factors ((val-bias)/nrange)
        """
        return (signal - bias) / normalization_range

class Diff(_Filter):
    @classmethod
    def algorithm(cls, signal, params):
        """
        Calculates the differences between consecutive values
        :param signal:
        """
        # TODO: Manage Time references, in particular if Unevenly (to be discussed...)
        
        return _np.diff(signal)

class IIRFilter(_Filter):
    '''
    Filter the input signal using an Infinite Inpulse Response filter.
    
    Parameters
    ----------
    fp : list
        The pass frequencies normalized to 
    fs : list
        The stop frequencies
    loss : float (default)
        Loss tolerance in the pass band
    att : float
        Minimum attenuation required in the stop band.
    ftype : str
        Type of filter. 
    
    Returns
    -------
    Signal : the filtered signal
    
    Notes
    -----
    See :func:`scipy.signal.filter_design.iirdesign` for additional information
    '''
    
    @classmethod
    def algorithm(cls, signal, fp, fs, loss, att, ftype):
		fsamp = signal.fsamp
		
		# TODO: if A and B already exist and fsamp is not changed skip following
		
		#---------
		#TODO: check that fs and fp are meaningful
		#TODO: check if fs, fp, fsamp allow no solution for the filter
		nyq = 0.5 * fsamp
		fp = _np.array(fp)
		fs = _np.array(fs)
		wp = fp/nyq
		ws = fs/nyq
		b, a = _filter_design.iirdesign(wp, ws, loss, att, ftype=ftype)
		if _np.isnan(b[0]) | _np.isnan(a[0]):
			action_warning('Filter parameters allow no solution') # STOP o continua con segnale originario
		#---------
		return(_filtfilt(b,a,signal))
    
    @classmethod
    def _check_params(params):
        if (not 'fp' in params):
	    #no default # GRAVE
            pass
        if (not 'fs' in params):
	    #no default # GRAVE
            pass
        if (not 'loss' in params):
	    #default 0.1 # OK
            pass
        if (not 'att' in params):
	    #default 40 # OK
            pass
        if (not 'ftype' in params):
	    #default 'butter' # OK
            pass
        return params
    
    @classmethod
    def plot():
	#plot frequency response
	pass
        
class MatchedFilter(_Filter):
    '''
    Matched filter
    
    It generates a template using reference indexes and filters the signal.
    
    Parameters
    ----------
    template : nparray
        The template for matched filter (not reversed)
    
    Returns
    -------
    filtered_signal : nparray
        The filtered signal
        
    Notes
    -----
    See `matched filter`_ in Wikipedia.
    
    '''
    
    @classmethod
    def algorithm(cls, signal, template):
	filtered_signal = _np.convolve(signal, template)
	filtered_signal = filtered_signal[_np.argmax(template):]
	return(filtered_signal)
    
    @classmethod
    def _check_params(params):
	if (not 'template' in params):
	    #no default # GRAVE
            pass
	return(params)
    
    @classmethod
    def plot(cls):
	#plot template
	pass

class ConvolutionalFilter(_Filter):
    '''
    Convolution-based filter
    
    It filters a signal by convolution with a given impulse response function (IRF).
    
    Parameters
    ----------
    irftype : str
        Type of IRF to be generated. 'gauss', 'rect', 'triang', 'dgauss', 'custom'.
    N : int
        Number of samples to generate the IRF
    irf : nparray
        If given it is used as IRF
    normalize : boolean
        If True it normalizes the IRF to have unitary area
    
    Returns
    -------
    filtered_signal : nparray
        The filtered signal
        
    Notes
    -----
    '''
    class Types(object):
        Same = 'none'
        Gauss = 'gauss'
        Rect = 'rect'
        Triang = 'triang'
        Dgauss = 'dgauss'
        Custom = 'custom'
        
    @classmethod
    def algorithm(cls, signal, irftype, N, irf, normalize):
	if irftype == 'gauss':
            std = _np.floor(N/8)
            irf = _gaussian(N, std)
        elif irftype == 'rect':
            irf = _np.ones(N)
        elif irftype == 'triang':
            irf_1 = _np.arange(_np.floor(N/2))
            irf_2 = irf_1[-1] - _np.arange(_np.floor(N/2))
            if N%2==0:
                irf = _np.r_[irf_1, irf_2]
            else:
                irf = _np.r_[irf_1, irf_1[-1]+1, irf_2]
        elif irftype == 'dgauss':
            std = _np.floor(N/8)
            g = _gaussian(N, std)
            irf = _np.diff(g)
        elif irftype == 'custom':
            irf = _np.array(irf)

	# NORMALIZE
	if normalize:
	    irf = irf/np.sum(irf) #TODO account fsamp
	    
	signal_ = _np.r_[_np.ones(N)*signal[0], signal, _np.ones(N)*signal[-1]]
	
	signal_f = _np.convolve(signal_, irf, mode='same')
	signal_out = signal_f[N:-N]
	return(signal_out)
    
    
    @classmethod
    def _check_params(params):
        if not 'irftype' in params:
            # no default # GRAVE
            pass
        else:
	    if (params['irftype'] == Normalize.Types.Custom) & (not 'irf' in params):
		# no default # GRAVE
		pass
	    elif not 'N' in params:
		# no default # GRAVE
		pass
	    elif not isinstance(N, int):
	      pass
	if not 'normalize' in params:
	    # default = True # OK
        return params
    
    @classmethod
    def plot(cls):
	#plot irf
	pass
    
class DeConvolutionalFilter(_Filter):
    '''
    Convolution-based filter
    
    It filters a signal by deconvolution with a given impulse response function (IRF).
    
    Parameters
    ----------
    irf : nparray
        If given it is used as IRF
    normalize : boolean
        If True it normalizes the IRF to have unitary area
    
    Returns
    -------
    filtered_signal : nparray
        The filtered signal
        
    Notes
    -----
    '''
    class Types(object):
        Same = 'none'
        Gauss = 'gauss'
        Rect = 'rect'
        Triang = 'triang'
        Dgauss = 'dgauss'
        Custom = 'custom'
        
    @classmethod
    def algorithm(cls, signal, irf, normalize):
	if normalize:
	    irf = irf/np.sum(irf)
	L=len(signal)
	fft_signal = _np.fft.fft(signal, n=L)
	fft_signal = _np.fft.fft(irf, n=L)
	out = _np.fft.ifft(fft_signal/fft_irf)
	
	return(abs(out))

    @classmethod
    def _check_params(params):
        if not 'irf' in params:
            # no default # GRAVE
            pass
        if not 'normalize' in params:
	    # default = True # OK
        return params
    
    @classmethod
    def plot(cls):
	#plot irf
	pass

class AdaptiveThresholding(_Tool):
	'''
	Adaptively (windowing) threshold the signal using C*std(signal) as thresholding value.
	See Raju 2014.

	Parameters
	----------
	signal : nparray
		The input signal
	winlen : int
		Size of the window
	C : float
		Coefficient for the threshold

	Returns
	-------
	thresholded_signal : nparray
		The thresholded signal
	'''
	@classmethod
	def algorithm(cls, signal, params):
		winlen = params['win_len']
		C = params['C']
		winlen = int(_np.round(winlen))
		signal = _np.array(signal)
		signal_out = _np.zeros(len(signal))
		for i in range(0, len(signal), winlen):
			curr_block = signal[i:i+winlen]
			eta = C*_np.std(curr_block)
			curr_block[curr_block<eta]=0
			signal_out[i:i+winlen] = curr_block
		
		return(signal_out)
	
	@classmethod
    def check_params(cls, params):
		if not 'win_len' in params:
			#default = 100 # GRAVE
			pass
		if not 'C' in params:
			#default = 1 # OK
			pass
		return(params)