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

def getAvgPerf(config):

  eq = sympy.sympify('( 11.5417 + ( 0.00508481 * ( ( ( ( ( ( ( 6.77246 * x2 ) - ( ( ( ( ( 44.8533 * x0 ) + ( 36.9014 * x5 ) ) - ( ( 80.7387 * x1 ) + ( 107.142 * ( ( ( ( ( -131.701 * x4 ) + ( 1.42475 * x1 ) ) / x4 ) / ( ( ( 3.01692 * x0 ) + ( 3.22937 * x4 ) ) + ( 0.00137602 * x3 ) ) ) * ( ( ( 25.0434 * x1 ) - ( ( ( -6.01733 * x4 ) + ( ( ( -108.891 * x0 ) + ( 2.42072 * x5 ) ) + ( 28.8689 * x1 ) ) ) - ( ( 126.135 * x4 ) + ( 0.0688717 * x3 ) ) ) ) / ( ( 101.054 * x0 ) + ( 0.0860422 * x4 ) ) ) ) ) ) ) - ( 50.581 * x1 ) ) + ( 192.039 * x4 ) ) ) - ( 4.87047 * x6 ) ) + ( 64.5344 * ( ( x1 / ( ( 50.1788 * x4 ) + ( ( ( 5.29947 * x0 ) + ( 0.586408 * x5 ) ) + ( 104.23 * x1 ) ) ) ) * ( ( -54.5872 * ( x1 / ( x3 / x0 ) ) ) + ( 73.8578 * x1 ) ) ) ) ) - ( -4.66654 * x6 ) ) + ( 79.3636 * ( ( x1 / ( ( 0.593013 * x4 ) + ( 125.153 * x1 ) ) ) * ( ( 2.2734 * ( x3 / x0 ) ) + ( ( ( 73.9176 * x0 ) + ( 59.3446 * x5 ) ) - ( ( 0.274337 * ( ( ( ( 125.534 * x3 ) - ( 13.3396 * x1 ) ) * ( ( -9.05838 * x4 ) + ( 102.807 * x1 ) ) ) / x3 ) ) + ( 88.4397 * x1 ) ) ) ) ) ) ) / x1 ) ) )')

  result=eq.subs('x0',config[0]).subs('x1',config[1]).subs('x2',config[2]).subs('x3',config[3]).subs('x4',config[4]).subs('x5',config[5]).subs('x6',config[6]).subs('x7',config[7]).subs('x8',config[8])

  return result

if __name__=='__main__':
  configList=[]
  perfYield=[]

  output=file('yieldEverything.txt','w')
  
  '''
  #Parse configuration sata
  configDataFile=file('configPoster.txt','r')
  for line in configDataFile:
    configList.append(line.rstrip().split(' '))
  configDataFile.close()
  '''

  configList=generateConfigurations()


  for i,config in enumerate(configList):
    config = map(int, config)
    '''
    dataPoint=[getPerformance(config), getDieYield(config)]
    output.write(str(dataPoint[0])+' '+str(dataPoint[1])+';'+'\n')
    perfYield.append(dataPoint)
    '''
    if(i<int(len(configList)/4)):
      dieOut=getDieAreaYieldCost(config)
      perfOut=getAvgPerf(config)

      dataOut=[config,dieOut[0],dieOut[1],dieOut[2],perfOut]
      perfYield.append(dataOut)

    '''
    change=[0,0,0]
    if(i%4==0):
      base=dieOut
    else:
      for j in range(len(base)):
        change[j]=(dieOut[j]-base[j])/base[j]

      temp=' '.join(str(n) for n in config)
      output.write('"'+temp+'"'+','+str(change[0])+','+str(change[1])+','+str(change[2])+',,')
      if(i%4==3):
        output.write('\n')
    '''

  
  perfYield=sorted(perfYield, key=operator.itemgetter(3))
  perfList=[]
  peratoOptimalBase=[]
  index=0
  for line in perfYield:
    perfList.append(line[4])

  while(index<len(perfYield)):
    index=perfList.index(max(perfList[index:]))
    peratoOptimalBase.append(perfYield[index][0])
    #output.write(str(perfYield[index])+'\n')
    index=index+1

  peratoOptimalAll=[]
  for config in peratoOptimalBase:
    config[6:]=[0,0,0]
    dieOut=getDieAreaYieldCost(config)
    perfOut=getAvgPerf(config)

    dataOut=[config,dieOut[0],dieOut[1],dieOut[2],perfOut]
    peratoOptimalAll.append(dataOut)

    temp=' '.join(str(n) for n in config)
    output.write('"'+temp+'"'+','+str(dieOut[0])+','+str(dieOut[1])+','+str(dieOut[2])+','+str(perfOut)+'\n')

  for config in peratoOptimalBase:
    config[6:]=[1,0,0]
    dieOut=getDieAreaYieldCost(config)
    perfOut=getAvgPerf(config)

    dataOut=[config,dieOut[0],dieOut[1],dieOut[2],perfOut]
    peratoOptimalAll.append(dataOut)

    temp=' '.join(str(n) for n in config)
    output.write('"'+temp+'"'+','+str(dieOut[0])+','+str(dieOut[1])+','+str(dieOut[2])+','+str(perfOut)+'\n')

  for config in peratoOptimalBase:
    config[6:]=[0,1,0]
    dieOut=getDieAreaYieldCost(config)
    perfOut=getAvgPerf(config)

    dataOut=[config,dieOut[0],dieOut[1],dieOut[2],perfOut]
    peratoOptimalAll.append(dataOut)

    temp=' '.join(str(n) for n in config)
    output.write('"'+temp+'"'+','+str(dieOut[0])+','+str(dieOut[1])+','+str(dieOut[2])+','+str(perfOut)+'\n')

  for config in peratoOptimalBase:
    config[6:]=[0,0,1]
    dieOut=getDieAreaYieldCost(config)
    perfOut=getAvgPerf(config)

    dataOut=[config,dieOut[0],dieOut[1],dieOut[2],perfOut]
    peratoOptimalAll.append(dataOut)

    temp=' '.join(str(n) for n in config)
    output.write('"'+temp+'"'+','+str(dieOut[0])+','+str(dieOut[1])+','+str(dieOut[2])+','+str(perfOut)+'\n')



  output.close()

