# AUTOGENERATED! DO NOT EDIT! File to edit: 04_mr_artifacts.ipynb (unless otherwise specified).

__all__ = ['spikeTransform', 'get_spike_series', 'eval_rotation_series']

# Internal Cell
from torchio.transforms import RandomSpike

# Cell
def spikeTransform(image, intensityFactor, spikesPosition=[.1,.1]):
    data = image.data[0].unsqueeze(0)
    spikesPosition = [[0.0] + spikesPosition]
    spike = RandomSpike()
    data = spike.add_artifact(data, spikesPosition, intensityFactor)[0]
    data = torch.stack((data,data,data))
    return Image(torch.clamp(data,0,1))

def get_spike_series(image, model, start=0, end=2.5, step=.5, **kwargs):
    return get_generic_series(image,model,spikeTransform, start=start, end=end, step=step, **kwargs)

# Cell
def eval_rotation_series(image, mask, model, step=5, start=0, end=360, **kwargs):
    return eval_generic_series(
        image,
        mask,
        model,
        rotationTransform,
        start=start,
        end=end,
        step=step,
        mask_transform_function=rotationTransform,
        param_name="deg",
        **kwargs
    )