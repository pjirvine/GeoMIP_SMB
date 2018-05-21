"""
GeoMIP global means all models
"""

glbl_geomip_all = {}

mask_list = ['global_area','land_noice_area', 'pop']
exp_list = ['piControl','abrupt4xCO2','G1','G_frac']

var_dict = {} # Create a dictionary for each parameter then loop
for var in var_list:
            
    mask_dict = {}
    for mask in mask_list:
        
        exp_dict = {}
        for exp in exp_list:
            
            model_dict = {}
            for model in model_list:
                
                if all_data[model][var] is None:
                    model_dict[model] = None
                else:
                    model_dict[model] = np.sum( all_data[model][var][exp] * all_data[model][var][mask] )
                
                # cascade down the dicts storing higher level dict
            exp_dict[exp] = model_dict
        mask_dict[mask] = exp_dict
    var_dict[var] = mask_dict
# End loops

glbl_geomip_all = var_dict

"""
Global mean anomalies - median, min, max
"""

# This Calculates the median, mean, min and max over the GeoMIP ensemble for a given inner function and inner args
def med_min_max(inner_func, inner_args):
    
    # inner_func must read MODEL first then other args.
    # results for each model are calculated and output to an array
    model_results = [inner_func(model, *inner_args) for model in model_list]
    model_array = np.array(model_results)
    
    # The median, min and max of the model results array are returned as a list 
    return [np.nanmedian(model_array), np.nanmean(model_array), np.nanmin(model_array), np.nanmax(model_array)]

def exp_anom(model, exp_1, exp_2, var, weight):
    mean_1 = glbl_geomip_all[var][weight][exp_1][model]
    mean_2 = glbl_geomip_all[var][weight][exp_2][model]
    # don't calculate anything if None type present
    if (mean_1 is None) or (mean_2 is None):
        return np.nan
    else:
        return mean_1 - mean_2

# Loop over all vars

var_dict = {}
for var in var_list:
    
    temp_dict = {}

    # calculate global anoms
    # Inner args are EXP_1, EXP_2, VAR, WEIGHT
    temp_dict['CO2-ctrl_global'] = med_min_max(exp_anom, ['abrupt4xCO2','piControl',var,'global_area']) # exp_anom and inner
    temp_dict['G1-ctrl_global'] = med_min_max(exp_anom, ['G1','piControl',var,'global_area']) # exp_anom and inner
    temp_dict['G0.5-ctrl_global'] = med_min_max(exp_anom, ['G_frac','piControl',var,'global_area']) # exp_anom and inner

    # calculate land noice anoms
    temp_dict['CO2-ctrl_land_noice'] = med_min_max(exp_anom, ['abrupt4xCO2','piControl',var,'land_noice_area']) # exp_anom and inner
    temp_dict['G1-ctrl_land_noice'] = med_min_max(exp_anom, ['G1','piControl',var,'land_noice_area']) # exp_anom and inner
    temp_dict['G0.5-ctrl_land_noice'] = med_min_max(exp_anom, ['G_frac','piControl',var,'land_noice_area']) # exp_anom and inner

    var_dict[var] = temp_dict

glbl_geomip_anoms = var_dict

# Output to table
glbl_out = pd.DataFrame.from_dict(glbl_geomip_anoms).to_csv(table_dir+'geomip_glbl_anoms.csv')