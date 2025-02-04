#!/bin/bash

#SBATCH --nodes=20
#SBATCH --ntasks-per-node=5
#SBATCH -t 30:00:00
#SBATCH --export=ALL
#SBATCH --exclusive
#SBATCH --mail-user=ah986@cornell.edu
#SBATCH --mail-type=ALL

source /home/fs02/pmr82_0001/ah986/rival_framings/bin/activate
mpirun python3 data_extraction.py