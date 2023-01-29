
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

# Cp and Gamma interpolation function
# Input temperature value, output type (cp: 1, gamma: 2)
def k_interp(temp, type): 
    
    # Assign value to cp and gamma types
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


def fuelLevel(flowFuel, wElec, effGen):

    # Turbine pressure ratio is calculated (w_turbine = w_compressor)
    # Input variables
    # Component Efficiencies                Unit        Source / notes
    effComp = 0.675                         # none      GTBA
    effComb = 0.925                         # none      GTBA
    effTurb = 0.725                         # none      GTBA
    effNozz = 1                             # none      
    flowFuel = flowFuel/ 10**6 / 60         # m^3/s     Jetcat
    mAir = 0.23                             # kg/s      Jetcat 
    # Atmospheric Conditions
    t0 = 293.15                             # K         Test conditions
    p0 = 101.3                              # kPa       Test conditions
    # Fuel inputs
    dFuel = 821                             # kg/m^3    Kerosene
    lhvFuel = 43.0 * 1000                   # kJ/kg     Kerosene
    mFuel = dFuel * flowFuel                # kg/s      calc
    f = mFuel / mAir                        # none      calc
    mTot = mFuel + mAir                     # kg/s      calc
    # Known pressure ratios
    pressComp = 2.9                         # none      Jetcat
    pressComb = 0.97                        # none      OK State
    # Heat Capacities
    gammaLow = k_interp(t0, 2)              # unitless
    cpLow = k_interp(t0, 1)                 # kJ/kgK

    # S00, Generator
    wShaft = wElec / effGen                 # Shaft power 

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
    wCompa = wCompi / effComp + wShaft
    
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

    cp_mid = k_interp(t8a, 1)
    gamma_mid = k_interp(t8a, 2)

    v9 = math.sqrt(2000 * cp_mid * t8a * (1 - ((p0 / p8) ** ((gamma_mid - 1) / gamma_mid))))
    thrust = mTot * v9

    # Temperature and Pressure Plotting
    '''
    stations = np.arange(0, 6, 1)
    temperatures = np.array([t0, t0, t3a, t4a, t5a, t8a])
    pressures = np.array([p0, p0, p3, p4, p5, p8])

    figTemp, ax = plt.subplots(figsize=(12,6))
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
    '''

    return thrust

print(fuelLevel(339.98, 0, 1))


# Plot fuelLevel

def plotFuelLevel(wElec, effGen):
    fuelRange = np.arange(200, 390, 1)
    thrustValues = np.zeros(len(fuelRange))

    for i in range(len(fuelRange)):
        thrustValues[i] = fuelLevel(fuelRange[i], wElec, effGen)

    figTemp, ax = plt.subplots(figsize=(12,6))
    plt.plot(fuelRange, thrustValues, color = 'b')
    plt.axhline(y= 100, color = 'r')
    plt.xlabel("Fuel Input (ml/min)", size=12)
    plt.ylabel("Thrust Output (N)", size=12)
    plt.title("Jet Engine Model Thrust Output at %1.2f kW Electrical Output" % wElec, size=15)
    #plt.xticks(stations, size=12)
    plt.grid()
    plt.show()

#print(plotFuelLevel(0, 1))
#print(plotFuelLevel(0.5, 0.5))



# At wElec = 0.0, effGen = 1.0, fuelFlow = 339.98 for 100 N thrust output (100.000919)
# At wElec = 0.5, effGen = 0.5, fuelFlow = 349.38 for 100 N thrust output (100.000352)