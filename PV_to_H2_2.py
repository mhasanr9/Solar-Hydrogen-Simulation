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

result_dc = my_mc.results.dc #.resample("ME").sum()
result_ac = my_mc.results.ac #.resample("ME").sum()

# # Plotting AC vs DC #########################################################
# fig, ax = plt.subplots(figsize=(10, 6))
# # Convert the dates to month names for the x-axis
# months = result_ac.index.strftime('%B')
# # Plot the bar charts
# ax.bar(months, result_ac/1000, width=0.4, label='AC Power', align='center')
# ax.bar(months, result_dc['p_mp']/1000, width=0.4, label='DC Power', align='edge')
# # Adding labels and title
# ax.set_xlabel('Month')
# ax.set_ylabel('Power (KWh)')
# #ax.set_title('Power Comparison between AC and DC')
# ax.legend()
# # Rotate the x-axis labels for better readability
# #plt.xticks(rotation=45)
# # Show plot
# plt.tight_layout()
# plt.show()
# ############################################################

# result_df = result.to_frame()
# result_df.index = pd.to_datetime(result_df.index)
# #result_df.index = result_df.index.month
# result_df.index = result_df.index.strftime('%B')
# result_df.index.rename('Months', inplace=True)
# result_df.columns = ['Power']  # Rename the column
# result_df.plot()
# plt.xlabel('Months')
# plt.ylabel('Power (Wh)')
# plt.tight_layout()
# plt.show()
# print(result)

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
monthly_q = q_h2.resample("ME").sum()
monthly_q.index = pd.to_datetime(monthly_q.index)
monthly_q.index = monthly_q.index.strftime('%B')

print(monthly_q)


# #plot per day hydrogen production
# monthly_q = q_h2.resample("D").sum()
# months = monthly_q.index.strftime('%B')
# days = monthly_q.index.dayofyear
# fig, ax = plt.subplots(figsize=(10, 6))
# ax.bar(days, monthly_q, align='edge')
# ax.set_xlabel('Day of the year')
# ax.set_ylabel('Produced Hydrogen Amount (mol)')
# ax.set_xlim(0, 365)
# plt.tight_layout()
# plt.show()

# #plot per day hydrogen storage in tank
# day_q = q_h2.resample("D").sum()
# mass = day_q*2/1000
# months = day_q.index.strftime('%B')
# days = day_q.index.dayofyear
# fig, ax = plt.subplots()
# ax.plot(days,mass)
# ax.set_xlabel('Day of the year')
# ax.set_ylabel('Mass (Kg)')
# ax.set_xlim(0, 365)
# plt.tight_layout()
# plt.show()

#old plots
# plt.xlabel('Months')
# plt.ylabel('Hydrogen (mol/s)')
# plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
# plt.tight_layout()
# plt.show()
