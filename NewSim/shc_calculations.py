
import matplotlib.pyplot as plt
import numpy as np
import scipy as sc
import math
import random

# Original

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


def efficiency(press_comp, press_comb, press_turb, eff_comp, eff_comb, eff_turb):
    # Input variables               Unit        Source / notes
    flow_fuel = 390 / 10**6 / 60    # m^3/s     Jetcat
    v_in = 0                        # km/hr     Static test conditions
    v_out = 1560                    # km/hr     Jetcat
    m_air = 0.23                    # kg/s      Jetcat 
    # Atmospheric condition input variables
    t0 = 300                        # k         Test conditions
    p0 = 101.3                      # kPa       Test conditions
    d0 = 1.225                      # kg/m^3    Test conditions
    # Fuel inputs
    d_fuel = 0.821                  # kg/m^3    Kerosene
    LHV_fuel = 43.0                 # MJ/kg     Kerosene

    # Setup data table

    # Row 0: S0, Atmosphere
    # Row 1: S3, Post compressor
    # Row 2: S4, Post combustor
    # Row 3: S5, Post turbine
    # Row 4: S9, Nozzle exit plane

    # Col 0: t_i
    # Col 1: t_a
    # Col 2: h_i
    # Col 3: h_a
    # Col 4: p
    # Col 5: pr_i
    # Col 6: pr_a

    data = np.full((5, 7), -1)

    # S0, Atmosphere
    h0 = interp(t0, t, h)
    pr0 = interp(t0, t, pr)
    data[0] = np.array([t0, t0, h0, h0, p0, pr0, pr0])
  
    # S3, Post compressor
    p3 = press_comp * p0
    pr3 = press_comp * pr0

    h3_i = interp(pr3, pr, h)
    t3_i = interp(pr3, pr, t)
    w_ci = m_air * (h3_i - h0)
    
    h3_a = h0 + (h3_i - h0) / eff_comp 
    t3_a = t0 + (t3_i - t0) / eff_comp 
    w_ca = m_air * (h3_a - h0)

    data[1] = np.array([t3_i, t3_a, h3_i, h3_a, p3, pr3, pr3])

    # S4, Post combustor
    m_fuel = d_fuel * flow_fuel #kg/s
    q_fuel_i = m_fuel * LHV_fuel * 1000 # kJ
    q_fuel_a = eff_comb * q_fuel_i

    # To be checked

    h4_i = (q_fuel_a / m_air) + h3_i
    t4_i = interp(h4_i, h, t)
    pr4_i = interp(h4_i, h, pr)

    h4_a = (q_fuel_a / m_air) + h3_a
    t4_a = interp(h4_a, h, t)
    pr4_a = interp(h4_a, h, pr)

    p4 = p3 * press_comb

    data[2] = np.array([t4_i, t4_a, h4_i, h4_a, p4, pr4_i, pr4_a])

    # S5, Post turbine
    pr5_i = pr4_i / press_turb #what is okstate "power balance"?
    t5_i = interp(pr5_i, pr, t)
    h5_i = interp(t5_i, t, h)
    w_ti = m_air * (h4_i - h5_i)
    # actual
    pr5_a = pr4_a / press_turb #what is okstate "power balance"?
    h5_a = h4_a - eff_turb * (h4_a - h5_i)
    t5_a = interp(h5_a, h, t)
    w_ta = m_air * (h4_a - h5_a)
    p5 = p4 * press_turb

    # Incomplete


    return t3_a, t4_a


print(efficiency(2.9, 0.8, 0.85, 0.8, 0.7, 0.75))




# Specific Heat Method

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



def efficiency2(press_comp, press_comb, press_turb, eff_comp, eff_comb, eff_turb):
    # Input variables               Unit        Source / notes
    flow_fuel = 390 / 10**6 / 60    # m^3/s     Jetcat
    v0 = 0                          # km/hr     Static test conditions
    v_out = 1560                    # km/hr     Jetcat
    m_air = 0.23                    # kg/s      Jetcat 
    # Atmospheric condition input variables
    t0 = 300                        # k         Test conditions
    p0 = 101.3                      # kPa       Test conditions
    d0 = 1.225                      # kg/m^3    Test conditions
    # Fuel inputs
    d_fuel = 0.821                  # kg/m^3    Kerosene
    LHV_fuel = 43.0 * 1000          # kJ/kg     Kerosene


    # Setup data table

    # Row 0: S0, Atmosphere
    # Row 1: S3, Post compressor
    # Row 2: S4, Post combustor
    # Row 3: S5, Post turbine
    # Row 4: S9, Nozzle exit plane

    # Col 0: t_i
    # Col 1: t_a
    # Col 2: p_i
    # Col 3: p_a

    data = np.full((5, 4), -1)

    # S0, Atmosphere
    data[0] = np.array([t0, t0, p0, p0])
  
    # S1, Diffuser
    # Same as S0

    # S2, Compressor inlet
    # Same as S0

    # S3, Post compressor
    t3s = t0 * (press_comp ** ((k_interp(t0, 2) - 1) / k_interp(t0, 2)))
    t3a = t0 + (t3s - t0) / eff_comp
    p3 = press_comp * p0

    w_comp = m_air * (interp(t3a, t, h) - interp(t0, t, h))

    data[1] = np.array([t3s, t3a, p3, p3])

    # S4, Post combustor
    m_fuel = d_fuel * flow_fuel #kg/s
    q_fuel_s = m_fuel * LHV_fuel * 1000 # kJ
    q_fuel_a = eff_comb * q_fuel_s

    h4s = (q_fuel_a / m_air) + interp(t3s, t, h)
    t4s = interp(h4s, h, t)

    h4a = (q_fuel_a / m_air) + interp(t3a, t, h)
    t4a = (1 + (m_fuel / m_air) * LHV_fuel / (k_interp(t3a, 1) * t3a)) / (1 + (m_fuel / m_air))

    p4 = p3 * press_comb

    data[2] = np.array([t4s, t4a, p4, p4])

    # S5, Post turbine
    #t5a = t4a - (t3s - t0)
    

    #t5a = t4a - ((k_interp(t0, 1) / (k_interp(t4a, 1) / eff_turb)) * (t3a - t0))
    #t5s = t4a - ((t3a - t5a) / eff_turb)
    #h5a = interp(t5a, t, h)

    # Incomplete

    return t0, t3a, t4a


print(efficiency2(2.9, 0.8, 0.85, 0.8, 0.7, 0.75))
