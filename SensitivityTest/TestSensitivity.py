import subprocess
import os
import fileinput

dataList=[]

def change_header(file,number):
  for line in fileinput.input(file, inplace=1):
    if '#define NUM_FULL_SIM_DESIGN_POINTS' in line:
      print '#define NUM_FULL_SIM_DESIGN_POINTS '+number
    else:
      print line,
  fileinput.close()
  print 'Changed GP Header for ' + number + ' data points'

for filename in os.listdir('/data/ktran12/SURE2012_Meyer/sensitivity_test/data'):
  dataList.append(filename)

print 'There are ' + str(len(dataList)) + ' data files.'
dataList.sort()
for file in dataList:
  print file+',',
print ''

for file in dataList: 
  fileString=file.split('.')
  fout=open('/data/ktran12/SURE2012_Meyer/sensitivity_test/output/log/'+fileString[0]+'.log', 'w')
  change_header('/data/ktran12/GPRSkit-0.2/gprscreate/include/GPparams.h', fileString[0])

  print 'make clean'
  subprocess.call('make clean -C /data/ktran12/GPRSkit-0.2/gprscreate', shell=True)
  print 'make'
  subprocess.call('make -C /data/ktran12/GPRSkit-0.2/gprscreate', shell=True)

  gprsCommand='time /data/ktran12/GPRSkit-0.2/gprscreate/gprscreate /data/ktran12/SURE2012_Meyer/sensitivity_test/data/'+file+' /data/ktran12/SURE2012_Meyer/sensitivity_test/output/'+fileString[0]+'Out.'+fileString[1]
  print gprsCommand
  p = subprocess.call(gprsCommand, shell=True, stdout=fout)

  print 'Finished running ' + file
  fout.close()

print 'Done with everything!'

