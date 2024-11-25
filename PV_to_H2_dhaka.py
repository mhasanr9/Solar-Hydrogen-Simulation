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
                       altitude=32, name='BUET')
temp_param = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

my_system = PVSystem(surface_tilt=45, surface_azimuth=180, module_parameters=module, 
                     inverter_parameters=inverter, temperature_model_parameters=temp_param,
                     modules_per_string=15, strings_per_inverter=4)

#modelchain execution
my_mc = ModelChain(my_system, my_location)

############################################################
#download tmy_dhk data, change time zone and replace year
# tmy_dhk_data, months_selected, inputs, metadata = pvlib.iotools.get_pvgis_tmy_dhk(latitude=22.900334691224337, 
#                                                     longitude=89.50176306659651, outputformat='json', 
#                                        usehorizon=True, userhorizon=None, startyear=2005, endyear=2016, 
#                                        map_variables=True, url='https://re.jrc.ec.europa.eu/api/v5_2/', timeout=30)

# tmy_dhk_data.index = tmy_dhk_data.index.tz_convert('Asia/Dhaka')

# tmy_dhk_data.index = tmy_dhk_data.index.map(lambda x: x.replace(year=2024))
##############################################################

###############################
#Read saved tmy_dhk data from a CSV file
tmy_dhk = pd.read_csv('my_tmy_dhaka.csv', index_col=0)
tmy_dhk.index = pd.to_datetime(tmy_dhk.index)
###############################


#running the model
my_mc.run_model(tmy_dhk)

result_dc = my_mc.results.dc

result_dhk= result_dc['p_mp'].resample("ME").sum()/1000
result_dhk.index = pd.to_datetime(result_dhk.index)
result_dhk.index = result_dhk.index.strftime('%B')
months = result_dhk.index

result_dhk_y= result_dc['p_mp'].resample("YE").sum()/1000
print(result_dhk_y)
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

# #dhaka vs khulna DC Power
# from PV_to_H2 import result
# plt.plot(months, result, label='Khulna', linestyle='--')
# plt.plot(months, result_dhk, label='Dhaka', linestyle=':')
# # plt.plot(months, rad_dhk, label='Dhaka')
# # plt.plot(months, rad_khl, label='Khulna')
# plt.xlabel('Months')
# plt.ylabel('DC Power (KWh)')
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.legend()
# plt.show()

#hydrogen Production

#dc-dc buck converter
eta_bc = 0.95
rated_voltage=125
out_c = result_dc["p_mp"]*eta_bc/rated_voltage

#electrolyze subsystem

N_c =50
eta_f=0.9
F=96485
q_h2 = ((N_c*eta_f*out_c)/(2*F))*3600 #production in an hour
#print(q_h2.resample("ME").sum())

# hydrogen production calculations
monthly_dhk = q_h2.resample("ME").sum()
monthly_dhk.index = pd.to_datetime(monthly_dhk.index)
monthly_dhk.index = monthly_dhk.index.strftime('%B')
yearly_dhaka = q_h2.resample("YE").sum()
# print(yearly_dhaka)

# #import Khuna's data
# from Test2 import monthly_q 
# plt.bar(months, monthly_q,width=0.4, label='Khulna', align='center')
# plt.bar(months, monthly_dhk,width=0.4, label='Dhaka', align='edge')
# plt.xlabel('Months')
# plt.ylabel('Hydrogen Production (mol)')
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.legend()
# plt.show()


