# Version Control Note
When on Jetson Orin Nano, standard version control works as expected

# Step 0
1. Navigate to /workspaces/intro-to-gem5-AdamBaumgartner42/programs


# Simulating ARM
1. Compile pi_arm
aarch64-linux-gnu-gcc -O2 -static -o pi_arm64 compute_pi.c
aarch64-linux-gnu-gcc -O2 -static -o whetstone_arm64 whetstone.c -lm

2. Run gem5 simulation, time: < 10 seconds
gem5 l1_l2_l3_cache_arm64.py pi_arm64


# Simulating x86
1. Compile pi_x86
x86_64-linux-gnu-gcc -O2 -static -o pi_x86 compute_pi.c

## Requirement for x86 whetstone - use github x86 codespace
x86_64-linux-gnu-gcc -O2 -static -o whetstone_x86 whetstone.c -lm

2. Run gem5 simulation, time: < 10 seconds
gem5 l1_l2_l3_cache_x86.py pi_x86


# --- Reference ---

# Simulating RISCV
1. Compile pi_riscv
riscv64-linux-gnu-gcc -O2 -static -o pi_riscv compute_pi.c

2. Run gem5 simulation, time: < 10 seconds
gem5 l1_cache_riscv.py pi_riscv
