import numpy as np
from lib.partial_harvest import PartialHarvest as ph
from lib.helpers import biomass_harvest, price_function

class SubCost:
    def __init__(self, t, final_doc) -> None:
        """
        t: time t-th
        """
        self.t = t
        self.final_doc = final_doc
    
    def energy_cost(self, e, d=820, max=24):
        """
        e: energy consumtion (HP)
        d: harga listrik per HP
        max: max hours. Default 24.
        """
        return e*d*max


    def probiotic_cost(self, p):
        """
        p: daily probiotics
        final_doc: doc for final harvest
        """
        return p if self.t < self.final_doc else 0


    def other_cost(self, o):
        """
        t: time t-th
        o: other daily cost
        final_doc: doc for final harvest
        """
        return o if self.t < self.final_doc else 0

def costing(t0, area, wn, w0, alpha, n0, m, partial1, partial2, partial3, 
        docpartial1, docpartial2, docpartial3, docfinal, e, p, o, bonus, 
        h, pl, sr, r, fc, formula):

    energy = []
    probiotics = []
    others = []
    feeds = []
    harvest = []
    biomassa = []
    bonusses = []
    realized_revenue = []

    f = price_function("data/fixed_price.csv")

    times = range(0, docfinal+1)
    for t in times:
        sub_cost = SubCost(t, docfinal)
        energy.append(sub_cost.energy_cost(e))
        probiotics.append(sub_cost.probiotic_cost(p))
        others.append(sub_cost.other_cost(o))

        obj = ph(t0, t, area, wn, w0, alpha, n0, m, partial1, partial2, partial3, 
            docpartial1, docpartial2, docpartial3, docfinal)

        hv = obj.harvest_cost(h, pl, sr)
        harvest.append(hv[0])
        feeds.append(obj.feed_cost(fc, formula, r))

        biomassa.append(obj.biomassa()["kg"])
        bonusses.append(0)

        realized_revenue.append(obj.realized_revenue(f))

    # total biomassa which harvested
    total = sum(biomass_harvest(biomassa, docpartial1, docpartial2, docpartial3))

    bonusses[docfinal] = bonus * total

    data = np.array([energy, probiotics, others, harvest, feeds, bonusses])
    aggregate = data.sum(axis=1)/data.sum() 

    plharvested = hv[1]
    cost_perkg = data.sum()/total
    cost_perpl = data.sum()/sum(plharvested)

    total_revenue = sum(realized_revenue)
    profit = total_revenue - data.sum()
    revenue_perpl = total_revenue/total
    return_opex = profit/data.sum()
    margin = profit/total_revenue


    result = {
        "index": ["energy_cost", "probiotics_cost", "others_cost",
            "harvest_cost", "feed_cost", "bonusses"],
        "data": data.transpose().tolist(),
        "aggregate": aggregate.tolist(),
        "matrix": {
            "costPerKg": cost_perkg,
            "costPerPl": cost_perpl,
            "totalCost": data.sum(),
            "totalRevenue": total_revenue,
            "profit": profit,
            "revenuePerPl": revenue_perpl,
            "returnOnOpex": return_opex,
            "margin": margin
        }
    }
    return result