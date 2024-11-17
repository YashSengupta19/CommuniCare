import math

class OneEuroFilter:
    def __init__(self, mincutoff=1.0, beta=0.0, dcutoff=1.0):
        self.min_cutoff = mincutoff
        self.beta = beta
        self.d_cutoff = dcutoff
        self.x_prev = None
        self.dx_prev = None
        self.t_prev = None

    def alpha(self, cutoff, dt):
        tau = 1.0 / (2.0 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)

    def apply_filter(self, x, t):
        if self.t_prev is None:
            self.x_prev = x
            self.dx_prev = 0
            self.t_prev = t
            return x
        
        dt = t - self.t_prev
        dx = (x - self.x_prev) / dt if dt > 0 else 0.0
        dx_hat = self.dx_prev + self.alpha(self.d_cutoff, dt) * (dx - self.dx_prev)
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        x_hat = self.x_prev + self.alpha(cutoff, dt) * (x - self.x_prev)
        
        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t
        
        return x_hat
