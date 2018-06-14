#!/bin/bash
##################################################
# Sets up environment and starts standard interactive session
##################################################

# source centos7 setup
source centos7-modules.sh
# load modules
module load gcc/7.1.0-fasrc01 cdo/1.9.4-fasrc02
module load python/2.7.14-fasrc01
# load project environment
source activate analysis_01_06_18

