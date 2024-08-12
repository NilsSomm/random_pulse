#Nils Sommerfeld
#pulse_detector.py
#create only one of these objects for one type of pulse
#08/05/2024
#Version 1.0
import numpy as np
from scipy.signal import decimate
from scipy.optimize import curve_fit

class pulse_detector:
    def __init__(self, time_axis, pulse_duration, pulse_center, time_spacing, frequency_axis, bandwidth, central_frequency, frequency_spacing, amplitude, max_freq_subpulses, max_time_subpulses, cutoff = 0.1,):
        
        self.time_spacing = time_spacing
        self.freq_spacing = frequency_spacing
        self.freq_axis = frequency_axis
        self.time_axis = time_axis
        self.max_freq_subpulses = max_freq_subpulses
        self.max_time_subpulses = max_time_subpulses
        self.cutoff = cutoff
        
        #define time window to check
        t_low = (-1.5 * pulse_duration) + pulse_center
        t_high = (1.5 * pulse_duration) + pulse_center
        self.n_time_low = -1
        self.n_time_high = -1
        for i in range(len(time_axis)):
            if time_axis[i] > t_low and self.n_time_low == -1:
                self.n_time_low = i
            if time_axis[i] > t_high and self.n_time_high == -1:
                self.n_time_high = i
        
        #define frequency window to check
        f_low = (-1.5 * bandwidth) + central_frequency
        f_high = (1.5 * bandwidth) + central_frequency
        self.n_freq_low = -1
        self.n_freq_high = -1
        for i in range(len(frequency_axis)):
            if frequency_axis[i] > f_low and self.n_freq_low == -1:
                self.n_freq_low = i
            if frequency_axis[i] > f_high and self.n_freq_high == -1:
                self.n_freq_high = i
    
        #define height predictions for pulse detections
        self.height_prediction_time = bandwidth / pulse_duration * np.square(amplitude) * 4.4
        self.height_prediction_freq = np.square(amplitude) * 2.2

        self.bandwidth = bandwidth
        self.central_freq = central_frequency
        self.pulse_duration = pulse_duration
        self.sigma_f = bandwidth * np.sqrt(2) / 2.355
        self.sigma_t = pulse_duration * np.sqrt(2) / 2.355
        
        self.subpulse_width_freq = 1/(np.sqrt(2)*pulse_duration)
    
    
    def detect_frequency(self, frequency_series):
        def Gauss(x, A, B):
            y = A*np.exp(-1*B*x**2)
            return y
        
        peaks = np.zeros([self.max_freq_subpulses, 3])
        itt_pulse = 0
        arr = np.square(np.abs(frequency_series[self.n_freq_low:self.n_freq_high]))
        freq_arr = self.freq_axis[self.n_freq_low:self.n_freq_high]
        len_arr = len(arr)
        max_index = -1
        max_val = -1
        index_prev = -1
        dif = 0
        left_ps = 0
        right_ps = 0
        while (itt_pulse < self.max_freq_subpulses):
            max_index = -1
            max_val = 0
            for i, val in enumerate(arr):
                if val > max_val:
                    max_index = i
                    max_val = val
            if (max_val < self.height_prediction_freq * self.cutoff):
                #print("break cutoff")
                break
            if index_prev == max_index:
                #print("break repetition: num pulses: " + str(len(peaks)))
                break
            if max_index == -1:
                #print("break no peak found: num pulses: " + str(len(peaks)))
                break
            index_prev = max_index
            
            dif = 0 #last_point - current_point
            dif_prev = 0 #before_last_point - last_point
            left_ps = -1
            itt = max_index
            prev_point = -1
            pred = self.height_prediction_freq*np.square(np.exp(-0.5 * np.square((freq_arr[max_index] - self.central_freq)/self.sigma_f)))
            while (max_index-left_ps > 1 and dif >= 0):
                dif_prev = dif
                itt -= 1
                dif = arr[itt+1] - arr[itt]
                left_ps += 1
                
            
            #go right
            dif = 0 #last_point - current_point
            dif_prev = 0 #before_last_point - last_point
            right_ps = -1
            itt = max_index
            while (max_index+right_ps < len_arr - 2 and dif >= 0):
                dif_prev = dif
                itt += 1
                dif = arr[itt-1] - arr[itt]
                right_ps += 1
            
            if ((right_ps > 1 and left_ps > 1) or arr[max_index] > pred):
                try: 
                    AandB, covariance = curve_fit(Gauss, np.linspace(-left_ps * self.freq_spacing, right_ps * self.freq_spacing, right_ps + left_ps + 1), arr[max_index - left_ps:max_index + right_ps + 1], maxfev = 1000)
                    peaks[itt_pulse,0] = freq_arr[max_index]
                    peaks[itt_pulse,1] = AandB[0]
                    peaks[itt_pulse,2] = AandB[1]
                    arr = arr - AandB[0] * np.exp(-AandB[1]*(freq_arr-freq_arr[max_index])**2)
                    arr[arr < 0] = 0
                    itt_pulse+=1
                except:
                    #print("early break, fitting error. num_pulses: " + str(len(peaks)))
                    break
        return peaks
    
    
    def detect_time(self, time_series):
        def Gauss(x, A, B):
            y = A*np.exp(-1*B*x**2)
            return y
        
        peaks = np.zeros([self.max_time_subpulses,3])
        itt_pulse = 0
        arr = np.square(np.abs(time_series[self.n_time_low:self.n_time_high]))
        time_arr = self.time_axis[self.n_time_low:self.n_time_high]
        len_arr = len(arr)
        max_index = -1
        max_val = -1
        index_prev = -1
        dif = 0
        left_ps = 0
        right_ps = 0
        while (itt_pulse < self.max_time_subpulses):
            max_index = -1
            max_val = 0
            for i, val in enumerate(arr):
                if val > max_val:
                    max_index = i
                    max_val = val
            if (max_val < self.height_prediction_time * self.cutoff):
                #print("break cutoff")
                break
            if index_prev == max_index:
                #print("break repetition: num pulses: " + str(len(peaks)))
                break
            if max_index == -1:
                #print("break no peak found: num pulses: " + str(len(peaks)))
                break
            index_prev = max_index
            
            dif = 0 #last_point - current_point
            dif_prev = 0 #before_last_point - last_point
            left_ps = -1
            itt = max_index
            prev_point = -1
            pred = self.height_prediction_time*np.square(np.exp(-0.5 * np.square((time_arr[max_index])/self.sigma_t)))
            while (max_index-left_ps > 1 and dif >= 0):
                dif_prev = dif
                itt -= 1
                dif = arr[itt+1] - arr[itt]
                left_ps += 1
                
            
            #go right
            dif = 0 #last_point - current_point
            dif_prev = 0 #before_last_point - last_point
            right_ps = -1
            itt = max_index
            while (max_index+right_ps < len_arr - 2 and dif >= 0):
                dif_prev = dif
                itt += 1
                dif = arr[itt-1] - arr[itt]
                right_ps += 1
            
            if ((right_ps > 1 and left_ps > 1) or arr[max_index] > pred):
                try: 
                    AandB, covariance = curve_fit(Gauss, np.linspace(-left_ps * self.time_spacing, right_ps * self.time_spacing, right_ps + left_ps + 1), arr[max_index - left_ps:max_index + right_ps + 1], maxfev = 1000)
                    peaks[itt_pulse,0] = time_arr[max_index]
                    peaks[itt_pulse,1] = AandB[0]
                    peaks[itt_pulse,2] = AandB[1]
                    arr = arr - AandB[0] * np.exp(-AandB[1]*(time_arr-time_arr[max_index])**2)
                    arr[arr < 0] = 0
                    itt_pulse+=1
                except:
                    #print("early break, fitting error. num_pulses: " + str(len(peaks)))
                    break
        return peaks