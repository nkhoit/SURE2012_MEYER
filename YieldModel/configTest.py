#!/data/bin/python

import SIMDyield

list=SIMDyield.generateConfigurations()
print '\n'.join(str(n) for n in list)
