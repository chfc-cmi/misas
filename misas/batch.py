# AUTOGENERATED! DO NOT EDIT! File to edit: 08_batch_mode.ipynb (unless otherwise specified).

__all__ = ['batch_results', 'plot_avg_and_dots', 'plot_avg_and_errorbars', 'plot_boxplot', 'plot_batch']

# Internal Cell
import os
import pandas as pd
from .core import *
from .mri import *
import altair as alt
from tqdm.notebook import tqdm
from tempfile import mkdtemp
from functools import partial

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from shutil import rmtree

# Internal Cell
def dicom_to_Image(fname):
    ds = dcmread(fname)
    img = (ds.pixel_array.astype(np.int16))
    img = (img/img.max()*255).astype(np.uint8)
    img = Image.fromarray(np.array(img))
    return img.convert("RGB")

# Cell
def batch_results(images, model, eval_functions, true_masks=None, components=['bg','LV','MY','RV']):
    ''' Evaluation of the models performance across multiple images and transformations

    -images (list): paths for dicom files with which the model should be evaluated
    -model: model to be evaluated
    -eval_functions (dictionary): keys: name of transformation, values: eval functions from misas.core
    -true_masks (list, optional): paths of png files with true masks for dicoms in 'images' in the same order as 'images'
    -components (list, optional): classes that will be evaluated by the eval functions

    Returns: list of Pandas dataFrames, that contains one dataFrame for each image with the columns: 'parameter', 'bg', 'LV', 'MY', 'RV', 'File'
    '''
    results = []
    for number, x in enumerate(tqdm(eval_functions, leave=False)):
        trfm_result = []
        for index, i in enumerate(images):
            img = lambda: dicom_to_Image(i)
            tmp = mkdtemp()
            if true_masks == None:
                truth_path = os.path.join(tmp, "current_truth.png")
                truth = model.predict(model.prepareSize(img()))#[0]
                truth.save(truth_path)
                true_mask = lambda: Image.open(truth_path)
            elif true_masks != None:
                true_mask = lambda: Image.open(true_masks[index])
            transform_function = list(eval_functions.values())[number]
            mask_prepareSize = True
            if true_masks == None:
                mask_prepareSize = False #when set to false, so when no true mask is provided by the user and thus generated by batch_mode, functions that change the size of the true mask like resize don't work any longer.
            df = transform_function(img(), true_mask(), model, components=components, mask_prepareSize=mask_prepareSize)
            df["File"] = i
            df["Transformation"] = list(eval_functions.keys())[number]
            trfm_result.append(df)
            rmtree(tmp)
        trfm_result = pd.concat(trfm_result)
        results.append(trfm_result)
    return results

# Cell
def plot_avg_and_dots(df, draw_line=True, dots="single_values", value_name='Dice Score'):
    '''
    Plots the average dice score and shows the single data points

    Positional arguments:
    -df (pd.DataFrame object): columns: 'parameter', 'bg', 'LV', 'MY', 'RV', 'File'
    -draw_line (Boolean): determines if the line between the average of the datapoints is drawn
    -dots (string): "single_values" or "average"_ determines wether the dots show every single datapoint or one point for the average for each parameter
    -value_name (str): Name for the Y axis. Depending on which evaluation Score you used in the evaluation function, you can change the Label for the Y axis here.

    Returns: altair.FacetChart object
    '''
    melt_results = df.melt(id_vars=df.columns[0], value_vars=df.columns[2:5], value_name=value_name)
    if dots == "single_values":
        dot_plot = alt.Chart(melt_results
                ).mark_point(
                ).encode(x=melt_results.columns[0], y=alt.Y(f"{value_name}", scale=alt.Scale(domain=(0, 1.1))), color=alt.Color("variable")
                ).properties(width=400, height=200
                ).interactive()
    elif dots == "average":
        dot_plot = alt.Chart(melt_results
                ).mark_point(
                ).encode(x=melt_results.columns[0], y=alt.Y(f"average({value_name})", scale=alt.Scale(domain=(0, 1.1))), color=alt.Color("variable")
                ).properties(width=400, height=200
                ).interactive()
    if draw_line == True:
        avg_line_plot = alt.Chart(melt_results
                    ).mark_line(
                    ).encode(x=melt_results.columns[0], y=f"average({value_name})", color=alt.Color("variable")
                    ).properties(width=400, height=200
                    ).interactive()
        plot = alt.layer(dot_plot, avg_line_plot).facet(column="variable")
    else:
        plot = dot_plot.facet(column="variable")
    return plot

# Cell
def plot_avg_and_errorbars(df, value_name='Dice Score'):
    '''
    Plots the average dice score and shows the stdev as errorbars.

    Positional arguments:
    -df (pd.DataFrame object): columns: 'parameter', 'bg', 'LV', 'MY', 'RV', 'File'
    -value_name (str): Name for the Y axis. Depending on which evaluation Score you used in the evaluation function, you can change the Label for the Y axis here.

    Returns: altair.FacetChart object
    '''
    melt_results = df.melt(id_vars=df.columns[0], value_vars=df.columns[2:5], value_name=value_name)
    avg_line_plot = alt.Chart(melt_results
                ).mark_line(
                ).encode(x=melt_results.columns[0], y=f"average({value_name})", color=alt.Color("variable")
                ).properties(width=400, height=200
                ).interactive()
    error_bars = alt.Chart(melt_results
                ).mark_errorbar(extent='stdev'#, ticks=True
                ).encode(x=melt_results.columns[0], y=value_name, color=alt.Color("variable"))
    plot = alt.layer(avg_line_plot, error_bars).facet(column="variable")
    return plot

# Cell
def plot_boxplot(df, value_name='Dice Score'):
    '''
    Plots the average dice score as boxplots

    Positional arguments:
    -df (pd.DataFrame object): columns: 'parameter', 'bg', 'LV', 'MY', 'RV', 'File'
    -value_name (str): Name for the Y axis. Depending on which evaluation Score you used in the evaluation function, you can change the Label for the Y axis here.

    Returns: altair.FacetChart object
    '''
    melt_results = df.melt(id_vars=df.columns[0], value_vars=df.columns[2:5], value_name=value_name)
    plot = alt.Chart(melt_results
                ).mark_boxplot(extent="min-max", size=5
                ).encode(x=alt.X(melt_results.columns[0]), y=alt.Y(value_name), color=alt.Color("variable")
                ).properties(width=400, height=200
                ).facet(column="variable"
                ).interactive()
    return plot

# Cell
def plot_batch(df_results, plot_function=plot_avg_and_dots):
    '''
    Creates and displays the plots with the data as returned by the batch_results functions.

    Positional arguments:
    -df_results (list): dataframes which contains one dataFrame for each transformation in a format as it is returned by `batch_results`
    Keyword arguments:
    -plot_function:
        - plot_avg_and_errorbars: plots the average of the dice score of all images across the parameters and shows the standarddeviation as errorbars
        - plot_avg_and_dots: plots the average of the dice score and additionally shows the single datapoints instead of errorbars
        - plot_boxplot

    Returns: List with altair.FacetChart objects
    '''
    plots = []
    for index, i in enumerate(df_results):
        plot = plot_function(i)
        plot = plot.properties(title=df_results[index]["Transformation"].values[0]
                ).configure_legend(labelFontSize=13, title=None
                ).configure_axisX(titleFontSize=13, labelFontSize=13
                ).configure_axisY(titleFontSize=13, labelFontSize=13
                ).configure_header(titleFontSize=25, labelFontSize=13, title=None, labels=False
                ).configure_title(fontSize=20, anchor='middle')
        plots.append(plot)
    for p in plots:
        p.display()
    return plots