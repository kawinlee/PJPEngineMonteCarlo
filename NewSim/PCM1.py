import random
import matplotlib.pyplot as plt
import numpy as np
import scipy as sc
import math

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
    maxFuelFlow = 390               #ml/min, jetcat data
    v_in = 0                        #km/hr, static test condition
    v_out = 1560                    #km/hr, jetcat data
    pressureRatio_compressor = 2.9  #unitless, jetcat data
    pressureRatio_combustor = 0.97  #unitless, okstate data
    #pressureRatio_turbine =        #unitless, okstate data
    eff_compressor = 0.675          #unitless, GTBA Average
    eff_turbine = 0.725             #unitless, GTBA Average
    eff_combustion = 0.925          #unitless, GTBA Average
    m_air = 0.23                    #kg/s, jetcat data
    EGT_lower = 753                 #K, jetcat data
    EGT_upper = 993                 #K, jetcat data
    works = False

    # Atmospheric condition inputs
    t_atm = 300                     #k, atmospheric temperature
    p_atm = 101.3                   #kPa, atmospheric pressure
    d_atm = 1.225                   #kg/m^3, atmospheric density

    # Fuel inputs
    d_kerosene = 821                #kg/m^3, internet
    LHV_kerosene = 43.0 * 1000      #kJ/kg, internet
    m_fuel = d_kerosene * (maxFuelFlow / 1000 / 60)   #kg/s, fuel mass flow rate
    m_tot = m_air + m_fuel          # total mass flow

    # Combusion Efficiency
    

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
    pr_3 = (p_3 / p_0) * table_interp(t_0, t, p)
    t_3i = table_interp(pr_3, p, t)
    h_3i = table_interp(t_3i, t, h)
    w_ci = m_air * (h_3i - h_0)
    wca = w_ci / eff_compressor
    h3a = wca / m_air + h_0

    # Post combustor, S4
    # Energy provided by fuel (kJ) 
    q_fuel_ideal = m_fuel * LHV_kerosene # kJ
    q_fuel_actual = eff_combustion * q_fuel_ideal #kJ
    p_4 = p_3 * pressureRatio_combustor
    # ideal
    h_4i = (q_fuel_actual / m_tot) + h_3i
    t_4i = table_interp(h_4i, h, t)
    pr_4i = (p_4 / p_3) * table_interp(t_4i, t, p)
    # actual
    h_4a = (q_fuel_actual / m_tot) + h3a
    t_4a = table_interp(h_4a, h, t)
    pr_4a = table_interp(t_4a, t, p)
    #pr_4a = (p_4 / p_3) * table_interp(t_4a, t, p)
    # Post turbine, S5 
    # condition w_c = w_t
    h5a = h_4a - (wca / m_tot)
    pr5a = table_interp(h5a,h,p)
    pressureRatio_turbine = pr5a / pr_4a
    p5 = pressureRatio_turbine * p_4

    wta = m_tot * (h_4a - h5a)
    # Afterburner, S6 - S8
    # Not used

    # Nozzle exit plane, S9
    # Currently not calculating ideal case for simplicity
    # Perfect expansion assumption
    p_9 = p_0
    t_9a = 873
    h_9a = table_interp(t_9a,t,h)
    #v_9 = math.sqrt(2000 * (h5a - h_9a))
    # Thrust
    density = p_9 / (0.2871 * t_9a)
    #thrust = m_tot * (v_9 - (v_in * 1000 / 3600)) #in m/s, N
    # print("Actual Thrust:", f_actual)
    # print("Comp work:", w_ca)
    # print("Turb work:", wta)
    # print("EGT:", t_9a)
    
    # Output


    # if (t_9a < EGT_lower or t_9a > EGT_upper) and w_ca > wta:
    #     print("EGT out of bounds")
    #     print("Work balance does not close")
    # elif w_ca > wta:
    #     print("Work balance does not close")
    # elif t_9a < EGT_lower or t_9a > EGT_upper:
    #     print("EGT out of bounds")
    # else:
    #     works = True 
    #     print(works)        

    return 

print(calc())
# Monte Carlo Simulations

def monte_carlo(runs):
    total_data = np.zeros(shape = (runs, len(calc()))) #initialize tracking data
    data_row, data_col = total_data.shape

    #runs
    for i in range(runs): 
        data = calc()
        total_data[i] = data #assign run data to tracking data

    #average and standard deviation
    output_mean = np.zeros(shape = (data_col))
    output_sd = np.zeros(shape = (data_col))
    for i in range(data_col):
        output_mean[i] = np.mean(total_data[:, i])
        output_sd[i] = np.std(total_data[:, i])

    return total_data, output_mean, output_sd

# Plot Single Outputs from Monte Carlo Simulations
def single_output_data(mc, datapoint):
    total_data, output_mean, output_sd = mc
    data = total_data[:, datapoint]
    mean = output_mean[datapoint]

    plt.hist(data, bins = 20)
    plt.axvline(mean, color='k', linestyle='dashed', linewidth=1)

    return plt.show()



# Run Simulation

#mc = monte_carlo(runs)
#total_data, output_mean, output_sd = mc

#Get Data

#print(output_mean)
#print(output_sd)

#Produce Single Output Histogram
#single_output_data(mc, datapoint)



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
Before editing code, do git fetch
git fetch
git add .
git commit -m "<PUT MESSAGE HERE>"
git push 
'''