#!/data/bin/python
import sys
sys.path.append('/data/ktran12/lib/sympy-0.7.0/')
import sympy
import os
import fileinput
import math
import operator

#Combination Function
def comb(n,k):
  return reduce(lambda a,b: a*(n-b)/(b+1),xrange(k),1)

#Binomial Probability Distribution Function
def binompdf(n,p,i):
  return float(comb(n,i)*(p**i)*((1-p)**(n-i)))

def generateConfigurations():
  cores = [1,2,4,8,10,12,14,16,18,20]
  numThreads = [1,2,4,8,16,32,64]
  lanes = [1,2,4,8,16,32,64]
  DCache = [16,32,64]
  ICache = [16,32,64]
  L2Cache = [4096]

  configList = []

  for i in cores:
    for j in numThreads:
      for k in lanes:
        if(k>j):
          break
        for l in DCache:
          for m in ICache:
            for o in L2Cache:
              configList.append([i,l,m,o,j,k,0,0,0])

  return configList

#Gets the areas of each component on a SIMD chip
def getArea(data):
  base_clock_GHz = 2.6
  base_tech = 65
  tech_node = 65
  l1area_per_KB = 2.43/64
  reg = 0.199358389
  alus = 0.513011101
  l2area_per_KB = 11.0/1024
  IO_skeleton = 1.005347206-reg-alus
  IO_clock_GHz = 1.0

  num_IOs = data[0]
  IO_Dcache_KB = data[1]
  IO_Icache_KB = data[2]
  IO_shared_L2size_KB = data[3]
  IO_SIMD_depth = data[4]/data[5]
  IO_SIMD_width = data[5]

  IO_core_alus = (IO_SIMD_width+config[7])*alus
  IO_core_regs = (IO_SIMD_width+config[7])*IO_SIMD_depth*reg
  IO_core_area = IO_skeleton + IO_core_alus + IO_core_regs
  IO_scale_factor = 1.0/base_clock_GHz/base_clock_GHz*IO_clock_GHz*IO_clock_GHz;

  IO_core = IO_core_area * IO_scale_factor
  alus_scaled = alus*IO_scale_factor
  reg_scaled_wDepth = reg*IO_SIMD_depth*IO_scale_factor

  IO_L1 = (IO_Icache_KB+IO_Dcache_KB)*l1area_per_KB
  IO_area = IO_core+IO_L1

  IO_L2 = IO_shared_L2size_KB*l2area_per_KB
  IO_all = IO_area*(num_IOs+config[6]) + IO_L2
  IO_all += (alus_scaled+reg_scaled_wDepth)*config[8]*config[0]/2

  die_area_IO_all = IO_all/base_tech*tech_node

  areaOut = [IO_core, alus_scaled, reg_scaled_wDepth, IO_skeleton*IO_scale_factor, IO_L1, IO_area, IO_L2, IO_all, die_area_IO_all]

  return areaOut

def getYieldComp(compArea_mm):
  defectDensity=0.025
  n=16.5

  return 1/math.pow(1+(compArea_mm/100)*defectDensity, n)

def getRedYield(compYield, base, spare):
  y = 0.0
  for i in range(base, base + spare + 1):
    y += float(comb(base + spare,i) * (compYield**i) * ((1-compYield)**(base + spare - i)))
    
  return y

def getCost(dieYield, dieArea):
  waferCost=3000  #Wafer cost in USD
  waferDiameter=300  #Wafer diameter in mm^2

  dicePerWafer = (math.pi*(waferDiameter/2)**2/dieArea)-(math.pi*waferDiameter/math.sqrt(2*dieArea))
  dieCost = waferCost/(dicePerWafer*dieYield)

  return dieCost


def getDieAreaYieldCost(config):

  areaList = getArea(config)
  numCores = config[0]
  sslYield = 1

  laneArea = areaList[1]+areaList[2]
  laneYield = getYieldComp(laneArea)
  laneRedYield = getRedYield(laneYield, config[5], config[7])
  
  if(config[8]>0):
    sslYield = 2*binompdf(config[5], laneYield, config[5]-1)*binompdf(config[5], laneYield, config[5])*laneYield
    sslYield += binompdf(config[5], laneYield, config[5])*binompdf(config[5], laneYield, config[5])*laneYield
    numCores=numCores%2

  skeletonArea = areaList[3]
  skeletonYield = getYieldComp(skeletonArea)
  l1CacheYield = 1
  coreYield = laneRedYield * l1CacheYield * skeletonYield
  coreRedYield = getRedYield(coreYield, numCores, config[6])

  l2CacheYield = 1

  dieYield = coreRedYield*l2CacheYield*(sslYield**(config[0]/2))

  dieCost = getCost(dieYield,areaList[8])
  
  '''
  print config
  print areaList
  print "Lane Area: " + str(laneArea) + "mm^2"
  print "Die Yield: " + str(dieYield) 
  print "Die Cost: " + str(dieCost) + "\n"
  '''
 
  return [areaList[8],dieYield,dieCost]

def getShortestPerf(config):
  eq = sympy.sympify('( -109.357 + ( -25.6347 * ( ( ( 92.1859 * x6 ) - ( ( ( ( -2.20927 * ( ( ( -201.968 * x5 ) - ( -92.6793 * x2 ) ) / x0 ) ) - ( 4.4781 * x8 ) ) - ( ( 21.4946 * x6 ) - ( ( 143.526 * x4 ) - ( ( ( 49.0981 * x6 ) - ( ( ( ( 5.18815 * ( ( ( 56.7044 * x1 ) - ( ( ( ( 62.0626 * x8 ) - ( 86.2029 * ( ( ( -19.5875 * x5 ) - ( -38.1151 * x2 ) ) / x0 ) ) ) - ( -196.047 * x0 ) ) - ( 51.5922 * x1 ) ) ) / ( ( 1.48716 * x3 ) - ( ( ( 42.1913 * x5 ) - ( 182.373 * x0 ) ) + ( ( ( ( 21.947 * x1 ) - ( -3.04785 * x4 ) ) - ( 97.5962 * ( ( ( 63.9273 * x6 ) - ( ( ( ( 149.521 * ( x0 / x5 ) ) - ( -0.892625 * x4 ) ) - ( 90.0825 * x0 ) ) - ( 0.0228199 * x1 ) ) ) / x0 ) ) ) - ( ( -99.8903 * ( ( ( 50.8458 * x5 ) - ( 29.9984 * x2 ) ) / x2 ) ) - ( 30.829 * x8 ) ) ) ) ) ) ) - ( 18.0301 * x4 ) ) - ( -15.959 * x4 ) ) - ( ( ( 13.1012 * x0 ) ^ ( 67.3139 * x8 ) ) - ( -9.95186 * x1 ) ) ) ) )^2 ) ) ) - ( ( ( -62.336 * x4 ) - ( ( ( 13.9078 * x6 ) - ( ( ( ( -3.64022 * ( ( ( 54.125 * x1 ) - ( ( -0.595084 * ( ( ( ( ( ( -48.0878 * x0 ) + ( ( 12.2064 * x4 ) ^ ( 78.9419 * x6 ) ) ) - ( 66.5776 * x4 ) ) - ( 61.323 * x6 ) ) - ( ( 61.2714 * x4 ) - ( 132.18 * x1 ) ) ) / x0 ) ) - ( -111.526 * x4 ) ) ) / ( ( 1.59766 * x3 ) - ( ( ( 99.357 * x5 ) - ( 72.0521 * x0 ) ) + ( ( ( ( ( 63.1587 * x0 ) + ( 63.6443 * x6 ) ) - ( 173.707 * x4 ) ) - ( 42.5172 * ( ( ( 54.1886 * x6 ) - ( ( ( ( 14.0581 * ( x8 / x5 ) ) - ( 0.338817 * x4 ) ) - ( 43.6322 * x0 ) ) - ( -0.120073 * x1 ) ) ) / x0 ) ) ) - ( ( 44.9849 * ( ( ( 34.5196 * x5 ) - ( 90.0463 * x2 ) ) / x2 ) ) - ( 91.7651 * x8 ) ) ) ) ) ) ) - ( -0.0514545 * x2 ) ) - ( 0.111878 * x4 ) ) - ( ( ( 24.3609 * x2 ) ^ ( 5.65791 * x8 ) ) - ( -391.707 * x1 ) ) ) ) )^2 ) + ( 61.9605 * x2 ) ) ) ) / ( ( 189.507 * x1 ) )^2 ) ) )')
  result=eq.subs('x0',config[0]).subs('x1',config[1]).subs('x2',config[2]).subs('x3',config[3]).subs('x4',config[4]).subs('x5',config[5]).subs('x6',config[6]).subs('x7',config[7]).subs('x8',config[8])

  return result

def getFilterPerf(config):
  eq = sympy.sympify('( 11.4533 + ( 4.05504e-05 * ( ( 41.6425 * x6 ) - ( ( ( ( ( 77.2051 * ( ( ( 66.4692 * ( ( x0 / x5 ) / ( ( 93.6097 * x0 ) )^2 ) ) - ( 98.6404 * x1 ) ) / ( ( 33.9483 * x4 ) )^2 ) ) + ( ( 51.4472 * x0 ) - ( ( 61.0716 * x8 ) )^2 ) ) ^ ( ( 93.3366 * x8 ) )^2 ) - ( ( ( ( 91.952 * ( x4 / ( ( ( ( ( ( ( ( ( ( 91.6766 * ( x4 * x1 ) ) ^ ( ( ( 88.5781 * ( ( ( ( ( 98.459 * ( x4 / x1 ) ) + ( 48.3747 * x6 ) ) )^2 )^2 / x1 ) ) + ( 92.7024 * x6 ) ) )^2 ) - ( 63.1303 * x8 ) ) ^ ( 84.0547 * x6 ) ) )^2 )^2 ^ ( ( ( ( 77.9855 * ( x4 / ( ( ( 27.7776 * ( x4 / x1 ) ) + ( 59.3983 * x6 ) ) - ( ( ( ( 64.9167 * ( x6 * ( ( ( ( ( 27.9308 * x0 ) + ( 92.5521 * x5 ) ) + ( ( ( ( ( ( ( ( 18.8497 * x3 ) )^2 )^2 ^ ( ( 69.1804 * x8 ) )^2 ) - ( ( ( 25.9681 * ( x4 / x1 ) ) + ( 62.981 * x6 ) ) )^2 ) - ( ( 8.0289 * x4 ) - ( 21.0501 * x0 ) ) ) - ( ( ( 85.2687 * x5 ) )^2 ^ ( ( 89.2557 * x8 ) )^2 ) ) )^2 ) )^2 * ( ( x0 / x5 ) / ( ( 61.6926 * x6 ) - ( ( ( ( ( 61.4738 * x0 ) - ( ( ( 54.7249 * x0 ) )^2 )^2 ) - ( 54.3023 * ( ( ( 59.1142 * x0 ) )^2 / x1 ) ) ) + ( 87.6732 * x5 ) ) - ( 4.74943 * x5 ) ) ) ) ) ) ) - ( 19.1858 * x0 ) ) )^2 + ( 80.0098 * x3 ) ) ) ) ) + ( 93.3095 * x6 ) ) - ( ( ( 9.86236 * x8 ) )^2 )^2 ) - ( 67.5879 * x1 ) ) ) - ( ( ( -6.91845 * ( x4 / x1 ) ) + ( ( 39.6405 * x0 ) - ( ( 59.2903 * x8 ) )^2 ) ) )^2 ) - ( ( 15.6634 * x1 ) - ( 185.906 * x0 ) ) ) - ( ( ( 36.2758 * x6 ) )^2 ^ ( ( ( 79.6764 * x8 ) )^2 )^2 ) ) ) ) + ( 98.69 * x6 ) ) + ( 100.193 * x6 ) ) )^2 ) - ( ( ( ( ( 90.334 * ( ( x0 / x5 ) / ( ( -0.244298 * x0 ) )^2 ) ) - ( 48.3277 * x1 ) ) - ( ( ( ( ( ( ( ( 74.7876 * ( x4 / x1 ) ) + ( 15.2101 * x6 ) ) )^2 )^2 ^ ( ( 80.0232 * x8 ) )^2 ) - ( ( 8.19679 * ( x4 / x1 ) ) )^2 ) - ( ( 35.2602 * x6 ) - ( ( ( ( ( 160.795 * ( x4 / x1 ) ) + ( 70.0722 * x7 ) ) - ( ( ( 95.9528 * x8 ) )^2 )^2 ) - ( -5.51979 * x1 ) ) - ( ( -6.48835 * x1 ) - ( -4.20551 * x5 ) ) ) ) ) - ( ( ( 82.8799 * x5 ) )^2 ^ ( ( 10.4704 * x8 ) )^2 ) ) ) - ( ( ( ( 53.0045 * x4 ) )^2 ^ ( ( ( 1.06568 * x8 ) )^2 )^2 ) - ( 59.1946 * x1 ) ) ) - ( ( ( ( ( ( ( 45.314 * x5 ) ^ ( ( 9.92804 * x8 ) )^2 ) - ( ( ( 0.824633 * ( x4 / x1 ) ) + ( 35.0825 * x6 ) ) )^2 ) - ( 0.0493153 * x1 ) ) - ( 14.3583 * x7 ) ) )^2 + ( 68.8789 * x3 ) ) ) ) ) ) )')

  result=eq.subs('x0',config[0]).subs('x1',config[1]).subs('x2',config[2]).subs('x3',config[3]).subs('x4',config[4]).subs('x5',config[5]).subs('x6',config[6]).subs('x7',config[7]).subs('x8',config[8])

  return result

def getAvgPerf(config):

  eq = sympy.sympify('( 11.5417 + ( 0.00508481 * ( ( ( ( ( ( ( 6.77246 * x2 ) - ( ( ( ( ( 44.8533 * x0 ) + ( 36.9014 * x5 ) ) - ( ( 80.7387 * x1 ) + ( 107.142 * ( ( ( ( ( -131.701 * x4 ) + ( 1.42475 * x1 ) ) / x4 ) / ( ( ( 3.01692 * x0 ) + ( 3.22937 * x4 ) ) + ( 0.00137602 * x3 ) ) ) * ( ( ( 25.0434 * x1 ) - ( ( ( -6.01733 * x4 ) + ( ( ( -108.891 * x0 ) + ( 2.42072 * x5 ) ) + ( 28.8689 * x1 ) ) ) - ( ( 126.135 * x4 ) + ( 0.0688717 * x3 ) ) ) ) / ( ( 101.054 * x0 ) + ( 0.0860422 * x4 ) ) ) ) ) ) ) - ( 50.581 * x1 ) ) + ( 192.039 * x4 ) ) ) - ( 4.87047 * x6 ) ) + ( 64.5344 * ( ( x1 / ( ( 50.1788 * x4 ) + ( ( ( 5.29947 * x0 ) + ( 0.586408 * x5 ) ) + ( 104.23 * x1 ) ) ) ) * ( ( -54.5872 * ( x1 / ( x3 / x0 ) ) ) + ( 73.8578 * x1 ) ) ) ) ) - ( -4.66654 * x6 ) ) + ( 79.3636 * ( ( x1 / ( ( 0.593013 * x4 ) + ( 125.153 * x1 ) ) ) * ( ( 2.2734 * ( x3 / x0 ) ) + ( ( ( 73.9176 * x0 ) + ( 59.3446 * x5 ) ) - ( ( 0.274337 * ( ( ( ( 125.534 * x3 ) - ( 13.3396 * x1 ) ) * ( ( -9.05838 * x4 ) + ( 102.807 * x1 ) ) ) / x3 ) ) + ( 88.4397 * x1 ) ) ) ) ) ) ) / x1 ) ) )')

  result=eq.subs('x0',config[0]).subs('x1',config[1]).subs('x2',config[2]).subs('x3',config[3]).subs('x4',config[4]).subs('x5',config[5]).subs('x6',config[6]).subs('x7',config[7]).subs('x8',config[8])

  return result

if __name__=='__main__':
  configList=[]
  perfYield=[]

  output=file('shortestBase.txt','w')
  
  configList=generateConfigurations()

  for i,config in enumerate(configList):
    config = map(int, config)
    dieOut=getDieAreaYieldCost(config)
    perfOut=getShortestPerf(config)

    dataOut=[config,dieOut[0],dieOut[1],dieOut[2],perfOut]
    output.write('"'+' '.join(str(n) for n in config)+'"'+','+str(dieOut[0])+','+str(dieOut[1])+','+str(dieOut[2])+','+str(perfOut)+'\n')
    perfYield.append(dataOut)


  output.close()

