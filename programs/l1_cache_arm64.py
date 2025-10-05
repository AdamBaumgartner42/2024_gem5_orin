import m5
from m5.objects import *
import sys
import os

# ============================================================
#   Parse command-line argument
# ============================================================
if len(sys.argv) != 2:
    print("Usage: gem5 script.py <binary>")
    sys.exit(1)

binary = sys.argv[1]

# ============================================================
#   L1 Cache definitions (no L2, no L3)
# ============================================================

class L1ICache(Cache):
    size = '16kB'
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20

class L1DCache(Cache):
    size = '64kB'
    assoc = 1                       # set to 1 for direct-mapped
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20

# ============================================================
#   System configuration
# ============================================================

system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# CPU
system.cpu = ArmTimingSimpleCPU()

# L1 caches only
system.cpu.icache = L1ICache()
system.cpu.dcache = L1DCache()
system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.dcache.cpu_side = system.cpu.dcache_port

# Memory bus (connect directly to memory)
system.membus = SystemXBar()
system.cpu.icache.mem_side = system.membus.cpu_side_ports
system.cpu.dcache.mem_side = system.membus.cpu_side_ports

# Interrupts and memory controller
system.cpu.createInterruptController()
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports
system.system_port = system.membus.cpu_side_ports

# ============================================================
#   Workload setup
# ============================================================

try:
    system.workload = SEWorkload.init_compatible(binary)
except:
    system.workload = SEWorkload()

process = Process()
process.cmd = [binary]
process.executable = binary
system.cpu.workload = process
system.cpu.createThreads()

root = Root(full_system=False, system=system)

print(f"L1 ICache size: {system.cpu.icache.size}")
print(f"L1 DCache size: {system.cpu.dcache.size}")
m5.instantiate()

print("\n=== BEGIN SIMULATION ===")
print(f"Running ARM64 binary: {binary}")
print("Configuration: L1 CACHE ONLY (no L2, no L3)\n")

exit_event = m5.simulate()
print(f'Exiting @ tick {m5.curTick()} because {exit_event.getCause()}')
m5.stats.dump()

# ============================================================
#   Cache stats extraction + ratio calculation
# ============================================================

def extract_l1_cache_stats(stats_file="m5out/stats.txt"):
    """Extracts relevant L1 icache/dcache statistics from stats.txt"""
    cache_stats = {}
    try:
        with open(stats_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '::' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        stat_name = parts[0]
                        try:
                            stat_value = float(parts[1])
                        except ValueError:
                            continue

                        if ('system.cpu.icache' in stat_name or
                            'system.cpu.dcache' in stat_name):
                            if any(keyword in stat_name for keyword in
                                   ['overallHits', 'overallMisses', 'overallAccesses',
                                    'demandHits', 'demandMisses', 'demandAccesses']):
                                cache_stats[stat_name] = stat_value
    except FileNotFoundError:
        print("Stats file not found.")
    return cache_stats

def calculate_cache_ratios(cache_stats):
    """Computes hit/miss ratios for icache and dcache"""
    ratios = {}
    cache_types = ['icache', 'dcache']

    for cache_type in cache_types:
        hits = misses = accesses = None

        for stat_name, stat_value in cache_stats.items():
            if cache_type in stat_name:
                if 'Hits' in stat_name:
                    hits = stat_value
                elif 'Misses' in stat_name:
                    misses = stat_value
                elif 'Accesses' in stat_name:
                    accesses = stat_value

        if hits is not None or misses is not None:
            if accesses is None and hits is not None and misses is not None:
                accesses = hits + misses

            if accesses and accesses > 0:
                hit_ratio = (hits / accesses) * 100 if hits else 0
                miss_ratio = (misses / accesses) * 100 if misses else 0
                ratios[f'{cache_type}_hit_ratio'] = hit_ratio
                ratios[f'{cache_type}_miss_ratio'] = miss_ratio
                ratios[f'{cache_type}_hits'] = hits or 0
                ratios[f'{cache_type}_misses'] = misses or 0
                ratios[f'{cache_type}_total_accesses'] = accesses or 0

    return ratios

def extract_hostseconds(stats_file="m5out/stats.txt"):
    try:
        with open(stats_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) >= 2:
                        stat_name = parts[0]
                        try:
                            stat_value = float(parts[1])
                        except ValueError:
                            continue

                        if stat_name.lower() == 'hostseconds':
                            return stat_value

    except FileNotFoundError:
        print("Stats file not found.")
    return -1

# ============================================================
#   Output results
# ============================================================

print("\n=== ARM64 L1 CACHE STATISTICS FROM stats.txt ===")
cache_stats = extract_l1_cache_stats()
elapsedTime = extract_hostseconds()

if cache_stats:
    print("Raw Cache Statistics:")
    print("-" * 70)
    for stat_name, stat_value in sorted(cache_stats.items()):
        print(f"{stat_name}: {stat_value}")

    ratios = calculate_cache_ratios(cache_stats)


    print("\nCalculated Cache Performance Metrics:")
    print("-" * 70)
    print(f"Elapsed Time:             {elapsedTime:.2f} seconds")
    if ratios:
        if 'dcache_hit_ratio' in ratios:
            print(f"L1 D-Cache Hit Ratio:     {ratios['dcache_hit_ratio']:.2f}%")
            print(f"L1 D-Cache Miss Ratio:    {ratios['dcache_miss_ratio']:.2f}%")
            print(f"L1 D-Cache Hits:          {int(ratios['dcache_hits'])}")
            print(f"L1 D-Cache Misses:        {int(ratios['dcache_misses'])}")
            print(f"L1 D-Cache Total Accesses:{int(ratios['dcache_total_accesses'])}")
            print()
    else:
        print("\nCould not calculate hit/miss ratios — insufficient data.")
else:
    print("No L1 cache statistics found.")

print(f"\nTotal simulation ticks: {m5.curTick()}")
print("Full statistics available in: m5out/stats.txt")
