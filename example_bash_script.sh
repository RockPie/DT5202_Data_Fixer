#!/bin/bash

for i in {00..05}; do
  echo "Fixing data of data ${i}"
  python DT5202_Data_Fixer.py --input infile_${i}.txt --output outfile${i}.txt >> "log_${i}.txt" 2>&1
done