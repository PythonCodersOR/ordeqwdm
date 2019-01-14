# CREATE THE SILETZ HSPF MODEL

import os, csv, pickle, datetime
import pandas as pd
import shapefile
from pyhspf import Subbasin, Watershed, HSPFModel, WDMUtil
from array import *

start = datetime.datetime(2004, 1, 1)
end = datetime.datetime(2018, 4, 1)
tstep = 60
lc_codes = ['FORLO', 'FORHI', 'DEVLO', 'DEVHI', 'GRSLO',
            'GRSHI', 'CULLO', 'CULHI', 'IMPRV']

parentDir = r'//deqhq1/tmdl/TMDL_WR/MidCoast/Models/Dissolved Oxygen/Middle_Siletz_River_1710020405'
dataDir = '/001_data'
metDir = '/met_data'
qDir = '/flow_data'
shapeDir = '/004_gis/001_data/001_shape/hspf'
landCoverDir = '/nlcd_2011'
wdmFile = os.path.abspath(os.path.curdir) + '\\siletz_river_in.wdm'
mssgpath = os.path.abspath(os.path.curdir) + '\\hspfmsg.wdm'

# READ IN LAND COVER DATA
with open(parentDir + dataDir + landCoverDir + '/' + 
          'siletz_HRU_summary_ha.csv') as hruFile:
    
    readTables = csv.reader(hruFile, delimiter = ',')
    
    hru_df = []
    
    for hruRow in readTables:

        hru_df.append(hruRow)

# Convert the items in each row-wise list to float
lists = 0

for i in hru_df:

    hru_df[lists] = [float(hru) for hru in hru_df[lists]]

    lists += 1

# fraction of developed land that is impervious (assume all impervious land)
ifraction = 1.

# Read and input the FTables
fTabFil = parentDir + dataDir + '/' + 'ftables.csv'

fTables = read_ftables(fTabFil)

# READ IN BASIN, REACH AND OUTLET SHAPEFILES
basinShp = shapefile.Reader(parentDir + shapeDir +
                            '/siletz_catchments_HSPF.shp')

reachShp = shapefile.Reader(parentDir + shapeDir +
                            '/siletz_river_reaches_HSPF.shp')

basinRecords = basinShp.records()

reachRecords = reachShp.records()

# Send the import data to the pre-build processors
subbasins = create_subbasins(basinRecords,
                             reachRecords,
                             2011,
                             lc_codes,
                             hru_df,
                             fTables)

flow_network = create_flownetwork(basinRecords)

# CREATE HSPF MODEL
watershedSiletz = Watershed("Siletz River", subbasins)

watershedSiletz.add_mass_linkage(flow_network)

for basin in range(0, len(basinRecords)):
    
    if basinRecords[basin][6] == 0:
        
        watershedSiletz.add_outlet(str(basin + 1)) # Assumes basin numbers     
        
    x = 1 # Don't need this but the loop wants to include 'hspfmodel...'

# Build the model
hspfmodel = HSPFModel(units = 'Metric')

filename = 'siletz_river'

outfile = filename + '.out'

wdmoutfile = filename + '_out.wdm'

hspfmodel.build_from_watershed(watershedSiletz,
                               'siletz_river',
                               ifraction = ifraction,
                               tstep = tstep,
                               print_file = outfile)

watershedSiletz.plot_mass_flow(output = 'siletz_basin_network')

# ADD TIME SERIES DATA: PRECIP, PET, and FLOW TO THE WDM FILE
pcpData = pd.read_csv(os.path.abspath(os.path.curdir) + 
                      '\\siletz_HSPF_precip.csv')

petData = pd.read_csv(os.path.abspath(os.path.curdir) + 
                      '\\siletz_HSPF_pet.csv')
    
flwData = pd.read_csv(os.path.abspath(os.path.curdir) + 
                      '\\siletz_HSPF_flw.csv')

ts_to_wdmFile(wdmFile = wdmFile,
              pcpData = pcpData,
              petData = petData,
              flwData = flwData)

# See if you can read the data from the WDM file
wdm = WDMUtil(verbose = True, messagepath = mssgpath)

# ADD BASIN TIMESERIES FROM THE WDM TO HSPFMODEL
# open the wdm for read access
wdm.open(wdmFile, 'r')

start, end = wdm.get_dates(wdmFile, 101)

x = 1

# Add specific basin met data
for basin in range(0, len(basinRecords)):

    # The DSNs are known from the exp file so just use those this time
    prcp = wdm.get_data(wdmFile, 100 + x)

    evap = wdm.get_data(wdmFile, 200 + x)

    # Add and assign timeseries data
    hspfmodel.add_timeseries('precipitation', ('prcp_' + str(x)), start, prcp,
                             tstep = tstep)

    hspfmodel.add_timeseries('evaporation', ('evap_' + str(x)), start, evap,
                             tstep = tstep)
    
    # Assign to specific basin
    hspfmodel.assign_subbasin_timeseries('precipitation', str(basin + 1),
                                         ('prcp_' + str(x)))

    hspfmodel.assign_subbasin_timeseries('evaporation', str(basin + 1),
                                         ('evap_' + str(x)))

    x += 1

# Add flow data to the gaged basin
flow = wdm.get_data(wdmFile, 301)

hspfmodel.add_timeseries('flowgage', 'flow', start, flow,
                         tstep = tstep)

hspfmodel.assign_subbasin_timeseries('flowgage', '11', 'flow')

wdm.close(wdmFile)

# COMPLETE AND EXECUTE MODEL
hspfmodel.add_hydrology()

with open('siletz_river', 'wb') as f: pickle.dump(hspfmodel, f)

print('\nsuccessfully created new model "siletz_river."\n')

