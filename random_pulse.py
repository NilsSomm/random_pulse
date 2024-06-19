#Nils Sommerfeld
#random_pulse.py
#12/12/2023

#random_laser_pulse
#Class to create a laser pulse, using random numbers to generate different phases for a range of frequencies.

#Inputs:
#amplitude: the peak amplitude that the random numbers are generated at
#freq_sample_start: the frequency (ev) to start assigning random numbers to the frequencies
#freq_sample_end: the frequency (ev) to end the assigning of random numbers
#zeros_end: the frequency (ev) to end the zero-padding at
#freq_spacing_factor: the sample spacing multiplier of the frequencies: multiplier * 2 * pi * fel_pulse_duration. should be <= 0.1.
#fel_pulse_duration: the FWHM of the pulse squared in the temporal domain (fs)
#envelope_shape: the fuction of the envelope, currently only 'gauss' is supported
#random_mod_function: only 'gauss', 'none' right now - changes the amplitude of the random numbers generated
#random_mod_fwhm: the bandwidth (ev) of the random numbers (FWHM) (in intensity) of the function modifying the random numbers
#random_mod_center: the central wavelength (ev) of the mod function
#normalize: whether to normalize around the 'multiplier' input

#Outputs:
#get_time_series (np array) - returns time series of the generated pulse that corresponds with the time domain
#get_time_domain (np array) - returns the time axis
#get_time_spacing (float) - returns spacing between elements of the time domain
#get_time_envelope (np array) - returns the envelope of the time series
#get_freq_series (np array) - returns the frequency series of the generated pulse that corresponds with the frequency domain
#get_freq_domain (np array) - returns the frequency axis
#get_pos_freq_series (np array) - returns the frequency series of the generated pulse that corresponds with the positive frequency domain. The negative frequencies can be ignored during analysis because the negative frequencies are the complex conjugate of the postive frequencies.
#get_pos_freq_domain (np array) - returns the positive frequency axis
#get_freq_spacing (float) - returns spacing between elements of the frequency domain



import numpy as np
from scipy.fft import fft, fftfreq, ifft, fftshift, ifftshift


class random_laser_pulse:
    def __init__(self, amplitude = 1, freq_sample_start = 40, freq_sample_end = 50, zeros_end = 100, freq_spacing_factor = 0.1, fel_pulse_duration = 25, envelope_shape = 'gauss', random_mod_function = 'gauss', random_mod_fwhm = 1.1, random_mod_center = 45, normalize = True):
        
        #raise errors if bad inputs
        if (envelope_shape != 'gauss'):
            raise ValueError ('Invalid envelope_shape setting')
        if (random_mod_function != 'none' and random_mod_function != 'gauss'):
            raise ValueError ('Invalid random_mod_function settting')
        if (freq_sample_start > freq_sample_end):
            raise ValueError ('Sample range boundaries error')
        if (freq_sample_end > zeros_end):
            raise ValueError ('Zero-padding boundary error')
        
        #define some values
        self.frequency_spacing = freq_spacing_factor * 2 * np.pi / fel_pulse_duration
        normalization_factor = 1/np.sqrt(freq_spacing_factor)
        fwhm_inten_to_sigma = np.sqrt(2) / 2.355
        oneoverroot2pi = 1/np.sqrt(2*np.pi)
        ev_conv = 1/4.137
        
        #convert input frequencies to indeces (+1 is due to the 0 position being reserved for the 0 freq term)
        start_index = int(round(freq_sample_start / self.frequency_spacing)) + 1
        end_index = int(round(freq_sample_end / self.frequency_spacing)) + 1
        middle_index = int(round(random_mod_center / self.frequency_spacing)) + 1
        num_samples = end_index - start_index
        sigma_f = (random_mod_fwhm / self.frequency_spacing)*fwhm_inten_to_sigma
        
        #set up the inverse FFT
        self.n = 2 * int(round(zeros_end/self.frequency_spacing)) + 1
        self.ifft_in = np.zeros([self.n], dtype = np.cdouble)
        
        #loop over range of random frequencies
        for i in range(self.n//2 + start_index, self.n//2 + end_index, 1):
            self.ifft_in[i] = amplitude * np.exp(((np.random.random() * 2) - 1) * np.pi * 1j) #generate random phase
            self.ifft_in[i] *= np.exp(-0.5 * np.square((i - middle_index - self.n//2)/sigma_f)) #multiply by a gaussian
            if (normalize):
                self.ifft_in[i] *= normalization_factor
        
        #do inverse fourier transform and define time domain
        self.raw_waveform = ifftshift(np.real(ifft(fftshift(self.ifft_in)))) * self.n * self.frequency_spacing * oneoverroot2pi / np.sqrt(ev_conv)
        self.ts = fftshift(fftfreq(self.n, d=self.frequency_spacing)) * 2 * np.pi * ev_conv #fs^-1 to ev
        
        #throw a gauss envelope on top
        sigma_t = fel_pulse_duration * fwhm_inten_to_sigma
        self.envelope = np.exp(-0.5 * np.square(self.ts/sigma_t))
        self.waveform_adjusted = self.raw_waveform * self.envelope
        
        #do an fft back to the spectral domain
        self.time_spacing = self.ts[2]-self.ts[1]
        self.freqs = fftshift(fft(ifftshift(self.waveform_adjusted))) * self.time_spacing * oneoverroot2pi / np.sqrt(ev_conv)
        self.freq_domain = fftshift(fftfreq(len(self.freqs), d=self.time_spacing) * 2 * np.pi * ev_conv)
        
        #TIME ENVELOPE
        #create frequency range with one set of frequencies around zero
        self.envelope_ifft_in = np.zeros([self.n], dtype = np.cdouble)
        self.envelope_ifft_in[self.n//2 - num_samples//2 : self.n//2 + num_samples//2] = self.freqs[self.n//2 + start_index : self.n//2 + end_index - (num_samples % 2)] * 2
        
        #fft this
        self.time_envelope = ifftshift(np.abs(ifft(fftshift(self.envelope_ifft_in)))) * self.n * self.frequency_spacing * oneoverroot2pi / np.sqrt(ev_conv)
        #time series is already defined
        
        
    
    
    def get_time_series(self):
        return self.waveform_adjusted
    def get_time_domain(self):
        return self.ts
    def get_freq_series(self):
        return self.freqs
    def get_freq_domain(self):
        return self.freq_domain
    def get_pos_freq_series(self):
        return self.freqs[self.n//2:] * np.sqrt(2)
    def get_pos_freq_domain(self):
        return self.freq_domain[self.n//2:]
    def get_time_spacing(self):
        return self.time_spacing
    def get_freq_spacing(self):
        return self.frequency_spacing
    def get_time_envelope(self):
        return self.time_envelope