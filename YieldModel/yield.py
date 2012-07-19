#!/data/bin/python

def getArea(data):

  return areaOut

def getYield(data):

  return yieldOut

def getPerformance(data):

  return perfOut



if __name__=='__main__':
  config=[]
  perfYield=[]

  #Parse configuration sata
  configDataFile=file('input.txt','r')
  for line in configDataFile:
    config.append(line.rstrip().split(';'))
  configDataFile.close()

  for data in config:
    dataPoint=[getPerformance(data) getYield(data)]
    perfYield.append(dataPoint)
    
  
