# AUTOGENERATED! DO NOT EDIT! File to edit: 01_local_interpret_pillow_rewrite.ipynb (unless otherwise specified).

__all__ = ['Fastai1_model', 'get_generic_series', 'plot_series', 'plot_frame', 'gif_series', 'eval_generic_series',
           'plot_eval_series', 'rotationTransform', 'get_rotation_series', 'eval_rotation_series', 'cropTransform',
           'get_crop_series', 'eval_crop_series', 'brightnessTransform', 'get_brightness_series', 'eval_bright_series',
           'contrastTransform', 'get_contrast_series', 'eval_contrast_series', 'zoomTransform', 'get_zoom_series',
           'eval_zoom_series', 'dihedralTransform', 'get_dihedral_series', 'eval_dihedral_series', 'resizeTransform',
           'get_resize_series', 'eval_resize_series', 'get_confusion', 'plot_confusion', 'plot_confusion_series',
           'Dummy_model', 'get_generic_series', 'plot_series', 'plot_frame', 'gif_series', 'eval_generic_series',
           'plot_eval_series', 'rotationTransform', 'get_rotation_series', 'eval_rotation_series', 'cropTransform',
           'get_crop_series', 'eval_crop_series', 'brightnessTransform', 'get_brightness_series', 'eval_bright_series',
           'contrastTransform', 'get_contrast_series', 'eval_contrast_series', 'zoomTransform', 'get_zoom_series',
           'eval_zoom_series', 'dihedralTransform', 'get_dihedral_series', 'eval_dihedral_series', 'resizeTransform',
           'get_resize_series', 'eval_resize_series', 'get_confusion', 'plot_confusion', 'plot_confusion_series']

# Internal Cell
from fastai.vision import *
import pandas as pd
from tqdm.notebook import tqdm
import matplotlib.pyplot as plt
import gif
import math
import numpy as np
import torchvision
import altair as alt
import warnings
warnings.filterwarnings('ignore')

# Internal Cell
def dice_by_component(predictedMask, trueMask, component = 1):
    dice = Tensor([1])
    pred = predictedMask.data == component
    msk = trueMask.data == component
    intersect = pred&msk
    total = pred.sum() + msk.sum()
    if total > 0:
        dice = 2 * intersect.sum().float() / total
    return dice.item()

# Internal Cell
def recall_by_component(predictedMask, trueMask, component = 1):
    recall = Tensor([1])
    pred = predictedMask.data == component
    msk = trueMask.data == component
    intersect = pred&msk
    total = pred.sum() + msk.sum()
    if total > 0:
        recall = intersect.sum().float() / msk.sum()
    return recall.item()

# Internal Cell
def precision_by_component(predictedMask, trueMask, component = 1):
    precision = Tensor([1])
    pred = predictedMask.data == component
    msk = trueMask.data == component
    intersect = pred&msk
    total = pred.sum() + msk.sum()
    if total > 0:
        precision = Tensor([0])
        if pred.sum() > 0:
            precision = intersect.sum().float() / pred.sum()
    return precision.item()

# Cell
class Fastai1_model:
    def __init__(self, github, model):
        self.trainedModel = torch.hub.load(github,model)
        self.resize256 = lambda x: x.resize(256)

    def prepareSize(self, item):
        return self.resize256(item)

    def predict(self, image):
        return self.trainedModel.predict(image)

# Internal Cell
from matplotlib import cm
from matplotlib.colors import ListedColormap

default_cmap = cm.viridis(np.arange(cm.inferno.N))
default_cmap[0][-1] = 0
default_cmap = ListedColormap(default_cmap)

# Cell
def get_generic_series(image,
        model,
        transform,
        truth=None,
        tfm_y=False,
        start=0,
        end=180,
        step=30,
        log_steps=False,
    ):
    series = []
    trueMask = None
    steps = np.arange(start,end,step)
    if log_steps:
        steps = np.exp(np.linspace(log(start),log(end),int((end-start)/step)))
    for param in tqdm(steps, leave=False):
        img = image.clone()
        img = transform(img, param)
        if hasattr(model,"prepareSize"):
            img = model.prepareSize(img)
        pred = model.predict(img)[0]
        series.append([param,img,pred])
        if truth:
            trueMask = truth.clone()
            if tfm_y:
                trueMask = transform(trueMask, param)
            if hasattr(model,"prepareSize"):
                trueMask = model.prepareSize(trueMask)
        series[-1].append(trueMask)
    return series

# Cell
def plot_series(
        series,
        nrow=1,
        figsize=(16,6),
        param_name='param',
        overlay_truth=False,
        vmax=None,
        cmap=default_cmap,
        **kwargs
    ):
    fig, axs = plt.subplots(nrow,math.ceil(len(series)/nrow),figsize=figsize,**kwargs)
    #fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9)
    for element, ax in zip(series, axs.flatten()):
        param,img,pred,truth = element
        img.show(ax=ax, title=f'{param_name}={param:.2f}')
        if vmax is None:
            vmax = max([x[2].data.max() for x in series])
            if truth:
                vmax_truth = max([x[3].data.max() for x in series])
                vmax = max(vmax_truth, vmax)
        pred.show(ax=ax,vmax=vmax,cmap=cmap)
        if overlay_truth and truth:
            truth.show(ax=ax,alpha=.2)

# Cell
@gif.frame
def plot_frame(param, img, pred, param_name="param",vmax=None,cmap=default_cmap,**kwargs):
    _,ax = plt.subplots(**kwargs)
    img.show(ax,title=f'{param_name}={param:.2f}')
    pred.show(ax, vmax=vmax, cmap=cmap)

# Cell
def gif_series(series, fname, duration=150, param_name="param", vmax=None, cmap=default_cmap):
    if vmax is None:
        vmax = max([x[2].data.max() for x in series])
    frames = [plot_frame(*x[:3], param_name=param_name, vmax=vmax, cmap=cmap) for x in series]
    gif.save(frames, fname, duration=duration)

# Cell
def eval_generic_series(
        image,
        mask,
        model,
        transform_function,
        start=0,
        end=360,
        step=5,
        param_name="param",
        mask_transform_function=None,
        components=['bg', 'c1','c2'],
        eval_function=dice_by_component
    ):
    results = list()
    for param in tqdm(np.arange(start, end, step), leave=False):
        img = image.clone()
        img = transform_function(img, param)
        trueMask = mask.clone()
        if mask_transform_function:
            trueMask = mask_transform_function(trueMask, param)
        if hasattr(model,"prepareSize"):
            img = model.prepareSize(img)
            trueMask = model.prepareSize(trueMask)
        prediction = model.predict(img)[0]
        # prediction._px = prediction._px.float()
        result = [param]
        for i in range(len(components)):
            result.append(eval_function(prediction, trueMask, component = i))
        results.append(result)

    results = pd.DataFrame(results,columns = [param_name, *components])
    return results

# Cell
def plot_eval_series(results, chart_type="line", value_vars=None, value_name='Dice Score'):
    id_var = results.columns[0]
    if not value_vars:
        value_vars = results.columns[2:]
    plot = alt.Chart(results.melt(id_vars=[id_var],value_vars=value_vars, value_name=value_name))
    if chart_type=="line":
        plot = plot.mark_line()
    elif chart_type=="point":
        plot = plot.mark_point(size=80)
    else:
        raise ValueError(f'chart_type must be one of "line" or "point"')
    plot = plot.encode(
      x=id_var,
      y=value_name,
      color=alt.Color("variable"),#,legend=None),
      tooltip=value_name
    ).properties(width=700,height=300).interactive()
    return plot#.configure_axis(title=None,labels=False,ticks=False)

# Cell
def rotationTransform(image, deg):
    return image.rotate(int(deg))

def get_rotation_series(image, model, start=0, end=360, step=60, **kwargs):
    return get_generic_series(image,model,rotationTransform, start=start, end=end, step=step, **kwargs)

# Cell
def eval_rotation_series(image, mask, model, step=5, start=0, end=360,  param_name="deg", **kwargs):
    return eval_generic_series(
        image,
        mask,
        model,
        rotationTransform,
        start=start,
        end=end,
        step=step,
        mask_transform_function=rotationTransform,
        param_name=param_name,
        **kwargs
    )

# Cell
def cropTransform(image, pxls, finalSize=256):
    image = image.clone()
    image = image.resize(finalSize)
    image = image.crop_pad(int(pxls))
    image = image.rotate(180)
    image = image.crop_pad(finalSize, padding_mode="zeros")
    image = image.rotate(180)
    return image

def get_crop_series(image, model, start=56, end=257, step=50, finalSize=256, **kwargs):
    return get_generic_series(image,model,partial(cropTransform,finalSize=finalSize), start=start, end=end, step=step, **kwargs)

# Cell
def eval_crop_series(image, mask, model, step=5, start=56, end=256, finalSize=256, param_name="pixels", **kwargs):
    return eval_generic_series(
        image,
        mask,
        model,
        partial(cropTransform,finalSize=finalSize),
        start=start,
        end=end,
        step=step,
        mask_transform_function=partial(cropTransform,finalSize=finalSize),
        param_name=param_name,
        **kwargs
    )

# Cell
def brightnessTransform(image, light):
    return image.brightness(light)

def get_brightness_series(image, model, start=0.05, end=1, step=.1, **kwargs):
    return get_generic_series(image,model,brightnessTransform, start=start, end=end, step=step, **kwargs)

# Cell
def eval_bright_series(image, mask, model, start=0.05, end=.95, step=0.05, param_name="brightness", **kwargs):
    return eval_generic_series(
        image,
        mask,
        model,
        brightnessTransform,
        start=start,
        end=end,
        step=step,
        param_name=param_name,
        **kwargs
    )

# Cell
def contrastTransform(image, scale):
    return image.contrast(scale)

def get_contrast_series(image, model, start=0.1, end=7.11, step=1, **kwargs):
    return get_generic_series(image,model,contrastTransform, start=start, end=end, step=step, **kwargs)

# Cell
def eval_contrast_series(image, mask, model, start=0.1, end=7.1, step=0.5, param_name="contrast", **kwargs):
    return eval_generic_series(
        image,
        mask,
        model,
        contrastTransform,
        start=start,
        end=end,
        step=step,
        param_name=param_name,
        **kwargs
    )

# Cell
def zoomTransform(image, scale, finalSize=256):
    image = image.resize(finalSize).clone()
    image = image.crop_pad(int(scale), padding_mode="zeros")
    image = image.resize(finalSize).clone()
    return image

def get_zoom_series(image, model, start=56, end=500, step=50, finalSize=256, **kwargs):
    return get_generic_series(image,model,partial(zoomTransform,finalSize=finalSize), start=start, end=end, step=step, **kwargs)

# Cell
def eval_zoom_series(image, mask, model, step=10, start=56, end=500, finalSize=256, param_name="scale", **kwargs):
    return eval_generic_series(
        image,
        mask,
        model,
        partial(zoomTransform,finalSize=finalSize),
        start=start,
        end=end,
        step=step,
        mask_transform_function=partial(zoomTransform,finalSize=finalSize),
        param_name=param_name,
        **kwargs
    )

# Cell
def dihedralTransform(image, sym_im):
    return image.dihedral(k=int(sym_im))

def get_dihedral_series(image, model, start=0, end=8, step=1, **kwargs):
    return get_generic_series(image,model,dihedralTransform, start=start, end=end, step=step, **kwargs)

# Cell
def eval_dihedral_series(image, mask, model, start=0, end=8, step=1, param_name="k", **kwargs):
    return eval_generic_series(
        image,
        mask,
        model,
        dihedralTransform,
        start=start,
        end=end,
        step=step,
        param_name=param_name,
        mask_transform_function=dihedralTransform,
        **kwargs
    )

# Cell
def resizeTransform(image, size):
    return image.resize(int(size)).clone()

# Cell
def get_resize_series(image, model, start=10, end=200, step=30, **kwargs):
    return get_generic_series(image,model,resizeTransform, start=start, end=end, step=step, **kwargs)

# Cell
def eval_resize_series(image, mask, model, start=22, end=3000, step=100, param_name="px", **kwargs):
    return eval_generic_series(
        image,
        mask,
        model,
        resizeTransform,
        start=start,
        end=end,
        step=step,
        param_name=param_name,
        mask_transform_function=resizeTransform,
        **kwargs
    )

# Cell
def get_confusion(prediction, truth, max_class=None):
    if not max_class:
        max_class = max(prediction.data.max(), truth.data.max())
    # https://stackoverflow.com/a/50023660
    cm = np.zeros((max_class+1, max_class+1), dtype=int)
    np.add.at(cm, (prediction.data, truth.data), 1)
    return cm

# Cell
def plot_confusion(confusion_matrix, norm_axis=0, components=None, ax=None, ax_label=True, cmap="Blues"):
    cm = confusion_matrix / confusion_matrix.sum(axis=norm_axis, keepdims=True)
    if not components:
        components = ["c" + str(i) for i in range(cm.shape[0])]
    if not ax:
        _, ax = plt.subplots()
    ax.imshow(cm, cmap=cmap)

    # We want to show all ticks...
    ax.set_xticks(np.arange(len(components)))
    ax.set_yticks(np.arange(len(components)))

    # ... and label them with the respective list entries
    ax.set_xticklabels(components)
    ax.set_yticklabels(components)

    # label axes
    if ax_label:
        ax.set_xlabel("truth")
        ax.set_ylabel("prediction")

    # label cells
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            text = ax.text(j, i, round(cm[i, j],2),
                           ha="center", va="center")

    return ax

# Cell
def plot_confusion_series(
        series,
        nrow=1,
        figsize=(16,6),
        param_name='param',
        cmap="Blues",
        components=None,
        norm_axis=0,
        **kwargs
    ):
    fig, axs = plt.subplots(nrow,math.ceil(len(series)/nrow),figsize=figsize,**kwargs)
    for element, ax in zip(series, axs.flatten()):
        param,img,pred,truth = element
        cm = get_confusion(pred,truth)
        plot_confusion(cm, ax=ax, components=components, ax_label=False, norm_axis=norm_axis, cmap=cmap)

# Internal Cell
#from fastai.vision import *
from PIL import Image, ImageEnhance, ImageShow, ImageOps
from matplotlib.pyplot import imshow
from functools import partial
import itertools
import pandas as pd
from tqdm.notebook import tqdm
import matplotlib.pyplot as plt
import gif
import math
import numpy as np
import torchvision
import altair as alt
import warnings
warnings.filterwarnings('ignore')

# Internal Cell
def dice_by_component(predictedMask, trueMask, component = 1):
    """
    Calculates the dice score (the overlap between the mask predicted
    by the model and the true mask that the user supplies, while 0 equals
    no overlap and 1 equals 100% overlap)
    user supplies the predictedMask
    and trueMask through the function eval_generic_series, component's
    standard value is set to 1, but gets overwritten by
    eval_generic_series)
    """
    dice = 1.0
    #dice = Tensor([1])
    #example = Tensor([1])
    #print (example)
    pred = np.array(predictedMask) == component
    #print (pred)
    msk = np.array(trueMask) == component
    #print(msk)
    intersect = pred&msk
    #print(intersect)
    total = np.sum(pred) + np.sum(msk)
    #print(total)
    if total > 0:
        dice = 2 * np.sum(intersect).astype(float) / total
    return dice

# Internal Cell
def recall_by_component(predictedMask, trueMask, component = 1):
    """
    Calculates the recall score (percentage of trueMask that is included
    in the overlap of trueMask and predictedMask)
    """
    recall = 1.0
    pred = np.array(predictedMask) == component
    msk = np.array(trueMask) == component
    intersect = pred&msk
    total = np.sum(pred) + np.sum(msk)
    if total > 0:
        recall = np.sum(intersect).astype(float) / np.sum(msk)
    return recall

# Internal Cell
def precision_by_component(predictedMask, trueMask, component = 1):
    """
    Calculates the precision score (percentage of predictedMask that is included
    in the overlap of trueMask and predictedMask)
    """
    precision = 1.0
    pred = np.array(predictedMask) == component
    msk = np.array(trueMask) == component
    intersect = pred&msk
    total = np.sum(pred) + np.sum(msk)
    if total > 0:
        precision = 1.0
        if np.sum(pred) > 0:
            precision = np.sum(intersect).astype(float) / np.sum(pred)
    return precision

# Cell
class Dummy_model:
    #def __init__(self, github, model):



    def prepareSize(self, item):
        return item

    def predict(self, image):
        return [trueMask()]
    #    return self.trainedModel.predict(image)

# Internal Cell
from matplotlib import cm
from matplotlib.colors import ListedColormap

default_cmap = cm.viridis(np.arange(cm.inferno.N))
default_cmap[0][-1] = 0
default_cmap = ListedColormap(default_cmap)

# Cell
def get_generic_series(image,
        model,
        transform,
        truth=None,
        tfm_y=False,
        start=0,
        end=180,
        step=30,
        log_steps=False,
    ):
    """
    Generic function for transforming images.
    Input: image (PIP image, usually your sample image opened by img()),
    model (the function for your model that manages the prediction for your mask),
    transform (your specific transformation function),
    truth = None (replaces with a true mask if available),
    tfm_y = False (set to True if your true mask has to be transformed as well to fit the
    transformed sample image e.g in case of a rotation of the sample image),


    """
    series = []
    trueMask = None
    steps = np.arange(start,end,step)
    if log_steps:
        steps = np.exp2(np.linspace(np.log2(start),np.log2(end),round((np.log2(end)-np.log2(start))/np.log2(step)+1)))
    for param in tqdm(steps, leave=False):
        img = image
        img = transform(img, param)
        if hasattr(model,"prepareSize"):
            img = model.prepareSize(img)
        pred = model.predict(img)[0]
        series.append([param,img,pred])
        if truth:
            trueMask = truth
            if tfm_y:
                trueMask = transform(trueMask, param)
            if hasattr(model,"prepareSize"):
                trueMask = model.prepareSize(trueMask)
        series[-1].append(trueMask)
    return series

# Cell
def plot_series(
        series,
        nrow=1,
        figsize=(16,6),
        param_name='param',
        overlay_truth=False,
        vmax=None,
        cmap=default_cmap,
        **kwargs
    ):
    fig, axs = plt.subplots(nrow,math.ceil(len(series)/nrow),figsize=figsize,**kwargs)
    #fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9)
    if vmax is None:
        #vmax = max([x[2].data.max() for x in series])
        vmax = max([x[2].getextrema()[1] for x in series])
        #x = pred.getextrema()
        #vmax = x[1]
        if series[0][3]:
            vmax_truth = max([x[3].getextrema()[1] for x in series])
            vmax = max(vmax_truth, vmax)
    for element, ax in zip(series, axs.flatten()):
        param,img,pred,truth = element
        #img.show(ax=ax, title=f'{param_name}={param:.2f}')
        #ax.imshow(img)
        ax.imshow(np.array(img))
        #pred.show(ax=ax,vmax=vmax,cmap=cmap)
        ax.imshow(np.array(pred), vmax=vmax,cmap=cmap) #don't forget to uncomment this line

        if overlay_truth and truth:
            #ax.imshow(truth, alpha=.2)
            ax.imshow(np.array(truth), alpha = 0.2)
            #truth.show(ax=ax,alpha=.2)

# Cell
@gif.frame
def plot_frame(param, img, pred, param_name="param",vmax=None,cmap=default_cmap,**kwargs):
    _,ax = plt.subplots(**kwargs)
    #img.show(ax,title=f'{param_name}={param:.2f}')
    ax.imshow(img)
    #pred.show(ax, vmax=vmax, cmap=cmap)
    ax.imshow(np.array(pred), vmax=vmax,cmap=cmap)

# Cell
def gif_series(series, fname, duration=150, param_name="param", vmax=None, cmap=default_cmap):
    if vmax is None:
        #vmax = max([x[2].data.max() for x in series])
        vmax = max([x[2].getextrema()[1] for x in series])
    frames = [plot_frame(*x[:3], param_name=param_name, vmax=vmax, cmap=cmap) for x in series]
    gif.save(frames, fname, duration=duration)

# Cell
def eval_generic_series(
        image,
        mask,
        model,
        transform_function,
        start=0,
        end=360,
        step=5,
        param_name="param",
        mask_transform_function=None,
        components=['bg', 'c1','c2'],
        eval_function=dice_by_component
    ):
    results = list()
    for param in tqdm(np.arange(start, end, step), leave=False):
        img = image
        img = transform_function(img, param)
        trueMask = mask
        if mask_transform_function:
            trueMask = mask_transform_function(trueMask, param)
        if hasattr(model,"prepareSize"):
            img = model.prepareSize(img)
            trueMask = model.prepareSize(trueMask)
        prediction = model.predict(img)[0]
        # prediction._px = prediction._px.float()
        result = [param]
        for i in range(len(components)):
            result.append(eval_function(prediction, trueMask, component = i))
        results.append(result)

    results = pd.DataFrame(results,columns = [param_name, *components])
    return results

# Cell
def plot_eval_series(results, chart_type="line", value_vars=None, value_name='Dice Score'):
    id_var = results.columns[0]
    if not value_vars:
        value_vars = results.columns[2:]
    plot = alt.Chart(results.melt(id_vars=[id_var],value_vars=value_vars, value_name=value_name))
    if chart_type=="line":
        plot = plot.mark_line()
    elif chart_type=="point":
        plot = plot.mark_point(size=80)
    else:
        raise ValueError(f'chart_type must be one of "line" or "point"')
    plot = plot.encode(
      x=id_var,
      y=value_name,
      color=alt.Color("variable"),#,legend=None),
      tooltip=value_name
    ).properties(width=700,height=300).interactive()
    return plot#.configure_axis(title=None,labels=False,ticks=False)

# Cell
def rotationTransform(image, deg):
    return image.rotate(int(deg))


def get_rotation_series(image, model, start=0, end=360, step=60, **kwargs):
    return get_generic_series(image,model,rotationTransform, start=start, end=end, step=step, **kwargs)

# Cell
def eval_rotation_series(image, mask, model, step=5, start=0, end=360,  param_name="deg", **kwargs):
    return eval_generic_series(
        image,
        mask,
        model,
        rotationTransform,
        start=start,
        end=end,
        step=step,
        mask_transform_function=rotationTransform,
        param_name=param_name,
        **kwargs
    )

# Cell
#def cropTransform(image, pxls, finalSize=256):
#    image = ImageOps.fit(image, (finalSize ,finalSize))
#    image = ImageOps.crop(image, (finalSize)//2-pxls)
#    image = ImageOps.crop(image, (-(finalSize//2-pxls)))
#    return image



#def cropTransform(image, pxls, finalSize=256):
    #image = image.contain(finalSize)
    #return image
    #image = image.clone()
    #image = image.resize(finalSize)
    #image = image.crop_pad(int(pxls))
    #image = image.rotate(180)
    #image = image.crop_pad(finalSize, padding_mode="zeros")
    #image = image.rotate(180)

#PIL.ImageOps.crop(image, border=0)[source]¶
#PIL.ImageOps.contain(image, size, method=Resampling.BICUBIC)[source]¶
#np.min
#is number -> make tuple
# is tuple -> stay tuple
#finalSize = min (tuple)/2

#def get_crop_series(image, model, start=20, end=257, step=20, finalSize=256, **kwargs):
#    if end >= finalSize//2:
#        end = finalSize//2
#        #print(type(finalSize//2))
#    return get_generic_series(image,model,partial(cropTransform,finalSize=finalSize), start=start, end=end, step=step, **kwargs)
    #return get_generic_series(image,model,cropTransform(finalSize=finalSize), start=start, end=end, step=step, **kwargs)

# Cell
def cropTransform(image, pxls, finalSize = img().size):
    image = ImageOps.fit(image, (finalSize))
    image = ImageOps.crop(image, (min(finalSize)//2-pxls))
    image = ImageOps.crop(image, (-(min(finalSize)//2-pxls)))
    return image




#def cropTransform(image, pxls, finalSize=(230, 256)):
#    image = ImageOps.fit(image, (finalSize))
#    image = ImageOps.crop(image, (min(finalSize)//2-pxls))
#    image = ImageOps.crop(image, (-(min(finalSize)//2-pxls)))
#    return image

#finalSize = img().size
#print (finalSize)


#PIL.ImageOps.crop(image, border=0)[source]¶
#PIL.ImageOps.contain(image, size, method=Resampling.BICUBIC)[source]¶

#is number -> make tuple
# is tuple -> stay tuple
#finalSize = min (tuple)/2

def get_crop_series(image, model, start=20, end=257, step=10, finalSize = img().size, **kwargs):
    if type(finalSize) == int:
        finalSize = (finalSize, finalSize)
    if end >= min(finalSize)//2:
        end = min(finalSize)//2
    return get_generic_series(image,model,partial(cropTransform,finalSize=finalSize), start=start, end=end, step=step, **kwargs)
    #return get_generic_series(image,model,cropTransform(finalSize=finalSize), start=start, end=end, step=step, **kwargs)

# Cell
def eval_crop_series(image, mask, model, step=5, start=56, end=256, finalSize=img().size, param_name="pixels", **kwargs):
    if type(finalSize) == int:
        finalSize = (finalSize, finalSize)
    if end >= min(finalSize)//2:
        end = min(finalSize)//2
    return eval_generic_series(
        image,
        mask,
        model,
        partial(cropTransform,finalSize=finalSize),
        start=start,
        end=end,
        step=step,
        mask_transform_function=partial(cropTransform,finalSize=finalSize),
        param_name=param_name,
        **kwargs
    )

# Cell
def brightnessTransform(image, light):
    #return image.brightness(light)
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance (light)
    return image

def get_brightness_series(image, model, start=0.25, end=8, step=np.sqrt(2), log_steps = True, **kwargs):
    return get_generic_series(image,model,brightnessTransform, start=start, end=end, step=step, log_steps=log_steps, **kwargs)

# Cell
def eval_bright_series(image, mask, model, start=0.05, end=.95, step=0.05, param_name="brightness", **kwargs):
    return eval_generic_series(
        image,
        mask,
        model,
        brightnessTransform,
        start=start,
        end=end,
        step=step,
        param_name=param_name,
        **kwargs
    )

# Cell
def contrastTransform(image, scale):
    #return image.contrast(scale)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance (scale)
    return image
def get_contrast_series(image, model, start=0.25, end=8, step=np.sqrt(2),log_steps = True, **kwargs):
    return get_generic_series(image,model,contrastTransform, start=start, end=end, step=step,log_steps = log_steps, **kwargs)

# Cell
def eval_contrast_series(image, mask, model, start=0.25, end=8, step=np.sqrt(2), param_name="contrast", **kwargs):
    return eval_generic_series(
        image,
        mask,
        model,
        contrastTransform,
        start=start,
        end=end,
        step=step,
        param_name=param_name,
        **kwargs
    )

# Cell
def zoomTransform(image, zoom, finalSize= img().size):
    #image = image.resize(finalSize).clone()
    #image = image.crop_pad(int(scale), padding_mode="zeros")
    #image = image.resize(finalSize).clone()
    #if scale >= finalSize//2 :
    #    scale = (finalSize//2-1)
    #    print ("You should lower your end value")
    #image = ImageOps.fit(image, (finalSize))
    max_zoom = ((image.size[0]//2-1),(image.size[1]//2)-1)
    min_zoom = (0,0)
    zoom_factor = []
    zoom_factor.append (round(max_zoom [0] * zoom))
    zoom_factor.append (round(max_zoom [1] * zoom))
    zoom_factor_tuple=tuple(zoom_factor)
    image = ImageOps.crop (image, zoom_factor_tuple) # finalSize/2 - 1 ist die Grenze
    image = ImageOps.pad (image ,(finalSize))
    return image

def get_zoom_series(image, model, start=0, end=1, step=.1, finalSize= img().size, **kwargs):
    #return get_generic_series(image,model,partial(zoomTransform,finalSize=finalSize), start=start, end=end, step=step, **kwargs)
#def get_zoom_series(image, model, start=10, end=127, step=10, finalSize=256, **kwargs):
    if type(finalSize) == int:
        finalSize = (finalSize, finalSize)
    if end > 1:
        end = 1
    return get_generic_series(image,model,partial(zoomTransform,finalSize=finalSize), start=start, end=end, step=step, **kwargs)


#ZoomTrue = True , **kwargs
#->
#get_generic_series
# if ZoomTrue == True
#    pred = ImageOps.fit(pred, (finalSize,finalSize)

# Cell
#def zoomTransform(image, scale, finalSize=256):
#    #if scale >= finalSize//2 :
#    #    scale = (finalSize//2-1)
#    #    print ("You should lower your end value")
#    image = ImageOps.fit(image, (finalSize ,finalSize))
#    image = ImageOps.crop (image, scale) # finalSize/2 - 1 ist die Grenze
#    image = ImageOps.pad (image ,(finalSize ,finalSize))
#
#    return image
#
#def get_zoom_series(image, model, start=-30, end=140, step=10, finalSize=256, **kwargs):
#    return get_generic_series(image,model,partial(zoomTransform,finalSize=finalSize), start=start, end=end, step=step, **kwargs)
#def get_zoom_series(image, model, start=10, end=127, step=10, finalSize=256, **kwargs):
#    if end >= finalSize//2:
#        end = (finalSize//2-1)
#    return get_generic_series(image,model,partial(zoomTransform,finalSize=finalSize), start=start, end=end, step=step, **kwargs)

# Cell
def eval_zoom_series(image, mask, model, step=0.1, start=0, end=1, finalSize= img().size, param_name="scale", **kwargs):
    if type(finalSize) == int:
        finalSize = (finalSize, finalSize)
    if end > 1:
        end = 1
    return eval_generic_series(
        image,
        mask,
        model,
        partial(zoomTransform,finalSize=finalSize),
        start=start,
        end=end,
        step=step,
        mask_transform_function=partial(zoomTransform,finalSize=finalSize),
        param_name=param_name,
        **kwargs
    )

# Cell
def dihedralTransform(image, sym_im):
    #return image.dihedral(k=int(sym_im))
    rot = [0, 90, 180, 270]
    flip = [True, False]
    dihedral = list (itertools.product (rot, flip))
    image = image.rotate (dihedral[sym_im][0])
    if dihedral [sym_im][1] == True:
        #image = ImageOps.flip(image)
        image = ImageOps.mirror(image)
    return image
##PIL.ImageOps.flip(image)[source]¶
#PIL.ImageOps.mirror(image)[source]¶


def get_dihedral_series(image, model, start=0, end=8, step=1, **kwargs):
    return get_generic_series(image,model,dihedralTransform, start=start, end=end, step=step, **kwargs)

# Cell
def eval_dihedral_series(image, mask, model, start=0, end=8, step=1, param_name="k", **kwargs):
    return eval_generic_series(
        image,
        mask,
        model,
        dihedralTransform,
        start=start,
        end=end,
        step=step,
        param_name=param_name,
        mask_transform_function=dihedralTransform,
        **kwargs
    )

# Cell
def resizeTransform(image, size):
    size_original = image.size
    image=ImageOps.contain (image, (size,size))
    image = ImageOps.fit(image, size_original)
    return image
    #image.resize(int(size)).clone()
    #image.resize

# Cell
def get_resize_series(image, model, start=10, end=200, step=30, **kwargs):
    return get_generic_series(image,model,resizeTransform, start=start, end=end, step=step, **kwargs)

# Cell
def eval_resize_series(image, mask, model, start=22, end=3000, step=100, param_name="px", **kwargs):
    return eval_generic_series(
        image,
        mask,
        model,
        resizeTransform,
        start=start,
        end=end,
        step=step,
        param_name=param_name,
        mask_transform_function=resizeTransform,
        **kwargs
    )

# Cell
def get_confusion(prediction, truth, max_class=None):
    if not max_class:
        max_class = max(prediction.data.max(), truth.data.max())
    # https://stackoverflow.com/a/50023660
    cm = np.zeros((max_class+1, max_class+1), dtype=int)
    np.add.at(cm, (prediction.data, truth.data), 1)
    return cm

# Cell
def plot_confusion(confusion_matrix, norm_axis=0, components=None, ax=None, ax_label=True, cmap="Blues"):
    cm = confusion_matrix / confusion_matrix.sum(axis=norm_axis, keepdims=True)
    if not components:
        components = ["c" + str(i) for i in range(cm.shape[0])]
    if not ax:
        _, ax = plt.subplots()
    ax.imshow(cm, cmap=cmap)

    # We want to show all ticks...
    ax.set_xticks(np.arange(len(components)))
    ax.set_yticks(np.arange(len(components)))

    # ... and label them with the respective list entries
    ax.set_xticklabels(components)
    ax.set_yticklabels(components)

    # label axes
    if ax_label:
        ax.set_xlabel("truth")
        ax.set_ylabel("prediction")

    # label cells
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            text = ax.text(j, i, round(cm[i, j],2),
                           ha="center", va="center")

    return ax

# Cell
def plot_confusion_series(
        series,
        nrow=1,
        figsize=(16,6),
        param_name='param',
        cmap="Blues",
        components=None,
        norm_axis=0,
        **kwargs
    ):
    fig, axs = plt.subplots(nrow,math.ceil(len(series)/nrow),figsize=figsize,**kwargs)
    for element, ax in zip(series, axs.flatten()):
        param,img,pred,truth = element
        cm = get_confusion(pred,truth)
        plot_confusion(cm, ax=ax, components=components, ax_label=False, norm_axis=norm_axis, cmap=cmap)