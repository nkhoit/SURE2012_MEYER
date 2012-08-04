#include <iostream>
using namespace std;

typedef struct{
  float clockFrequency;
  int numCpus;
  int DcacheSize;
  int IcacheSize;
  int L2cacheSize;
  int simdDepth;
  int simdWidth;
  int numSpareCores;
  int numSpareLanes;
  double area;
} configuration;

void calcArea(configuration& config) {
    double base_clock_GHz = 2.6;
    double base_tech = 65;
    double l1area_per_KB = 2.43/64;
    double reg = 0.199358389;
    double alus = 0.513011101;
    double l2area_per_KB = 11.0/1024;
    //the area of 2-way OOO core without caches
    //double OOO_1way_area = 3.207190567/2;
    double IO_skeleton = 1.005347206-reg-alus;
    double tech_node = 65.0;
    
    // derivations
    // OOO_clock_GHz is the frequency, which squares the area
    //OOO_core = OOO_1way_area/base_clock_GHz/base_clock_GHz*OOO_clock_GHz*OOO_clock_GHz;
    //OOO_L1 = (OOO_Icache_KB+OOO_Dcache_KB)*l1area_per_KB;
    ///OOO_L2 = l2area_per_KB*OOO_L2size_KB;
    double OOO_all = 0;//num_OOOs*(OOO_core+OOO_L1)+OOO_L2;
    
    // the area of an IO without caches, ALUs, nor regs
    //IO_core_area = IO_skeleton + IO_SIMD_width*(alus+IO_SIMD_depth*reg);
    double IO_core_alus = (config.simdWidth + config.numSpareLanes)*alus;
    double IO_core_regs = (config.simdWidth + config.numSpareLanes)*config.simdDepth*reg;
    double IO_core_area = IO_skeleton + IO_core_alus + IO_core_regs;
    double IO_scale_factor = 1.0/base_clock_GHz/base_clock_GHz*config.clockFrequency*config.clockFrequency;
    double IO_core = IO_core_area * IO_scale_factor;
    IO_core_alus = IO_core_alus*IO_scale_factor;
    IO_core_regs = IO_core_regs*IO_scale_factor;
    double laneArea = IO_core / (config.simdWidth + config.numSpareLanes); // (alus+depth*reg)*scaleFactor
    double skeletonArea = IO_skeleton*IO_scale_factor;
    double IO_L1 = (config.IcacheSize+config.DcacheSize)*l1area_per_KB;
    double IO_area = IO_core+IO_L1;
    double IO_L2 = config.L2cacheSize*l2area_per_KB;
    double IO_all = IO_area*(config.numCpus + config.numSpareCores) + IO_L2;
    //if(config.doubleSpares)
    //	IO_all += laneArea * config.numCpus/(2+2*QUAD_SPARES); //divide by 4 if spares are for 4 cores versus 2
    double die_area_IO_all = IO_all/base_tech*tech_node;
    double die_area_OOO = OOO_all/base_tech*tech_node;
    double die_area = die_area_IO_all + die_area_OOO;
    config.area = die_area;
    /*
	if(config.numSpareLanes > 0)
		config.area *= LANE_OVERHEAD;
	if(config.numSpareCores > 0)
		config.area *= CORE_OVERHEAD;
	if(config.doubleSpares)
		config.area *= SHARED_OVERHEAD;
	
    calcYield(config, laneArea, 0.0, IO_L1, IO_L2);
    */
}

int main(){
  configuration config={2.0,1,16,16,4096,4,1,0,0,0};
  configuration config2={2.0,20,64,16,4096,1,8,0,0,0};
  calcArea(config);
  calcArea(config2);
  cout << config.area << endl;
  cout << config2.area << endl;
  return 0;

}
