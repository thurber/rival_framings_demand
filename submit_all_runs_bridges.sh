#!/bin/bash

start_vals=($(seq 1 50 551))
end_vals=($(seq 50 50 600))
batches=($(seq 1 5))

for i in "${batches[@]}"; do
  sbatch --job-name=batch_$i \
  --output=./outputs/batch_$i].out \
  --error=./errors/batch_$i.err \
  curtailment_scaling_bridges.sh ${start_vals[$i]} ${end_vals[$i]} $i
  sleep 0.5
done