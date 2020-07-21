#!/bin/bash
#SBATCH --job-name="statemod"
#SBATCH --output="statemodruns.out"
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --export=ALL
#SBATCH -t 1:00:00            # set max wallclock time

module load python/3.6.9
mpirun python3 submit_CMIP_runs.py

