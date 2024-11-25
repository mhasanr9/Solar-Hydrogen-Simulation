#import classes and modules
import pandas as pd 
import matplotlib.pyplot as plt
import pvlib
import os
from datetime import timedelta

# pvgis_data, meta, inputs = pvlib.iotools.get_pvgis_hourly(latitude=22.900334691224337, longitude=89.50176306659651, 
#                                start=2020, end=2020, raddatabase="PVGIS-ERA5", 
#                                components=True, surface_tilt=45, surface_azimuth=0, 
#                                outputformat='json', usehorizon=True, userhorizon=None, 
#                                pvcalculation=False, peakpower=None, pvtechchoice='crystSi', 
#                                mountingplace='free', loss=0, trackingtype=0, 
#                                optimal_surface_tilt=False, optimalangles=False, 
#                                url='https://re.jrc.ec.europa.eu/api/v5_2/', map_variables=True, timeout=30)

# print(pvgis_data)

tmy_data, months_selected, inputs, metadata = pvlib.iotools.get_pvgis_tmy(latitude=23.72673681445547, 
                                                    longitude=90.39263652432568, outputformat='json', 
                                       usehorizon=True, userhorizon=None, startyear=2005, endyear=2016, 
                                       map_variables=True, url='https://re.jrc.ec.europa.eu/api/v5_2/', timeout=30)

tmy_data.index = tmy_data.index.tz_convert('Asia/Dhaka')

tmy_data.index = tmy_data.index.map(lambda x: x.replace(year=2024))
tmy_data.to_csv('my_tmy_dhaka.csv', index=True)