#import classes and modules
import pandas as pd 
import matplotlib.pyplot as plt
import pvlib
import os

from datetime import timedelta
from pvlib.modelchain import ModelChain
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS


#Get PV module and Inverter from database
sandia_modules_db = pvlib.pvsystem.retrieve_sam('SandiaMod')
inverter_db = pvlib.pvsystem.retrieve_sam('CECInverter')

# #CSV Output
# sandia_modules_db.to_csv('module.csv', index=True)
# inverter_db.to_csv('inverter.csv', index=True)


#select module and inverter
module = sandia_modules_db['Canadian_Solar_CS6X_300M__2013_']
inverter = inverter_db['ABB__TRIO_20_0_TL_OUTD_S1B_US_480_A__480V_']

#Create instances 
my_location = Location(latitude=22.900334691224337, longitude=89.50176306659651, tz='Asia/Dhaka', 
                       altitude=9, name='KUET')
temp_param = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

my_system = PVSystem(surface_tilt=45, surface_azimuth=180, module_parameters=module, 
                     inverter_parameters=inverter, temperature_model_parameters=temp_param,
                     modules_per_string=15, strings_per_inverter=4)

#modelchain execution
my_mc = ModelChain(my_system, my_location)

############################################################
#download TMY data, change time zone and replace year
# tmy_data, months_selected, inputs, metadata = pvlib.iotools.get_pvgis_tmy(latitude=22.900334691224337, 
#                                                     longitude=89.50176306659651, outputformat='json', 
#                                        usehorizon=True, userhorizon=None, startyear=2005, endyear=2016, 
#                                        map_variables=True, url='https://re.jrc.ec.europa.eu/api/v5_2/', timeout=30)

# tmy_data.index = tmy_data.index.tz_convert('Asia/Dhaka')

# tmy_data.index = tmy_data.index.map(lambda x: x.replace(year=2024))
##############################################################

###############################
#Read saved TMY data from a CSV file
tmy = pd.read_csv('my_tmy.csv', index_col=0)
tmy.index = pd.to_datetime(tmy.index)
###############################

#running the model
my_mc.run_model(tmy)

result_dc = my_mc.results.dc

result= result_dc['p_mp'].resample("ME").sum()/1000
result.index = pd.to_datetime(result.index)
result.index = result.index.strftime('%B')

# result_df = result.to_frame()
# result_df.index = pd.to_datetime(result_df.index)
# #result_df.index = result_df.index.month
# result_df.index = result_df.index.strftime('%B')
# result_df.index.rename('Months', inplace=True)
# result_df.columns = ['Power']  # Rename the column
# result_df.plot(kind='bar')
# plt.xlabel('Months')
# plt.ylabel('Power (Wh)')
# #plt.tight_layout()
# plt.show()
print(result)
