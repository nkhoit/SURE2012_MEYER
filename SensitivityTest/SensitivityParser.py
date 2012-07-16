#!/data/bin/python
import sys
sys.path.append('/data/ktran12/lib/sympy-0.7.0/')
import sympy
import subprocess
import os
import fileinput
import math

dataList=[]

for filename in os.listdir('./output'):
  dataList.append(filename)

print 'There are ' + str(len(dataList)) + ' output files.'
dataList.sort()
dataList.remove('log')

fAverage=open('./AverageTotalParsed.txt','r')
fMeanPer=open('./SensTestResults.txt','w')
AverageList=fAverage.readlines()
fAverage.close()

for file in dataList: 
  print 'Parsing ' + file
  fileString=file.split('Out.')
  feq=open('./output/'+file, 'r')
  lineList=feq.readlines()
  feq.close()
  eq=sympy.sympify(lineList[-1].split(':')[0])
  sum=0
  for i in range(len(AverageList)):
    var=AverageList[i].rstrip().split(' ')
    result=eq.subs('x0',var[0]).subs('x1',var[1]).subs('x2',var[2]).subs('x3',var[3]).subs('x4',var[4]).subs('x5',var[5]).subs('x6',var[6]).subs('x7',var[7]).subs('x8',var[8])
    diff=abs(result-float(var[9]))/float(var[9])
    sum=sum+diff
  sum=sum/len(AverageList)
  fMeanPer.write(fileString[0]+' '+str(sum)+';')

fMeanPer.close()

