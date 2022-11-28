import random
import matplotlib.pyplot as plt
import numpy as np
import scipy as sc



# Ideal Gas Properties Table
gas_prop_table_csv = open('ideal_gas_prop.csv')
gas_prop_table_array = np.loadtxt(gas_prop_table_csv, delimiter = ' ')

t = 0 #temperature is the first column, enthalpy is second, pr is third
h = 1
p = 2

def table_interp(val1, col_from, col_to):

    table_from = gas_prop_table_array[:, col_from]
    table_to = gas_prop_table_array[:, col_to]
    
    index = np.argmax(table_from >= val1)
    ratio = (val1 - table_from[index - 1]) / (table_from[index] - table_from[index - 1])
    val2 = ratio * (table_to[index] - table_to[index - 1]) + table_to[index - 1]

    return val2

# Pressure: kPa (relative pressure: no units)
# Temperature: K
# Power: kW
# Calorific Value: kJ/kg

def calc():

    # Input variables
    maxFuelFlow = 390 #ml/min
    Tmax = 100 # Newtons from max fuel flow
    v_in = 0 #km/hr, velocity in
    v_out = 1560 #km/hr
    exitExhaustTempMaxLB = 480 #deg 
    exitExhaustTempMaxUB = 720 #deg 
    pressureRatio_compressor = 2.9
    eff_compressor = 0.8 #ESTIMATE as of 11.28.22
    m_air = 0.23 #kg/s, air mass flow rate

    # Atmospheric condition inputs
    t_atm = 300 #k, atmospheric temperature
    p_atm = 101.3 #kPa, atmospheric pressure
    d_atm = 1.225 #kg/m^3, atmospheric density

    # Fuel inputs
    d_kerosene = 0.821 #kg/m^3
    LHV_kerosene = 43.0 #MJ/kg

    # Combusion Efficiency
    # eff_combustion = 0.9
    eff_combustion = np.random.normal(0.7, 0.1)

    # Atmosphere, S0
    # temp and pressure at s1 (station 1), ideal gas assumption
    t_0 = t_atm
    p_0 = p_atm
    h_0 = table_interp(t_0, t, h)

    # Diffuser, S1
    # Assume no engine diffuser

    # Compressor Inlet, S2
    # Conditions t,p,h are the same here as S0

    # Post compressor, S3
    # Isentropic Assumption
    p_3 = pressureRatio_compressor * p_0
    p_3r = pressureRatio_compressor * table_interp(t_0, t, p)
    t_3 = table_interp(p_3r, p, t)
    h_3 = table_interp(t_3, t, h)
    w_3 = m_air * (h_3 - h_0)
    # Non - isentropic
    h_3a = h_0 + (h_3 - h_0)/eff_compressor
    

    # Post combustor, S4
    # Energy provided by fuel (kJ)
    m_fuel = d_kerosene * maxFuelFlow / 1000 / 60 #kg/s, fuel mass flow rate
    q_fuel_ideal = m_fuel * LHV_kerosene * 1000 # kJ
    q_fuel_actual = eff_combustion * q_fuel_ideal #kJ
    # No Pressure Loss Assumption
    h_4 = (q_fuel_actual / m_air) + h_3
    t_4 = table_interp(h_4, h, t)
    p_4r = table_interp(t_4, t, p)

    # Post turbine, S5 
    # Isentropic assumption, pressure drop to p_0
    p_5r = p_4r / pressureRatio_compressor
    t_5 = table_interp(p_5r, p, t)
    h_5 = table_interp(t_5, t, h)
    w_5 = m_air * (h_4 - h_5)

    # Thrust
    f_thrust = m_air * ((v_out - v_in) * 1000 / 3600)

    # Output
    data = np.array([t_0, h_0, p_0, t_3, h_3, p_3, p_3r, w_3, q_fuel_actual, t_4, h_4, p_4r, t_5, h_5, p_5r, w_5, f_thrust])
    return data

# Monte Carlo Simulations

# Inputs
num_runs = 10000

# Tracking
t3_data = np.zeros(shape = (num_runs))
tracker_run_data = np.zeros(shape = (num_runs, len(calc())))
data_row, data_col = tracker_run_data.shape

# Runs
for i in range(num_runs):
    data = calc()
    tracker_run_data[i] = data

# Averages
output_mean = np.zeros(shape = (data_col))
#a = tracker_run_data[:, 9]

for i in range(data_col):
    a = tracker_run_data[:, i]
    output_mean[i] = np.mean(a)

# Plot output

print(output_mean)

plt.xlim(0, num_runs)
plt.plot(t3_data)
plt.show()

'''
 isentropic efficiency of compressor and turbine
 Model the pressure drop through the engine appropriately
 pressure drop -> more shaft power
 Checking Compressor needs is less than what the turbine provides (Power differential condition)
 What is this Exhaust gas power output (kW)	21.7
 check missing specs in the calculation
 compressor combuster turbine and nozzle (missing) 
'''


'''
git fetch
git reset --hard HEAD
git merge origin/main

commit 
git add .
git commit -m "<PUT MESSAGE HERE>"
git push 

'''