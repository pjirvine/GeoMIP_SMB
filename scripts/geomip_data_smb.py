"""
This python script contains variables and functions that are required to gather up / generate the data
for the fraction better off project.
These functions will mostly be specific to this project.
"""

import numpy as np
import os.path
# import cf
from netCDF4 import Dataset
from scipy.stats import ttest_ind_from_stats

from analysis import *

"""
Model - exp - runs + notes
"""

model_exp_runs = {}
model_exp_runs['BNU-ESM_piControl'] = ['r1i1p1'] # Issue! G1 r1 to be converted to r2
model_exp_runs['CanESM2_piControl'] = ['r1i1p1']
model_exp_runs['CCSM4_piControl'] = ['r2i1p1','r4i1p1'] # Issue! Waiting on separate to do
model_exp_runs['CESM-CAM5.1-FV_piControl'] = ['r1i1p1']
model_exp_runs['CSIRO-Mk3L-1-2_piControl'] = ['r1i1p1']
model_exp_runs['EC-EARTH_piControl'] = ['r1i1p1'] 
model_exp_runs['GISS-E2-R_piControl'] = ['r2i1p1','r1i1p1','r3i1p1','r1i1p2','r1i1p2'] # Issue! parts 2 and 3 in picontrol?
model_exp_runs['HadCM3_piControl'] = ['r1i1p1']
model_exp_runs['HadGEM2-ES_piControl'] = ['r1i1p1']
model_exp_runs['IPSL-CM5A-LR_piControl'] = ['r1i1p1']
model_exp_runs['MIROC-ESM_piControl'] = ['r1i1p1']
model_exp_runs['MPI-ESM-LR_piControl'] = ['r1i1p1']
model_exp_runs['NorESM1-M_piControl'] = ['r1i1p1']

model_exp_runs['BNU-ESM_abrupt4xCO2'] = ['r1i1p1'] # Issue! G1 r1 to be converted to r2
model_exp_runs['CanESM2_abrupt4xCO2'] = ['r1i1p1']
model_exp_runs['CCSM4_abrupt4xCO2'] = ['r1i1p1','r3i1p1'] # Issue! Waiting on separate to do
model_exp_runs['CESM-CAM5.1-FV_abrupt4xCO2'] = ['r1i1p1','r3i1p1']
model_exp_runs['CSIRO-Mk3L-1-2_abrupt4xCO2'] = ['r1i1p1','r2i1p1','r3i1p1']
model_exp_runs['EC-EARTH_abrupt4xCO2'] = ['r1i1p1'] 
model_exp_runs['GISS-E2-R_abrupt4xCO2'] = ['r2i1p1','r1i1p1','r3i1p1'] # Issue! parts 2 and 3 in picontrol?
model_exp_runs['HadCM3_abrupt4xCO2'] = ['r1i1p1','r2i1p1','r3i1p1']
model_exp_runs['HadGEM2-ES_abrupt4xCO2'] = ['r1i1p1']
model_exp_runs['IPSL-CM5A-LR_abrupt4xCO2'] = ['r1i1p1']
model_exp_runs['MIROC-ESM_abrupt4xCO2'] = ['r1i1p1']
model_exp_runs['MPI-ESM-LR_abrupt4xCO2'] = ['r1i1p1']
model_exp_runs['NorESM1-M_abrupt4xCO2'] = ['r1i1p1']

model_exp_runs['BNU-ESM_G1'] = ['r2i1p1','r1i1p1'] # Issue! G1 r1 to be converted to r2
model_exp_runs['CanESM2_G1'] = ['r1i1p1','r2i1p1','r3i1p1']
model_exp_runs['CCSM4_G1'] = ['r1i1p1','r2i1p1'] # Issue! Waiting on separate to do
model_exp_runs['CESM-CAM5.1-FV_G1'] = ['r1i1p1']
model_exp_runs['CSIRO-Mk3L-1-2_G1'] = ['r1i1p1','r2i1p1','r3i1p1']
model_exp_runs['EC-EARTH_G1'] = ['r1i1p1'] 
model_exp_runs['GISS-E2-R_G1'] = ['r2i1p1','r1i1p1','r3i1p1'] # Issue! parts 2 and 3 in picontrol?
model_exp_runs['HadCM3_G1'] = ['r1i1p1','r2i1p1','r3i1p1']
model_exp_runs['HadGEM2-ES_G1'] = ['r1i1p1']
model_exp_runs['IPSL-CM5A-LR_G1'] = ['r1i1p1']
model_exp_runs['MIROC-ESM_G1'] = ['r1i1p1']
model_exp_runs['MPI-ESM-LR_G1'] = ['r2i1p1']
model_exp_runs['NorESM1-M_G1'] = ['r1i1p1']

"""
###
Get GeoMIP Masks
###
"""

def get_masks_weights(model_in, variable=""): 
    
    """
    This function gathers up all the masks and weights listed below and returns them.
    
    If variable is Not None:
        It checks if the variable is an extreme and if so uses the NorESM1-M grid as
        all extreme variables are on this grid.
        
    If no original resolution ice is available the regridded NorESM1-M ice is used instead.
    
    Return:
        All masks, etc. are from 0 - 100% in input files but all are output as 0-1
        All weights total to 1 on output.
    """
    
    if "ETCCDI" in variable: # Use NorESM1-M if  variable is an extreme one
        model = "NorESM1-M"
    else:
        model = model_in
    
    # Define directory format
    in_dir_base = "/n/home03/pjirvine/keithfs1_pji/geomip_archive/final_data/{model}/fix/"
    in_dir = in_dir_base.format(model = model)

    # Define file names for land and ice
    nc_file_base = "{fx_type}_{model}{append}.nc"
    land_file = nc_file_base.format(model = model, fx_type = 'sftlf', append='')
        
    # Check if land file is present
    if not os.path.isfile(in_dir+land_file):
        return "No land mask file"
    
    # Load numpy array from land file
    land = Dataset(in_dir + land_file).variables['sftlf'][:]
    
    # Load land-noice file
    land_noice_file = "{model}_land_no_gr_ant.nc".format(model = model)
    # Load numpy array
    land_noice = Dataset(in_dir + land_noice_file).variables['sftlf'][:]
    
    greenland_file = "{model}_Gr_land.nc".format(model = model)
    greenland = Dataset(in_dir + greenland_file).variables['sftlf'][:]
    
    antarctica_file = "{model}_Ant_land.nc".format(model = model)
    antarctica = Dataset(in_dir + antarctica_file).variables['sftlf'][:]
    
    """
    Get weights
    """
    
    # calculate grid_weights
    # Check if gridweights file is present (this is needed as some mask files don't contain gridweights)
    # and calculated if not.
    if os.path.isfile(in_dir+'gridweights.nc'):
        grid_weights = Dataset(in_dir + 'gridweights.nc').variables['cell_weights'][:]
    else:
        grid_weights = cdo.gridweights(input=in_dir+land_file, returnArray  =  'cell_weights')
    
    # Check if population weighting is there
    pop_loc = in_dir+'{model}_pop.nc'.format(model=model)
    if os.path.isfile(pop_loc):
        pop = Dataset(pop_loc).variables['pop'][:]
        pop_weights = pop / np.sum(pop)
    else:
        return "no pop file"
    
    # Check if agriculture weighting is there
    ag_loc = in_dir+'{model}_agriculture.nc'.format(model=model)
    if os.path.isfile(ag_loc):
        ag = Dataset(ag_loc).variables['fraction'][:]
        ag_weights = ag / np.sum(ag)
    else:
        return "no ag file"
    
    """
    Prepare output dicts
    """
    
    lons_lats = {}
    masks = {}
    weights = {}
    
    """
    Output to dicts
    """
    
    # Use land file to gather lons and lats
    lons_lats['lons'] = Dataset(in_dir + land_file).variables['lon'][:]
    lons_lats['lats'] = Dataset(in_dir + land_file).variables['lat'][:]

    """
    Output masks
    """
    
    masks['global'] = np.ones_like(land)
    masks['land'] = 0.01 * land # convert 0-100 to 0-1
    masks['ocean'] = 1.0 - masks['land']
    masks['land_noice'] = 0.01 * land_noice
    masks['greenland'] = 0.01 * greenland
    masks['antarctica'] = 0.01 * antarctica
    
    """
    Output weights
    """
    
    # define function to calculate normalized mask weighting
    def weighted_mask(mask, weight):
        weighted_mask = mask * weight
        return weighted_mask / np.sum(weighted_mask)
    
    # Output weights all sum to 1
    weights['pop'] = pop_weights
    
    weights['ag'] = ag_weights
    
    weights['global_area'] = grid_weights
    weights['land_area'] = weighted_mask(masks['land'],grid_weights)
    weights['ocean_area'] = weighted_mask(masks['ocean'],grid_weights)
    weights['land_noice_area'] = weighted_mask(masks['land_noice'],grid_weights)
    weights['greenland_area'] = weighted_mask(masks['greenland'],grid_weights)
    weights['antarctica_area'] = weighted_mask(masks['antarctica'],grid_weights)
    
    # Except pop_count
    weights['pop_count'] = pop
    
    return lons_lats, masks, weights


"""
###
Get GeoMIP Data
###
"""

# This function retrieves the desired netcdf file.
def get_2d_geomip(var, model, exp, run, seas, stat,
                    time='11-50', lon_lat=False, lat_name='latitude', lon_name='longitude'):

    """
    Returns array of netcdf file along with latitude and longitude if option selected.
    (data.array [, lat.array, lon.array])
    """
    # Define nc_file format
    nc_file_base = "{var}_{model}_{exp}_{run}_{time}_{seas}_{stat}.nc"
    nc_file = nc_file_base.format(var=var, model=model, exp=exp, run=run, time=time, seas=seas, stat=stat)

    # Define directory format
    in_dir_base = "/n/home03/pjirvine/keithfs1_pji/geomip_archive/final_data/{model}/{exp}/time{stat}/"
    in_dir = in_dir_base.format(model=model, exp=exp, stat=stat)

    file_loc = in_dir + nc_file

    if os.path.isfile(file_loc):
        f = cf.read(file_loc)
        if lon_lat:
            return (f.array, f.dim(lat_name).array, f.dim(lon_name).array)
        else:
            return f.array
    else:
        return None

