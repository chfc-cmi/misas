# Model Interpretation through Sensitivity Analysis for Segmentation
> Interpret and explain your segmetation models through analysing their sensitivity to defined alterations of the input


Input alterations currently include:
 - rotation
 - cropping

## Install

`pip install misas`

## How to use

Example with kaggle data

```python
from fastai.vision import *
```

```python
img = lambda: open_image("example/kaggle/images/1-frame014-slice006.png")
trueMask = lambda: open_mask("example/kaggle/masks/1-frame014-slice006.png")
trainedModel = load_learner(path="example/kaggle", file="model.pkl", tfm_y=False)
img().show(y=trueMask(), figsize=(8,8))
```


![png](docs/images/output_6_0.png)


### Rotation

```python
plot_rotation_series(img, trainedModel)
```


![png](docs/images/output_8_0.png)


```python
results = rotation_series(img, trueMask, trainedModel)
plt.plot(results['deg'], results['diceLV'])
plt.plot(results['deg'], results['diceMY'])
plt.axis([0,360,0,1])
```

    





    [0, 360, 0, 1]




![png](docs/images/output_9_2.png)


### Cropping

```python
plot_crop_series(img, trainedModel)
```


![png](docs/images/output_11_0.png)


```python
results = crop_series(img, trueMask, trainedModel)
plt.plot(results['pxls'], results['diceLV'])
plt.plot(results['pxls'], results['diceMY'])
plt.axis([32,256,0,1])
```

    





    [32, 256, 0, 1]




![png](docs/images/output_12_2.png)

