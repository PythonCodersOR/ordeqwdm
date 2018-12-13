import os, pickle, datetime
import pandas as pd

from pyhspf import WDMUtil

str_precip = 'siletz_HSPF_precip.csv'
str_pet = 'siletz_HSPF_PET.csv'
str_wdm = 'bigelk_in.wdm'
str_wdm_new = 'siletz.wdm'

# need to set variable for HSPF message file. WDMItil uses this file
messagepath = os.path.abspath(os.path.curdir) + '\\hspfmsg.wdm'

df_prec = pd.read_csv(str_precip)
df_prec.head()

df_pet = pd.read_csv(str_pet)
df_pet.head()

# create an instance of WDMUtil class
wdm = WDMUtil(verbose = True, messagepath = 'hspfmsg.wdm')

# create a new wdm file
wdm.open(str_wdm_new, 'w')


# take from pyHSPF test01.py example
#
# the first few test runs write data to the WDM files, but they assume the 
# datasets already exist so we need to create them. have a look at the test
# UCI files if you are curious

attributes = {'TCODE ': 4, 
              'TSSTEP': 1, 
              'TSTYPE': 'WTMP', 
              'TSFORM': 3,
              }

# what these attributes mean:
#
# the time series type for the first dataset is "WTMP" (water temperature)
# the time code is 4 (the units of the time step for the dataset are days)
# the time step is 1 (1 "unit" of the time step = 1 day)
# the time step form is 3 (the water temperature is a "state" variable 
# that does not depend on time step)
#
# the time step form is perhaps most difficult to understand. different 
# variables have different forms when they are discretized into time steps.
# the flow for a time step could represent the average value across the
# step, the value at the beginning or end, the average value, or the total
# value (this is perhaps most important)--thus for example if I say "the flow
# between 2 and 3 pm was 10 m3 is different than saying the flow at 3 pm was
# 10 m3 per hour. Given that context, HSPF groups all variables into one of
# three categories (the examples reference heat transfer concepts):

# TSFORM = 1 -- The mean value of a state variable (such as temperature)
# TSFORM = 2 -- The total flux across a time step (such as heat flux energy)
# TSFORM = 3 -- The value at the end of the time step (such as temperature)




# for precip and pet, the TSFORM  value would be 2 becuase it would be the total precip that occured over the time-step
attributes['TSFORM'] = 3
attributes['TSTYPE'] = 'PREC'
wdm.create_dataset(str_wdm_new, 11, attributes)
attributes['TSTYPE'] = 'PET'
wdm.create_dataset(str_wdm_new, 12, attributes)

# add precip data for sub-basin 1
start_date = df_prec['DATE'][0]
date_start = datetime.datetime(int(start_date[5:9]), int(start_date[0:2]), int(start_date[3:4]))
prec_add = [float(x) for x in list(df_prec.iloc[:,1])]
wdm.add_data(str_wdm_new, 11, prec_add, date_start)

# add pet data for sub-basin 1
start_date = df_prec['DATE'][0]
date_start = datetime.datetime(int(start_date[5:9]), int(start_date[0:2]), int(start_date[3:4]))
pet_add = [float(x) for x in list(df_pet.iloc[:,1])]
wdm.add_data(str_wdm_new, 12, pet_add, date_start)

# close wdm file
wdm.close(str_wdm_new)