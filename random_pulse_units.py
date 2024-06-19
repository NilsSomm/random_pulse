#fel_pulse.py

#This class uses the random_laser_pulse class from random_pulse.py. The inputs are simplified 

#inputs:
#units_in - input units, 'si' or 'au'.
#units_out - output units, 'si' or 'au'
#amplitude - height factor of the signal
#freq_spacing_factor - Defines frequency spacing by the formula frequency spacing = freq_spacing_factor*2*pi/pulse_duration. Should be set to at most 0.1. The smaller the more points, but the longer it takes to generate the pulse.
#pulse_duration - width of the FWHM of the average intensity envelope of the time signal. fs in 'si' unit set.
#bandwidth - width of the FWHM of the average intensity envelope of the frequency signal. eV in 'si' unit set.
#central_freq - central frequency of the frequency signal. eV in 'si' unit set

#outputs
#get_time_series (np array) - returns time series of the generated pulse that corresponds with ->
#get_time_domain (np array) - returns the time axis, the spacing between points is given by ->
#get_time_spacing (float) - 
#get_time_envelope (np array) - returns the envelope of the time series

#get_freq_series
#get_freq_domain
#get_pos_freq_series
#get_pos_freq_domain
#get_freq_spacing

import numpy as np
from unitConv import unitConverter
from random_pulse import random_laser_pulse
class fel_pulse():
    def __init__(self, units_in = 'si', units_out = 'si', amplitude = 1, freq_spacing_factor = 0.05, pulse_duration = 25, bandwidth = 1, central_freq = 45):
        #tu = to use
        amp_tu = amplitude
        pd_tu = pulse_duration
        band_tu = bandwidth
        cnfrq_tu = central_freq
        
        self.units_out = units_out
        
        self.unitC = unitConverter()
        if units_in == 'au':
            pd_tu = self.unitC.au2fs(pd_tu)
            amp_tu = amp_tu #units??
            band_tu = self.unitC.au2ev(band_tu)
            cnfrq_tu = self.unitC.au2ev(cnfrq_tu)
        
        self.rp = random_laser_pulse(amplitude = amp_tu, freq_sample_start = cnfrq_tu - (band_tu*4), freq_sample_end = cnfrq_tu + (band_tu*4), zeros_end = (cnfrq_tu+(band_tu*4)) * 8, freq_spacing_factor = freq_spacing_factor, fel_pulse_duration = pd_tu, envelope_shape = 'gauss', random_mod_function = 'gauss', random_mod_fwhm = band_tu, random_mod_center = cnfrq_tu, normalize = True)
        
    def get_time_series(self):
        if self.units_out == 'au':
            return self.get_time_series() / np.sqrt(self.unitC.fs2au(1))
        return self.rp.get_time_series()
    def get_time_envelope(self):
        if self.units_out == 'au':
            return self.rp.get_time_envelope() / np.sqrt(self.unitC.fs2au(1))
        return self.rp.get_time_envelope()
    def get_time_domain(self):
        if self.units_out == 'au':
            return self.unitC.fs2au(self.get_time_domain())
        return self.rp.get_time_domain()
    def get_freq_series(self):
        if self.units_out == 'au':
            return self.rp.get_freq_series() / np.sqrt(self.unitC.ev2au(1))
        return self.rp.get_freq_series()
    def get_freq_domain(self):
        if self.units_out == 'au':
            return self.unitC.ev2au(self.rp.get_freq_domain())
        return self.rp.get_freq_domain()
    def get_pos_freq_series(self):
        if self.units_out == 'au':
            return self.rp.get_pos_freq_series() / np.sqrt(self.unitC.ev2au(1))
        return self.rp.get_pos_freq_series()
    def get_pos_freq_domain(self):
        if self.units_out == 'au':
            return self.unitC.ev2au(self.rp.get_pos_freq_domain())
        return self.rp.get_pos_freq_domain()
    def get_time_spacing(self):
        if self.units_out == 'au':
            return self.unitC.fs2au(self.rp.get_time_spacing())
        return self.rp.get_time_spacing()
    def get_freq_spacing(self):
        if self.units_out == 'au':
            return self.unitC.ev2au(self.rp.get_freq_spacing())
        return self.rp.get_freq_spacing()
        
        
        
