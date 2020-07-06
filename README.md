# Model Interpretation through Sensitivity Analysis for Segmentation
> Interpret and explain your segmetation models through analysing their sensitivity to defined alterations of the input


Input alterations currently include:
 - rotation
 - cropping

## Install

`pip install misas`

## How to use

Example with kaggle data

```
from fastai.vision import *
```

```
img = lambda: open_image("example/kaggle/images/1-frame014-slice005.png")
trueMask = lambda: open_mask("example/kaggle/masks/1-frame014-slice005.png")
trainedModel = load_learner(path="example/kaggle", file="model.pkl", tfm_y=False)
resize256 = lambda image: image.resize(256)
img().show(y=trueMask(), figsize=(8,8))
```


![png](docs/images/output_6_0.png)


### Rotation

```
plot_series(get_rotation_series(img(), trainedModel, prep_function=resize256))
```


![png](docs/images/output_8_0.png)


```
results = eval_rotation_series(img(), trueMask(), trainedModel, prep_function=resize256)
plt.plot(results['deg'], results['c1'])
plt.plot(results['deg'], results['c2'])
plt.axis([0,360,0,1])
```




    [0, 360, 0, 1]




![png](docs/images/output_9_1.png)


You can use interactive elements to manually explore the impact of rotation

```
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
```

```
rotation_series = get_rotation_series(img(),trainedModel,prep_function=resize256,step=10)
```

```
def plot_rotation_frame(deg):
    return plot_frame(*rotation_series[int(deg/10)], figsize=(10,10))
```

```
interact(
    plot_rotation_frame,
    deg=widgets.IntSlider(min=0, max=360, step=10, value=90, continuous_update=False)
)
```




    <function __main__.plot_rotation_frame(deg)>



There are lots of other transformations to try (e.g. cropping, brightness, contrast, ...). For a complete list see the local_interpret documentation.
