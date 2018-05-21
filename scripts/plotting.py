"""
This python script contains plotting functions used in the fraction better off project
These functions should be mostly of general use
"""

"""
IMPORT MODULES
"""

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as colors
import matplotlib.cm as cmx
from matplotlib.colors import LogNorm

from analysis import *

"""
LT_GT_LABELS
"""

def lt_gt_labels(values):

    """
    Returns a list of labels lt / gt the values given
    """

    first_label = ['< '+str(values[0])]
    last_label = ['> '+str(values[-1])]
    if len(values) > 1:
        mid_labels = [str(Y)+' > '+str(X) for X,Y in zip(values[1:],values[:-1])]
    else:
        mid_labels = []
    all_labels = first_label + mid_labels + last_label

    return all_labels

"""
PLOT_PICK

This routine passes arguments to the selected plotting function
"""

def plot_pick(ax_num, plot_type, plot_args, plot_kwargs):
    
    # If any of the plot_args are missing (e.g. data!) then only print title
    if any(i is None for i in plot_args):
        ax_num.set_title(plot_kwargs['title'])
        out = None
    else:
        if plot_type == 'core_histogram':
            out = core_histogram(ax_num, *plot_args, **plot_kwargs)    
        elif plot_type == 'residual_blob_plot':
            out = residual_blob_plot(ax_num, *plot_args, **plot_kwargs)
        elif plot_type == 'res_distribution_plot':
            out = res_distribution_plot(ax_num, *plot_args, **plot_kwargs)
        elif plot_type == 'core_2d_histogram':
            out = core_2d_histogram(ax_num, *plot_args, **plot_kwargs)
        elif plot_type == 'hist_wrap':
            out = hist_wrap(ax_num, *plot_args, **plot_kwargs)
        elif plot_type == 'hist2d_wrap':
            out = hist2d_wrap(ax_num, *plot_args, **plot_kwargs)
    return out
            
"""
MULTI_PLOT

This function takes a list of inputs for sub_plots and bundles them together into one regular figure.
"""

def multi_plot(sub_plot_list, num_cols = None, sharex = True, sharey = True,
               out_file = None, plot_format='png', dpi=480, show = True): # plot options
    
    """
    Set up figure structure
    """
    
    # round down square root of sub plot num for num cols
    if num_cols is None:
        num_cols = int(np.sqrt(len(sub_plot_list)))

    # make sure number of rows is sufficient
    num_rows = len(sub_plot_list) / num_cols
    if num_rows*num_cols < len(sub_plot_list):
        num_rows += 1
    
    if num_rows - num_cols > 1:
        num_cols += 1
        num_rows -= 1
    
    # Generate the figure and sub_plots and output to list
    f, axes = plt.subplots(num_rows, num_cols, sharex=sharex, sharey=sharey)
    if isinstance(axes, np.ndarray):
        ax_list = axes.flatten()
    else:
        ax_list = np.array([axes])

    # Set common variables
    plt.rcParams.update({'font.size': 16})
    if num_rows > num_cols:
        f.set_size_inches(8.5, 11)
    else:
        f.set_size_inches(8.5, 8.5)
        
    """
    Generate the sub-plots, looping through sub_plot_list:
    """
    
    for idx in xrange(len(sub_plot_list)):
        #         if sub_plot_list[idx][0] is not None: # Check to see if there is input data
        out = plot_pick(ax_list[idx], *sub_plot_list[idx])
    
    ### WARNING #### This only applies for core_2d_histogram. will need rewriting if expanded.
    if out is not None:
        f.subplots_adjust(right=0.85)
        cax = f.add_axes([0.9,0.1,0.03,0.8])
        cbar = f.colorbar(out, cax=cax)
    
    if out_file is not None:
       # Save figure to file:
        plt.savefig(out_file+'.'+plot_format, format=plot_format, dpi=dpi)
        
    if show:
        plt.show()

"""
HIST_WRAP produces the standard histogram plots but in a more general way
"""

def hist_wrap(plot_id, hist_args, hist_kwargs, title='', xlabel=None, ylabel=None, plot_axis=None):

    """
    hist args = data
    For hist kwargs see:
    https://matplotlib.org/devdocs/api/_as_gen/matplotlib.pyplot.hist.html
    
    axis = [xmin, xmax, ymin, ymax]
    """
    
    """
    Label plot
    """
    
    plot_id.set_title(title)
    plot_id.set_xlabel(xlabel)
    plot_id.set_ylabel(ylabel)
    
    """
    Set limits on axis
    """
    
    if plot_axis is not None:
        plot_id.axis(plot_axis)
        # Set histogram range to match    
        hist_kwargs['range']=[plot_axis[0],plot_axis[1]]
    
    """
    Produce the plot
    """
    
    plot_return = plot_id.hist(*hist_args, **hist_kwargs)
    
        
"""
CORE_HISTOGRAM produces the standard histogram plots
"""

def core_histogram(plot_id, data, weight=None, ttest=None, # data input
                   num = 50, color='k', histtype='stepfilled', axes=None, # basic plot options
                   quant_lines=False, quant_values = [0.05, 0.5, 0.95], quant_col= 'r', # quant line options
                   dist_text = False, dist_values = [0], # Distribution text options
                   title = None, ttest_leg = True, leg_font_size = None):  # plot labeling options

    
    """
    This function produces the standard histogram plots.
    """
    
    """
    Setup basic plot items
    """
    
    plot_id.set_title(title)
    leg_items = [] # list of items for legend
    
    if axes is not None:
        plot_id.axis(axes)
        x_range = (axes[0], axes[1])
        y_range = (axes[2], axes[3])
    else:
        x_range = None 
    
    """
    Apply t-test
    ALTERNATIVE - AS FUNCTION?
    """
    
    if ttest is not None:
        old_weight = np.copy(weight)
        # Apply t-test to weight
        weight = weight * ttest 
        # Fraction which fail the T-test
        ttest_fail = 1.0 - (np.sum(weight) / np.sum(old_weight))
        # Create legend item for T-test
        legend_ttest = mpatches.Patch(label='T-test: '+"{:3.1f}".format(100*ttest_fail)+'%')
        leg_items.append(legend_ttest)
    
    """
    Produce the plot
    """
    
    plot_return = plot_id.hist(data, num, weights=weight, normed=True, histtype=histtype, color=color, range=x_range)
    
    """
    Quantile lines
    ALTERNATIVE - AS FUNCTION?
    """
    
    if quant_lines and axes is not None: # Need to define 
        quantiles = weighted_quantile(data, quant_values, sample_weight = weight)
        plot_id.vlines(quantiles, y_range[0], y_range[1], color=quant_col, linewidth=2.0)
    
    """
    Distribution text
    """    
    
    if dist_text:
        
        distribution = fraction_distribution(data, dist_values, sample_weight=weight)

        for idx in xrange(len(distribution)):
            if idx == 0: # Label string for first result
                label_temp = '< ' + str(dist_values[idx]) + '    = ' + "{:3.1f}".format(100*distribution[idx])+'%'
            elif idx == len(dist_values): # Label string for last result
                label_temp = '> ' + str(dist_values[idx-1])+'    = '+"{:3.1f}".format(100*distribution[idx])+'%'
            else: # Label string for all other results
                label_temp = str(dist_values[idx-1]) + ' > ' + str(dist_values[idx])+' = '+"{:3.1f}".format(100*distribution[idx])+'%'
            legend_dist_temp = mpatches.Patch(label=label_temp)
            leg_items.append(legend_dist_temp)
    
    """
    Add the legend
    """
    
    if len(leg_items) > 0:
        leg = plot_id.legend(handles=leg_items, handlelength=0, handletextpad=0, fontsize=leg_font_size)
        plot_id.legend(prop={'size':leg_font_size}) # Set legend text size
        # Only show the label and not the tag
        for item in leg.legendHandles:
            item.set_visible(False)
            
    """
    Return
    """
    
    return None

"""
HIST2D_WRAP
"""

def hist2d_wrap(plot_id, hist2d_args, hist2d_kwargs, title='', xlabel='X', ylabel='Y', plot_axis=None,
               zero_lines = True, one_line = False, neg_one_line = False):

    """
    hist2d args = data_x, data_y
    For hist2d kwargs see:
    https://matplotlib.org/api/pyplot_api.html?highlight=matplotlib%20pyplot%20hist#matplotlib.pyplot.hist2d
    
    axis = [xmin, xmax, ymin, ymax]
    """
    
    """
    Label plot
    """
    
    plot_id.set_title(title)
    plot_id.set_xlabel(xlabel)
    plot_id.set_ylabel(ylabel)
    
    """
    Produce the plot
    """
    
    axes_image = plot_id.hist2d(*hist2d_args, **hist2d_kwargs)
    
    """
    Set limits on axis
    """
    
    if plot_axis is not None:
        plot_id.axis(plot_axis)
    
    """
    Add lines
    """
    
    if zero_lines:
        plot_id.axvline(0, color='k')
        plot_id.axhline(0, color='k')
    
    ax_max = max( max(plot_id.get_xlim()), max(plot_id.get_ylim()) )
    ax_min = min( min(plot_id.get_xlim()), min(plot_id.get_ylim()) )
    if one_line:
        plot_id.plot([ax_min, ax_max],[ax_min,ax_max], color='k')
    if neg_one_line and (ax_min < 0):
        plot_id.plot([ax_min, -1.0 * ax_min],[-1.0 * ax_min, ax_min], color='k')
    
    # returns image but not details to prompt edit to fit in colorbar
    return axes_image[3]

"""
CORE_2D_HISTOGRAM

This function plots 2D histograms.
"""

def core_2d_histogram(plot_id, data_x, data_y, title=None, nbins = 40, weight = None, ttest = None, absolute = False, xy_range=None,
                      col_range=None, cell_count=False):
    
    # set title
    plot_id.set_title(title)
    
    # take absolute of input data
    if absolute:
        data_x = abs(data_x)
        data_y = abs(data_y)
    
    # Screen out data that is masked out (value = 0.0)
    if weight is not None:
        data_x = data_x[weight > 0.0]
        data_y = data_y[weight > 0.0]
        if ttest is not None:
            ttest = ttest[weight > 0.0]
        weight = weight[weight > 0.0] # Reduce weight last
    
    # Screen out data that fails ttest
    if ttest is not None:
        data_x = data_x[ttest]
        data_y = data_y[ttest]
        if weight is not None:
            weight = weight[ttest]
     
    # Set plot range
    if xy_range is not None:
        plot_range = ((xy_range[0],xy_range[1]),(xy_range[0],xy_range[1]))
        if absolute:
            plot_range = ((0,xy_range[1]),(0,xy_range[1]))
    else:
        plot_range = None
    
    if col_range is not None:
        col_min, col_max = col_range
    else:
        col_min, col_max = None, None
        
    # apply weighting and normalize if normal weighted plot is being produced, else produce plot of count of gridcells
    if cell_count or (weight is None):
        axes_image = plot_id.hist2d(data_x, data_y, bins=nbins, range=plot_range, norm=LogNorm(), cmin = col_min, cmax = col_max)
    else:
        axes_image = plot_id.hist2d(data_x, data_y, bins=nbins, range=plot_range, norm=LogNorm(), cmin = col_min, cmax = col_max,
                                    weights=weight, normed=True)
    
    # Set max and min for colorbar range.
    if col_min is not None:
        axes_image[3].set_clim(vmin=col_min, vmax=col_max)
    
    # Plot guide lines on plot:
    if not absolute:
        plot_id.axvline(0, color='k')
        plot_id.axhline(0, color='k')
        
    if xy_range is not None:
        plot_id.plot(plot_range[0], plot_range[1], color='k')
        if not absolute:
            plot_id.plot(plot_range[0], (plot_range[1][1],plot_range[1][0]), color='k')
        
    return axes_image[3] # returns image but not details

"""
RESIDUAL_BLOB_PLOT

produces a plot which shows the distribution of the absolute residual metric as a function of the level of cooling. 
"""

def residual_blob_plot(plot_id, piControl, abrupt4xCO2, G1, weight=None, ttest=None, frac_limit=1.0, value_step=0.1, value_step_num=20, title=None):

    """
    Set up basic plot stuff
    """
    plot_id.set_title(title)
    leg_items = []
    
    # Calculate fractions
    frac_number = int(frac_limit * 100) + 1
    CO2_effect = abrupt4xCO2 - piControl
    fraction_geo = [float(X)*0.01 for X in xrange(frac_number)]
    G_frac_list = [abrupt4xCO2 + float(X)*0.01*(G1 - abrupt4xCO2) for X in xrange(frac_number)]
    G_frac_anom_list = [X - piControl for X in G_frac_list]
    G_frac_res_list = [X / CO2_effect for X in G_frac_anom_list]
    
    if ttest is not None:
        old_weight = np.copy(weight)
        # Apply t-test to weight
        weight = weight * ttest 
        # Fraction which fail the T-test
        ttest_fail = 1.0 - (np.sum(weight) / np.sum(old_weight))
        # Create legend item for T-test
        legend_ttest = mpatches.Patch(label='T-test: '+"{:3.1f}".format(100*ttest_fail)+'%')
        leg_items.append(legend_ttest)
    
    # Calculate values and distribution at these values
    values = [value_step*X for X in xrange(value_step_num+1)]
    
    fraction_list = [fraction_distribution(abs(X), values, cumulative=True, sample_weight=weight) for X in G_frac_res_list]
    fraction_array = np.array(fraction_list)
    
    # Up until 1 (no effect) Green is used.
    Greens = plt.get_cmap('Greens_r') 
    Green_Norm  = colors.Normalize(vmin=0, vmax=1)
    Green_scalarMap = cmx.ScalarMappable(norm=Green_Norm, cmap=Greens)

    # beyond 1 Red is used
    Reds = plt.get_cmap('Reds') 
    Red_Norm  = colors.Normalize(vmin=0, vmax=1)
    Red_scalarMap = cmx.ScalarMappable(norm=Red_Norm, cmap=Reds)

    #plt.plot(fraction_geo, fraction_array[:,0], color='b')
    #plt.plot(fraction_geo, fraction_array[:,0], color='r')
    half_step_num = int(0.5*value_step_num)
    for i in xrange(half_step_num + 1):
        colorVal = Green_scalarMap.to_rgba(values[i])
        plot_id.fill_between(fraction_geo[1:], fraction_array[1:,i], fraction_array[1:,i-1], color=colorVal)
    for i in xrange(half_step_num + 1):
        colorVal = Red_scalarMap.to_rgba(values[i])
        plot_id.fill_between(fraction_geo[1:], fraction_array[1:,i+1+half_step_num], 
                         fraction_array[1:,i+half_step_num], color=colorVal)
    
    plot_id.plot(fraction_geo[1:], fraction_array[1:,half_step_num], color='k', linewidth=2)    
    plot_id.axis([0,frac_limit,0,1])
                
    """
    Return
    """
    
    return None

"""
RESIDUAL_LINE_PLOT

Shows the distribution of the residauls as a function of the level of geoengineering
"""

def res_distribution_plot(plot_id, piControl, abrupt4xCO2, G1, line_quants, weight=None, ttest=None, quant_heavy=[0.05,0.25,0.5,0.75,0.95], plot_heavy=True, line_thick=1, frac_limit=1.0, y_limit=2.0, title=None):

    """
    This plots a line for each quantile given to it as a function of the level of geoengineering.
    """
    
    if (max(line_quants) > 1) or (min(line_quants) < 0):
        return "line_quants off: ", max(line_quants), min(line_quants)
    
    """
    Set up basic plot stuff
    """
    plot_id.set_title(title)
    leg_items = []
    
    # Calculate fractions
    frac_number = int(frac_limit * 100) + 1
    CO2_effect = abrupt4xCO2 - piControl
    fraction_geo = [float(X)*0.01 for X in xrange(frac_number)]
    G_frac_list = [abrupt4xCO2 + float(X)*0.01*(G1 - abrupt4xCO2) for X in xrange(frac_number)]
    G_frac_anom_list = [X - piControl for X in G_frac_list]
    G_frac_res_list = [X / CO2_effect for X in G_frac_anom_list]
    
    if ttest is not None:
        old_weight = np.copy(weight)
        # Apply t-test to weight
        weight = weight * ttest 
        # Fraction which fail the T-test
        ttest_fail = 1.0 - (np.sum(weight) / np.sum(old_weight))
        # Create legend item for T-test
        legend_ttest = mpatches.Patch(label='T-test: '+"{:3.1f}".format(100*ttest_fail)+'%')
        leg_items.append(legend_ttest)
    
    quant_list = [weighted_quantile(abs(X), line_quants, sample_weight=weight) for X in G_frac_res_list]
    quant_array = np.array(quant_list)
    
    #
    line_cols = plt.get_cmap('viridis') 
    line_cols_Norm  = colors.Normalize(vmin=0, vmax=1)
    line_cols_scalarMap = cmx.ScalarMappable(norm=line_cols_Norm, cmap=line_cols)
    
    # Plot regular lines:
    for idx in xrange(len(line_quants)):
        colorVal = line_cols_scalarMap.to_rgba(line_quants[idx])
        plot_id.plot(fraction_geo,quant_array[:,idx], linewidth=1.5*line_thick, color=colorVal)

    # Plot heavy lines:
    if plot_heavy:
        quant_heavy_list = [weighted_quantile(abs(X), quant_heavy, sample_weight=weight) for X in G_frac_res_list]
        quant_heavy_array = np.array(quant_heavy_list)
        
        for idx in xrange(len(quant_heavy)):
            colorVal = line_cols_scalarMap.to_rgba(quant_heavy[idx])
            plot_id.plot(fraction_geo,quant_heavy_array[:,idx], linewidth=2*line_thick, color='k')
        
    plot_id.axhline(1.0, linewidth=2*line_thick, color='k')
    
    plot_id.axis([0,frac_limit,0,y_limit])
                
    """
    Return
    """
    
    return None
