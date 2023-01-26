
import matplotlib.pyplot as plt
import numpy as np
import scipy as sc
import math
import random

# Load ideal gas properties table
gasPropCsv = open('ideal_gas_prop.csv')
gasPropArray = np.loadtxt(gasPropCsv, delimiter = ' ')

# Match table column to data type
t = 0 # temperature
h = 1 # entropy
pr = 2 # relative pressure

# Table interpolation function
# Input value, input type and output type
def interp(val, typeIn, typeOut): 
    
    # Extract input and output type arrays from table
    tableIn = gasPropArray[:, typeIn]
    tableOut = gasPropArray[:, typeOut]

    # Get index of first value in input type array greater than input value
    i = np.argmax(tableIn >= val) 

    # Map input value onto output type array
    ratio = (val - tableIn[i - 1]) / (tableIn[i] - tableIn[i - 1])
    val_out = ratio * (tableOut[i] - tableOut[i - 1]) + tableOut[i - 1] 
    return val_out

specHeatCsv = open('shc_air.csv')
specHeatArray = np.loadtxt(specHeatCsv, delimiter = ' ')

def k_interp(temp, type): 
    
    cpType = 1
    gammaType = 2

    # Extract input and output type arrays from table
    tableTemp = specHeatArray[:, 0]
    tableCp = specHeatArray[:, 1]
    tableCv = specHeatArray[:, 2]

    # Get index of first value in input type array greater than input value
    i = np.argmax(tableTemp >= temp)

    # Map input value onto output type array
    ratio = (temp - tableTemp[i-1]) / (tableTemp[i] - tableTemp[i - 1])

    cp = ratio * (tableCp[i] - tableCp[i - 1]) + tableCp[i - 1] 
    cv = ratio * (tableCv[i] - tableCv[i - 1]) + tableCv[i - 1] 

    # Return selected output value
    if type == cpType:
        return cp
    elif type == gammaType:
        return cp / cv


def fuelLevel(flowFuel, wGen):

    # Turbine pressure ratio is calculated (w_turbine = w_compressor)
    # Input variables
    # Component Efficiencies                Unit        Source / notes
    effComp = 0.675                        # none      GTBA
    effComb = 0.925                        # none      GTBA
    effTurb = 0.725                        # none      GTBA
    effNozz = 1                            # none      
    flowFuel = flowFuel/ 10**6 / 60       # m^3/s     Jetcat
    mAir = 0.23                            # kg/s      Jetcat 
    # Atmospheric Conditions
    t0 = 293.15                             # K         Test conditions
    p0 = 101.3                              # kPa       Test conditions
    # Fuel inputs
    dFuel = 821                            # kg/m^3    Kerosene
    lhvFuel = 43.0 * 1000                  # kJ/kg     Kerosene
    mFuel = dFuel * flowFuel             # kg/s      calc
    f = mFuel / mAir                      # none      calc
    mTot = mFuel + mAir                  # kg/s      calc
    # Known pressure ratios
    pressComp = 2.9                        # none      Jetcat
    pressComb = 0.97                       # none      OK State
    # Heat Capacities
    gammaLow = k_interp(t0, 2)             # unitless
    cpLow = k_interp(t0, 1)                # kJ/kgK

    # S00, Generator
    wElec = 0.500                          # kW
    effGen = 0.5                           # unitless estimate
    wShaft = wElec / effGen              # Shaft power 

    # S0, Atmosphere
    h0 = interp(t0, t, h)

    # S1, Diffuser
    # Same as S0

    # S2, Compressor inlet
    # Same as S0

    # S3, Post compressor
    p3 = pressComp * p0

    t3i = t0 * (pressComp ** ((gammaLow - 1) / gammaLow))
    h3i = interp(t3i, t, h)
    
    wCompi = mAir * (h3i - h0)
    wCompa = wCompi / effComp
    
    h3a = (wCompa / mAir) + h0
    t3a = interp(h3a, h, t)

    # S4, Post combustor

    qFueli = mFuel * lhvFuel
    qFuela = qFueli * effComb

    h4a = (qFuela / mTot) + (h3a / (1 + f))
    t4a = interp(h4a, h, t)
    p4 = pressComb * p3

    gammaHigh = k_interp(t4a, 2)

    # S5, Post turbine
    h5a = h4a - (wCompa / (mTot * effTurb))
    t5a = interp(h5a, h, t)

    pTurb = ((t5a / t4a) ** (gammaHigh / (gammaHigh - 1)))

    p5 = pTurb * p4

    # S6 - S7, Afterburner
    # Not used

    # S8, Nozzle exit plane
    p8 = p5
    t8a = t5a
    h8a = h5a

    # S9, Exit
    h9a = h0
    
    v9 = math.sqrt(2000 * (h8a - h9a))
    thrust = mTot * v9

    return p0, p3, p4, p5, p8
    #return h0, h3a, h4a, h5a, h8a, h9a

print(fuelLevel(390, 0))

'''ss_comb * p3

    gamma_high = k_interp(t4a, 2)
    cp_high = k_interp(t4a, 1)


  

    #w_comp = m_air * cp_low * (t3i - t0)

    #lhs = (w_comp / m_air) + (w_gen / m_tot)
    #rhs = (1 + f) * cp_high (t4a - t5a)

    fNew = 1 + eff_turb * (1 + (w_gen / w_comp))







    # m_tot * (1 + f) * cp * (t4 - t5)


    
    t4a = (1 + (f * eff_comb * LHV_fuel) / (cp_low * t3a)) * t3a / (1 + f)
    t5a = t4a - (w_comp / (cp_high * m_tot * eff_turb))
    t5i = t4a - eff_turb * (t4a - t5a)






    # S5, Post turbine
    t5a = t4a - (w_comp / (cp_high * m_tot * eff_turb))
    t5i = t4a - eff_turb * (t4a - t5a)
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

    v9test2 = math.sqrt(2000 * cp_mid * (t9a - t0))
    thrusttest2 = m_tot * v9test2


    workBalComp = cp_low * (t3a - t0)
    workBalTurb1 = (1 + f) * eff_turb * cp_high * (t4a - t5a)


    gas_const_air = 0.28705 # kg / m^3

    p9dynamic = p9 - p9static
    d_air_9 = p9 / (gas_const_air * t9a)

    v9test = math.sqrt(2000 * p9dynamic / d_air_9)

    thrusttest = m_tot * v9test

    temperatures = np.array([t0, t3a, t4a, t5a, t9a])
    pressures = np.array([p0, p3, p4, p5, p9])

    return w_comp, t9a, p9, thrust

'''








'''
    fig = plt.figure()
    ax = fig.add_subplot(111)
    x_base = np.array([0, 3, 4, 5, 9])
    plt.plot(x_base, temperatures, 'g-')
    plt.title("Temperatures")
    plt.xticks(np.arange(min(x_base), max(x_base) + 1, 1.0))
    plt.xlabel("Station")
    plt.ylabel("Temperature, K")
    for i, v in enumerate(temperatures):
        ax.text(i, v + 25, "%d" %v, ha="center")
        plt.ylim(0, max(temperatures) + 100)
    plt.show()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    x_base = np.array([0, 3, 4, 5, 9])
    plt.plot(x_base, pressures, 'g-')
    plt.title("Pressures")
    plt.xticks(np.arange(min(x_base), max(x_base) + 1, 1.0))
    plt.xlabel("Station")
    plt.ylabel("Pressures, K")
    for i, v in enumerate(pressures):
        ax.text(i, v + 25, "%d" %v, ha="center")
        plt.ylim(0, max(pressures) + 100)
    plt.show()


    

print(fuel_level(390))
'''

# function iterates fuel flow to match thrust
#fuelFlow = 80
#desired_thrust = 2 #N
#measured_thrust = fuel_level(fuelFlow)

#while measured_thrust > desired_thrust:
#    fuelFlow = fuelFlow - 0.25
#    measured_thrust = fuel_level(fuelFlow)
#
#print(measured_thrust, fuelFlow)