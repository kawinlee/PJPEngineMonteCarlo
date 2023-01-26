
import matplotlib.pyplot as plt
import numpy as np
import scipy as sc
import math
import random

# Load ideal gas properties table
gas_prop_csv = open('ideal_gas_prop.csv')
gas_prop_array = np.loadtxt(gas_prop_csv, delimiter = ' ')

# Match table column to data type
t = 0 # temperature
h = 1 # entropy
pr = 2 # relative pressure

# Table interpolation function
# Input value, input type and output type
def interp(val, type_in, type_out): 
    
    # Extract input and output type arrays from table
    table_in = gas_prop_array[:, type_in]
    table_out = gas_prop_array[:, type_out]

    # Get index of first value in input type array greater than input value
    i = np.argmax(table_in >= val) 

    # Map input value onto output type array
    ratio = (val - table_in[i - 1]) / (table_in[i] - table_in[i - 1])
    val_out = ratio * (table_out[i] - table_out[i - 1]) + table_out[i - 1] 
    return val_out

spec_heat_csv = open('shc_air.csv')
spec_heat_array = np.loadtxt(spec_heat_csv, delimiter = ' ')

def k_interp(temp, type): 
    
    cp_type = 1
    gamma_type = 2

    # Extract input and output type arrays from table
    table_temp = spec_heat_array[:, 0]
    table_cp = spec_heat_array[:, 1]
    table_cv = spec_heat_array[:, 2]

    # Get index of first value in input type array greater than input value
    i = np.argmax(table_temp >= temp)

    # Map input value onto output type array
    ratio = (temp - table_temp[i-1]) / (table_temp[i] - table_temp[i - 1])

    cp = ratio * (table_cp[i] - table_cp[i - 1]) + table_cp[i - 1] 
    cv = ratio * (table_cv[i] - table_cv[i - 1]) + table_cv[i - 1] 

    # Return selected output value
    if type == cp_type:
        return cp
    elif type == gamma_type:
        return cp / cv


def fuel_level(flow_fuel):

    # Turbine pressure ratio is calculated (w_turbine = w_compressor)
    # Input variables
    # Component Efficiencies                Unit        Source / notes
    eff_comp = 0.675                        # none      GTBA
    eff_comb = 0.925                        # none      GTBA
    eff_turb = 0.725                        # none      GTBA
    eff_nozz = 1                            # none      
    flow_fuel = flow_fuel/ 10**6 / 60       # m^3/s     Jetcat
    m_air = 0.23                            # kg/s      Jetcat 
    # Atmospheric Conditions
    t0 = 293.15                             # K         Test conditions
    p0 = 101.3                              # kPa       Test conditions
    # Fuel inputs
    d_fuel = 821                            # kg/m^3    Kerosene
    LHV_fuel = 43.0 * 1000                  # kJ/kg     Kerosene
    m_fuel = d_fuel * flow_fuel             # kg/s      calc
    f = m_fuel / m_air                      # none      calc
    m_tot = m_fuel + m_air                  # kg/s      calc
    # Known pressure ratios
    press_comp = 2.9                        # none      Jetcat
    press_comb = 0.97                       # none      OK State
    # Heat Capacities
    gamma_low = k_interp(t0, 2)             # unitless
    cp_low = k_interp(t0, 1)                # kJ/kgK

    # S00, Generator
    w_elec = 0.500                          # kW
    eff_gen = 0.5                           # unitless estimate
    w_shaft = w_elec / eff_gen              # Shaft power 

    # S0, Atmosphere
  
    # S1, Diffuser
    # Same as S0

    # S2, Compressor inlet
    # Same as S0

    # S3, Post compressor
    t3i = t0 * (press_comp ** ((gamma_low - 1) / gamma_low))
    p3 = press_comp * p0
    w_comp_i = m_air * cp_low * (t3i - t0)
    w_comp = w_comp_i / eff_comp
    t3a = (w_comp / (m_air * cp_low)) + t0

    # S4, Post combustor
    t4a = (1 + (f * eff_comb * LHV_fuel) / (cp_low * t3a)) * t3a / (1 + f)
    p4 = press_comb * p3

    gamma_high = k_interp(t4a, 2)
    cp_high = k_interp(t4a, 1)

    # S5, Post turbine
    t5a = t4a - (w_comp / (cp_high * m_tot))
    t5i = t4a - (w_comp / (cp_high * m_tot * eff_turb))
    p_turb = ((t5a / t4a) ** (gamma_high / (gamma_high - 1)))
    p5 = p_turb * p4

    # S6 - S8, Afterburner
    # Not used

    # S9, Nozzle exit plane
    t9a = eff_nozz * t5a
    p9 = p5
    p9static = p0

    cp_mid = k_interp(t9a, 1)
    gamma_mid = k_interp(t9a, 2)

    v9 = math.sqrt(2000 * cp_mid * t9a * (1 - ((p9static / p9) ** ((gamma_mid - 1) / gamma_mid))))
    thrust = m_tot * v9


    gas_const_air = 0.28705 # kg / m^3
    p9dynamic = p9 - p9static
    d_air_9 = p9 / (gas_const_air * t9a)
    v9test = math.sqrt(2000 * p9dynamic / d_air_9)
    thrusttest = m_tot * v9test

    stations = np.arange(0, 10, 1)
    temperatures = np.array([t0, t0, t0, t3a, t4a, t5a, t5a, t5a, t9a, t0])
    pressures = np.array([p0, p0, p0, p3, p4, p5, p5, p5, p9, p0])

    # Temperature and Pressure Plotting

    figTemp, ax = plt.subplots(figsize=(12,8))
    plt.plot(stations, temperatures)
    plt.xlabel("Station", size=12)
    plt.ylabel("Temperature (K)", size=12)
    plt.title("Jet Engine Model Temperatures", size=15)
    for index in range(len(stations)):
      ax.text(stations[index] - 0.2, temperatures[index] + 20, int(temperatures[index]), size=12)
    plt.xticks(stations, size=12)
    plt.grid()
    plt.show()

    figPress, ax = plt.subplots(figsize=(12,8))
    plt.plot(stations, pressures)
    plt.xlabel("Station", size=12)
    plt.ylabel("Pressure (kPa)", size=12)
    plt.title("Jet Engine Model Pressures", size=15)
    for index in range(len(stations)):
      ax.text(stations[index] - 0.2, pressures[index] + 4, int(pressures[index]), size=12)
    plt.xticks(stations, size=12)
    plt.grid()
    plt.show()

    return w_comp, v9, v9test, thrust


print(fuel_level(390))



# function iterates fuel flow to match thrust
#fuelFlow = 80
#desired_thrust = 2 #N
#measured_thrust = fuel_level(fuelFlow)

#while measured_thrust > desired_thrust:
#    fuelFlow = fuelFlow - 0.25
#    measured_thrust = fuel_level(fuelFlow)
#
#print(measured_thrust, fuelFlow)