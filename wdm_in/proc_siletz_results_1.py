import pandas as pd
import csv
from matplotlib import pyplot as plt
from pyhspf import HSPFModel, WDMUtil, Postprocessor

messagepath = 'hspfmsg.wdm'

wdm = WDMUtil(verbose = True, messagepath = messagepath)

# EXTRACT MODELED FLOWS FROM WDM OUTPUT FILE AND COMPARE TO 
wdmFile = 'siletz_river_out.wdm'

wdm.open(wdmFile, 'r')

dsns = wdm.get_datasets(wdmFile)
idconss = [wdm.get_attribute(wdmFile, n, 'IDCONS') for n in dsns]
staids  = [wdm.get_attribute(wdmFile, n, 'STAID ') for n in dsns]

volMod = wdm.get_data(wdmFile, 11)

wdm.close(wdmFile)

qMod = [q * 10**6 * 35.314666721 / (60 * 60) for q in volMod]

# Read flow data
flwData = pd.read_csv(os.path.abspath(os.path.curdir) + 
                      '\\siletz_HSPF_flw.csv')

qGge = flwData['Q_slz'].values.tolist()

# post-process
start = datetime.datetime(2004, 1, 1)
end = datetime.datetime(2018, 4, 1)

dttm = [start + t * datetime.timedelta(hours = 1)
        for t in range(int((end - start).total_seconds() / 3600))]             

procDts = start, end

ggID = 11

p = Postprocessor(hspfmodel, procDts)

p.plot_hydrograph(tstep = 'daily')






plt.plot(dttm, qMod, label = 'Model')

plt.plot(dttm, qGge, label = 'Gaged')

plt.xlabel("Date-Time")

plt.ylabel("Flow (cfs)")

plt.yscale('log')

plt.legend()

plt.show()




