#!/data/bin/python

def getArea(data):
  base_clock_GHz = 2.6;
  base_tech = 65;
  l1area_per_KB = 2.43/64;
  reg = 0.199358389;
  alus = 0.513011101;
  l2area_per_KB = 11.0/1024;
  OOO_1way_area = 3.207190567/2;
  IO_skeleton = 1.005347206-reg-alus;

  IO_core_alus = IO_SIMD_width*alus
  IO_core_regs = IO_SIMD_width*IO_SIMD_depth*reg
  IO_core_area = IO_skeleton + IO_core_alus + IO_core_regs
  IO_scale_factor = 1.0/base_clock_GHz/base_clock_GHz*IO_clock_GHz*IO_clock_GHz;
  IO_core = IO_core_area * IO_scale_factor
  IO_core_alus = IO_core_alus*IO_scale_factor
  IO_core_regs = IO_core_regs*IO_scale_factor
  IO_L1 = (IO_Icache_KB+IO_Dcache_KB)*l1area_per_KB;
  IO_area = IO_core+IO_L1;
  IO_L2 = IO_shared_L2size_KB*l2area_per_KB;
  IO_all = IO_area*num_IOs + IO_L2;
  die_area_IO_all = IO_all/base_tech*tech_node;

  return areaOut

#
# Yield estimate
#
def getYieldComp(compArea, defectDensity, n):
  return 1/math.pow(1+compArea*defectDensity, n)

##
# Yield for component level redundancy in cores
# Y(redundancy) = Sum (i=min : base+spare) { C(i, base+spare) * Prob(good)^i * Prob(bad)^(base+spare-i) }
##
def clrYield( comp, compYield, base, spare):
  #coreCompYield = {}
  #for key in coreComp:
  y = 0.0
  for i in range(base, base + spare + 1):
    y += float(comb(base + spare,i) * (compYield**i) * ((1-compYield)**(base + spare - i)))
    #print i, " ", base, " ", spare, " ", comb(base + spare,i), " ", (compYield**i), " ", ((1-compYield)**(base + spare - i))
  #print comp," ",base," ",spare," ",compYield," ",y
    
  return y

#
# Combination Function
#   Source: public forum http://www.velocityreviews.com/forums/t502438-combination-function-in-python.html
#
def comb(n,k):
  return reduce(lambda a,b: a*(n-b)/(b+1),xrange(k),1)

#
# Calculate Yield of each element in each core based on component level redundancy
# Obtain the Yield of the core with a product of the component yields
#
def getYieldCores( coreList, compYieldList, origCoreList, spareCoreList):
  coreYield = []
  for idx, coreAreas in enumerate( coreList ):
    coreConfig = origCoreList[idx]
    spareConfig = spareCoreList[idx]
    indivCompYield = compYieldList[idx]
    compYield = {}
    # compYield takes into account spares -- Component Level Redundancy
    for key in core:
      compYield[key] = clrYield(key, indivCompYield[key], coreConfig[key], spareConfig[key])
      #print "{0} ==> {1}".format(key, compYield[key])
    # coreYield obtained by multiplying the component yields
    y = 1.0
    for key in compYield:
      y *= compYield[key]
    coreYield.append(y)
  
  return coreYield

#
#
#
def getDieYield( coreYield, area, count, techNode ):
  # Calculate the Yield and Area of the die
  # Product
  dieYield = 1.0
  dieArea = 0.0
  for idx, core in enumerate(area):
    dieYield *= coreYield[idx]
    #dieArea += area["core{0}".format(idx)]
    numComp = count[idx]
    for key in numComp:
      dieArea = (dieArea + (numComp[key] * core[key])) 
  
  return dieYield, len(coreYield), dieArea

def getPerformance(data):

  return perfOut

if __name__=='__main__':
  dramDefects = 2430
  mpuDefects = 1395
  techNodes="32"

  config=[]
  perfYield=[]

  #Parse configuration sata
  configDataFile=file('input.txt','r')
  for line in configDataFile:
    config.append(line.rstrip().split(';'))
  configDataFile.close()

  for data in config:
    dataPoint=[getPerformance(data) getDieYield(data)]
    perfYield.append(dataPoint)
    
  
