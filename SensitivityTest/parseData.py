#!/data/bin/python
import sys
import fileinput
import csv

Fout = open('raw/ShortestParsed.csv','w')
numLines = 200

rawCSV = csv.reader(open('raw/ShortestPath.csv'), delimiter=',')
listCSV=list(rawCSV)
#skipVal = int(len(listCSV)/numLines) 
skipVal = 1

for i,line in enumerate(listCSV):
  if(line[0]!='1.79769e+308' and i%skipVal==0):
    parsedLine = ' '.join(str(j) for j in line[1].split(','))+' '+line[2]+'\n'
    #print parsedLine,
    Fout.write(parsedLine)

Fout.close()

