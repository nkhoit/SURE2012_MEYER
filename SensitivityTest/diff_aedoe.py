#!/data/bin/python
import sys
import fileinput
import csv

cores=[1,2,4,6,8,10,12,14,16,18,20]
DCache=[8,16,32,64]
SIMD=[(1,1),(1,2),(1,4),(1,8),(1,16),(1,32),(1,64),(2,2),(2,4),(2,8),(2,16),(2,32),(2,64),(4,4),(4,8),(4,16),(4,32),(4,64),(8,8),(8,16),(8,32),(8,64),(16,16),(16,32),(16,64),(32,32),(32,64),(64,64)]

if __name__=="__main__":
  simPoints=[]
  base=[]
  GPRSCounter=0
  simCounter=0
  previousCounter=0

  pointsToSim=file('simPoints_all.txt','r')
  baseIn=list(csv.reader(open('averageBase.txt'),delimiter=','))
  previousCounter=len(baseIn)

  for line in pointsToSim:
    simPoints.append(map(int,line.rstrip().split()))
  pointsToSim.close()

  for line in baseIn:
    base.append(map(int,line[0].split(' ')))

  for i in simPoints:
    alreadySimulated=False
    GPRSCounter+=1
    for j in base:
      if (cores[i[0]]==j[0] and DCache[i[1]]==j[1] and SIMD[i[2]][1]==j[4] and SIMD[i[2]][0]==j[5]):
        test=j
        alreadySimulated=True
        break
    if not alreadySimulated:
      print '--CpuFrequency=2.00GHz --DTBsize=1024 --DcacheBanks=4 --DcacheBlkSize=128 --DcacheHWPFdegree=1 --DcacheHWPFpolicy=none --DcacheLookupLatency=2ns --DcachePropagateLatency=0ns --DcacheRepl=LRU --ITBsize=256 --IcacheAssoc=4 --IcacheBlkSize=128 --IcacheHWPFdegree=1 --IcacheHWPFpolicy=none --L2NetBandWidthMbps=456000 --L2NetFrequency=300MHz --L2NetPortOutQueueLength=4 --L2NetRouterBufferSize=256 --L2NetRoutingLatency=1ns --L2NetTimeOfFlight=13t --L2NetType=FullyNoC --L2NetWormHole=True --MemNetBandWidthMbps=128000 --MemNetFrequency=266MHz --MemNetPortOutQueueLength=4 --MemNetRouterBufferSize=2048 --MemNetTimeOfFlight=130t --l2Assoc=16 --l2Banks=16 --l2BlkSize=128 --l2HWPFDataOnly=False --l2HWPFdegree=1 --l2HWPFpolicy=none --l2MSHRs=256 --l2Repl=LRU --l2TgtsPerMSHR=64 --l2lookupLatency=2ns --l2propagateLatency=30ns --l2tol1ratio=2 --localAddrPolicy=0 --maxThreadBlockSize=0 --physmemLatency=100ns --physmemSize=1024MB --portLookup=0 --protocol=mesi --randStackOffset=True --restoreContextDelay=0 --retryDcacheDelay=100 --stackAlloc=3 --switchOnDataAcc=True' + '--benchmark=LU --DcacheSize='+str(DCache[i[1]])+'kB --DcacheAssoc=8 --numHWTCs='+str(SIMD[i[2]][1])+ '--numSWTCs=2 --numcpus='+str(cores[i[0]])+' --l2Size=4096kB --IcacheSize=16kB --warpSize='+str(SIMD[i[2]][0])
      simCounter+=1


  print 'Total Design Space: ' + str(len(cores)*len(DCache)*len(SIMD)) + ' points; Points already simulated: ' + str(previousCounter) + ' points; Points required by GPRS: ' + str(GPRSCounter) + ' points; Points left to simulate: ' + str(simCounter)

      



