#!/bin/bash
##################################################
# Sets up environment and starts standard interactive session
##################################################

# load project environment
. ~/apps/bin/module_load_17_05_17
# 10 hour interactive session
srun -p test --tunnel=8200:8200 --pty --mem 3000 -t 0-08:00 /bin/bash
# open jupyter notebook in projects folder
cd ~/projects
