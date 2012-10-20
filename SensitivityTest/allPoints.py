#!/data/bin/python

cores=[1,2,4,6,8,10,12,14,16,18,20]
DCache=[8,16,32,64]
SIMD=[(1,1),(1,2),(1,4),(1,8),(1,16),(1,32),(1,64),(2,2),(2,4),(2,8),(2,16),(2,32),(2,64),(4,4),(4,8),(4,16),(4,32),(4,64),(8,8),(8,16),(8,32),(8,64),(16,16),(16,32),(16,64),(32,32),(32,64),(64,64)]
counter=0

for i in range(len(cores)):
  for j in range(len(DCache)):
    for k in range(len(SIMD)):
      print str(i) + ' ' + str(j) + ' ' + str(k)
      counter+=1

print str(counter) + ' points'

