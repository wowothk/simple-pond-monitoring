from lib.helpers import body_weight, heaviside_step, feed_formula3
import numpy as np

# base function per m2 in t 

class PartialHarvest:
    def __init__(self, t0: int, t: int, wn: float, w0: float, alpha: float, n0: int, sr: float, m: float, 
        ph: list, doc: list, final_doc:int = 120) -> None:
        """
        t0: initial time
        t: current time
        wn: shrimp max weight 
        w0:  shrimp stocking weight g
        alpha: shrimp growth rate
        n0: shrimp stocking density
        sr: survival rate
        ph: partial harvest. list of the amount each partial harvest
        doc: day old culture. list of the partial harvest time
        """
        self.t0 = t0
        self.t = t
        self.wn = wn
        self.w0 = w0
        self.alpha = alpha
        self.n0 = n0
        self.sr = sr
        self.m = m
        self.ph = ph
        self.doc = doc
        self.final_doc = final_doc

    def wt(self):
        return body_weight(self.wn, self.w0, self.alpha, self.t0, self.t)

    # def SR(self):
    #     m = np.log(self.sr)/self.t if self.t != 0 else 0
    #     return m 

    def population(self):
        partial_harvest = []
        for i, j in enumerate(self.doc):
            partial_harvest.append(self.ph[i] * heaviside_step(self.t - j))

        if self.t+1 >= self.final_doc:           
            partial_harvest.append((self.sr - sum(self.ph)) * heaviside_step(self.t - j))
        
        result = self.n0 * (np.exp(-self.m * self.t) - sum(partial_harvest))
        return result


    def biomassa(self):
        # biomassa in gram
        result = self.wt() * self.population()
        return result
    
    def biomassa_constant(self):
        return self.wt() * self.n0

    #########################################
    # revenue
    #########################################

    def realized_revenue(self, f):
        if self.t in self.doc:
            return self.biomassa()/1000 * f(1000/self.wt()) # biomassa dikalikan dengan harga per size  
        else:
            return 0

    def potential_revenue(self, f):
        pr = self.biomassa_constant()/1000 * f(1000/self.wt())
        return 0 if pr < 0 else pr

    #########################################
    # costing
    #########################################
    def feed_cost(self, fc, formula_type=2, r=None):
        """
        r: feeding rate
        fc: feed cost per kg
        formula_type: formula_type for feeding cost calculation. There are 1 and 2.
        """
        if formula_type == 1:
            return self.biomassa()/1000 * r * fc
        else:
            formula3 = feed_formula3("data/data-feeding-formula-3.csv", ",")
            if self.t < self.doc[-1]:
                return formula3[self.t] / 1000 * (1+0.2) * fc
            else:
                return 0

    def harvested_population(self):
        # dailyCulture = self.population()
        partial = []
        for i in self.doc:
            if self.t+1 == i:
                nti = PartialHarvest(self.t0, self.t+1, self.wn, self.w0, self.alpha, self.n0, self.sr, self.m, self.ph, self.doc, self.final_doc).population()
                nti_1 = PartialHarvest(self.t0, self.t, self.wn, self.w0, self.alpha, self.n0, self.sr, self.m, self.ph, self.doc, self.final_doc).population()
                partial.append(nti_1-nti)
            else:
                partial.append(0)

        return sum(partial)

    def biomass_harvest(self):
        return self.wt() * self.harvested_population()

    def harvest_cost(self, h):
        """
        h: harvest cost per kg
        """
        return self.harvested_population() * h

    def fcr(self, formula_type=2, r=None):
        feed = self.feed_cost(1, formula_type, r) # we use fc = 1 to get the amount of feed
        biomass = self.biomassa()/1000 
        return 0 if np.isnan(feed/biomass) else feed/biomass

    def adg(self):
        """
        average daily growth
        """
        result = self.wt()/self.t if self.t !=0 else 0
        return result