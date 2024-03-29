
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


def shc_eff(eff_comp, eff_comb, eff_turb, eff_nozz):

    # Turbine pressure ratio is calculated (w_turbine = w_compressor)
    # Dependent on component efficiencies

    # Input variables               Unit        Source / notes
    flow_fuel = 390/ 10**6 / 60     # m^3/s     Jetcat
    v0 = 0                          # km/hr     Static test conditions
    v_out = 1560                    # km/hr     Jetcat
    m_air = 0.23                    # kg/s      Jetcat 
    # Atmospheric condition input variables
    t0 = 293.15                     # k         Test conditions
    p0 = 101.3                      # kPa       Test conditions
    d0 = 1.225                      # kg/m^3    Test conditions
    # Fuel inputs
    d_fuel = 821                    # kg/m^3    Kerosene
    LHV_fuel = 43.0 * 1000          # kJ/kg     Kerosene
    # Known pressure ratios
    press_comp = 2.9

    m_fuel = d_fuel * flow_fuel # kg/s
    f = m_fuel / m_air
    m_tot = m_fuel + m_air

    p_comb = 0.97   # OK State

    gamma_low = k_interp(t0, 2)
    cp_low = k_interp(t0, 1)

    # S00, Generator
    w_elec = 0.500              # kW
    eff_gen = 0.5               # unitless estimate
    w_shaft = w_elec / eff_gen  # Shaft power 

    # S0, Atmosphere
  
    # S1, Diffuser
    # Same as S0

    # S2, Compressor inlet
    # Same as S0

    # S3, Post compressor
    t3i = t0 * (press_comp ** ((gamma_low - 1) / gamma_low))
    t3a = t0 + ((t3i - t0) / eff_comp)
    p3 = press_comp * p0

    w_comp = m_air * cp_low * (t3a - t0)

    # S4, Post combustor
    t4a = (1 + (f * eff_comb * LHV_fuel)/(cp_low * t3a)) * t3a / (1 + f)
    p4 = p_comb * p3

    gamma_high = k_interp(t4a, 2)
    cp_high = k_interp(t4a, 1)

    # S5, Post turbine
    t5a = t4a - (w_comp / (cp_high * m_tot))
    t5i = t4a - (eff_turb * (t4a - t5a))
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

    return v9, thrust, t9a, p9

print(shc_eff(0.675, 0.925, 0.725, 1))