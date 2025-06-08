# DNSMOS Pro

This is the official implementation of ["DNSMOS Pro: A Reduced-Size DNN for Probabilistic MOS of Speech"](https://www.isca-archive.org/interspeech_2024/cumlin24_interspeech.html). DNSMOS Pro is a model that takes as input a speech clip, and outputs a Gaussian mean opinion score (MOS) distribution.

Authors: Fredrik Cumlin, Xinyu Liang  
Emails: fcumlin@gmail.com, hopeliang990504@gmail.com

## Inference

There are three pretrained DNSMOS Pro ready to be used, trained on three datasets respectively. For inference, one can do the following (all paths are relative to this directory):
```
import numpy as np
import torch

import utils  # Python file containing the STFT.

model = torch.jit.load('runs/NISQA/model_best.pt', map_location=torch.device('cpu'))
samples = np.ones(160_000)
# Defaults in `utils.stft` correspond to training values.
spec = torch.FloatTensor(utils.stft(samples))
with torch.no_grad():
    prediction = model(spec[None, None, ...])
mean = prediction[:, 0]
variance = prediction[:, 1]
print(f'{mean=}, {variance=}')
```
The mean can be used as a scalar prediction of MOS. Recommended input duration is 10 s, and should be of 16 kHz sample rate.

## Installation
Installation with pip:
```
pip install -r requirements.txt
pip install torch==2.1.0+cu118 --index-url https://download.pytorch.org/whl/cu118
```

## Dataset preparation
[VCC2018](https://github.com/unilight/LDNet/tree/main/data)

[BVCC](https://zenodo.org/records/6572573#.Yphw5y8RprQ)

[NISQA](https://github.com/gabrielmittag/NISQA/wiki/NISQA-Corpus)

## Training
The framework is Gin configurable; specifying model and dataset is done with a Gin config. See examples in `configs/*.gin`.

Example launch:
```
python train.py --gin_path "configs/vcc2018.gin" --save_path "runs/VCC2018"
```
