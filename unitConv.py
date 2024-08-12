#unitConv
import numpy as np
class unitConverter:
    def au2ev(self, val):
        return val * 27.2116
    def ev2au(self, val):
        return val * 0.03674903
    def au2meter(self, val): 
        return val * 5.2917721067e-11
    def meter2au(self, val):
        return val * 18897260000
    def au2second(self, val):
        return val * 2.419e-17
    def second2au(self, val):
        return val * 4.133940e+16
    def au2fs(self, val):
        return val * 2.419e-2
    def fs2au(self, val):
        return val * 4.133940e+1