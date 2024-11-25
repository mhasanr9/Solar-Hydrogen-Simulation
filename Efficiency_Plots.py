import os
import pandas as pd
import matplotlib.pyplot as plt

import pvlib
from pvlib import iotools, location
from pvlib.irradiance import get_total_irradiance
from pvlib.pvarray import pvefficiency_adr
from datetime import timedelta
from pvlib.modelchain import ModelChain
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS

tmy = pd.read_csv('my_tmy.csv', index_col=0)
tmy.index = pd.to_datetime(tmy.index)

df = pd.DataFrame({'ghi': tmy['ghi'], 'dhi': tmy['dhi'], 'dni': tmy['dni'],
                   'temp_air': tmy['temp_air'],
                   'wind_speed': tmy['wind_speed'],
                   })

df.index = df.index - pd.Timedelta(minutes=30)

loc = Location(latitude=22.900334691224337, longitude=89.50176306659651, tz='Asia/Dhaka', 
                       altitude=9, name='KUET')
solpos = loc.get_solarposition(df.index)

TILT = 22.900334691224337
ORIENT = 180

total_irrad = get_total_irradiance(TILT, ORIENT,
                                   solpos.apparent_zenith, solpos.azimuth,
                                   df.dni, df.ghi, df.dhi)

df['poa_global'] = total_irrad.poa_global

df['temp_pv'] = pvlib.temperature.faiman(df.poa_global, df.temp_air,
                                         df.wind_speed)

# Borrow the ADR model parameters from the other example:

adr_params = {'k_a': 0.99924,
              'k_d': -5.49097,
              'tc_d': 0.01918,
              'k_rs': 0.06999,
              'k_rsh': 0.26144
              }

df['eta_rel'] = pvefficiency_adr(df['poa_global'], df['temp_pv'], **adr_params)

# Set the desired array size:
P_STC = 18000.   # (W)

# and the irradiance level needed to achieve this output:
G_STC = 1000.   # (W/m2)

df['p_mp'] = P_STC * df['eta_rel'] * (df['poa_global'] / G_STC)

plt.figure()
pc = plt.scatter(df['poa_global'], df['eta_rel']*100, c=df['temp_pv'], cmap='jet')
plt.colorbar(label='Temperature [C]', ax=plt.gca())
pc.set_alpha(0.25)
plt.grid(alpha=0.5)
plt.ylim(40)
plt.xlabel('Irradiance [W/m²]')
plt.ylabel('Relative efficiency [%]')
plt.show()

plt.figure()
pc = plt.scatter(df['poa_global'], df['p_mp'], c=df['temp_pv'], cmap='jet')
plt.colorbar(label='Temperature [C]', ax=plt.gca())
pc.set_alpha(0.25)
plt.grid(alpha=0.5)
plt.xlabel('Irradiance [W/m²]')
plt.ylabel('Array power [W]')
plt.show()