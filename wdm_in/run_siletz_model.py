import os, time, datetime, pickle
from pyhspf import HSPFModel, WDMUtil

model = 'siletz_river'
if not os.path.isfile(model):
    print('missing model file; re-run build_siletz_model.py')
    raise

with open(model, 'rb') as f: hspfmodel = pickle.load(f)

targets = ['reach_outvolume', # outflow volume for each reach
           'evaporation',     # simulated ET for each operation
           'rain',            #
           'runoff',          # runoff components (SURO, IFWO, AGWO)
           ]

hspfmodel.messagepath = 'C:/siletz/hspfmsg.wdm'

hspfmodel.build_wdminfile()

# Set (or get) start and end dates
start = datetime.datetime(2012, 1, 1)
end = datetime.datetime(2013, 1, 1)

hspfmodel.build_uci(targets, start, end, hydrology = True, verbose = True)

hspfmodel.run(verbose = True)



