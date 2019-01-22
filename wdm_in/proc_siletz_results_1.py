import pandas as pd
import csv, os, datetime, numpy
from matplotlib import pyplot as plt
from pyhspf import HSPFModel, WDMUtil, Postprocessor

messagepath = 'hspfmsg.wdm'

wdm = WDMUtil(verbose = True, messagepath = messagepath)

# EXTRACT MODELED FLOWS FROM WDM OUTPUT FILE AND COMPARE TO 
wdmFile = 'siletz_river_out.wdm'

wdm.open(wdmFile, 'r')

dsns = wdm.get_datasets(wdmFile)
idcons = [wdm.get_attribute(wdmFile, n, 'IDCONS') for n in dsns]
staids = [wdm.get_attribute(wdmFile, n, 'STAID ') for n in dsns]

pars = [dsns, idcons, staids]

dsnBas1 = [dsns for dsns, idcons, staid in zip(dsns, idconss, staids)
           if staid == '1']  # These are the dsns for all Basin 1 outputs 

indBas1 = [dsn - 1 for dsn in dsnBas1] # These are element indeces for Basin 1 dsns

start = datetime.datetime(2012, 1, 1)
end = datetime.datetime(2013, 1, 1)

dttm = [start + t * datetime.timedelta(hours = 1)
        for t in range(int((end - start).total_seconds() / 3600))]

datOut = [dttm]

datNms = ['Date']

for i in dsnBas1:
   
    tmpNme = idcons[i - 1] + '_' + staids[i - 1]
    
    datNms.append(tmpNme)
    
    tmpDat = wdm.get_data(wdmFile, i)

    datOut.append(tmpDat)

volMod = wdm.get_data(wdmFile, 11)

wdm.close(wdmFile)

datDFOut = pd.DataFrame.from_items(zip(datNms, datOut))

datDFOut.to_csv('basin_1_output.csv', index = False)

qMod = [q * 10**4 * 35.314666721 / (60 * 60) for q in volMod]

# Read flow data
flwData = pd.read_csv(os.path.abspath(os.path.curdir) + 
                      '\\siletz_HSPF_flw.csv')



qGge = flwData['Q_slz'].values.tolist()

# post-process

modelVolume = pd.DataFrame({'date': dttm, 'volm': volMod}, index = index)
modelVolume.to_csv('test.csv', index = False)
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