# DNSMOS Pro

This is the official implementation of ["DNSMOS Pro: A Reduced-Size DNN for Probabilistic MOS of Speech"](https://www.isca-archive.org/interspeech_2024/cumlin24_interspeech.html). DNSMOS Pro is a model that takes as input a speech clip, and outputs a Gaussian mean opinion score (MOS) distribution.

Authors: Fredrik Cumlin, Xinyu Liang  
Emails: fcumlin@gmail.com, hopeliang990504@gmail.com

## Quick start for students

The easiest path is:

```bash
git clone <this-repo-url>
cd DNSMOSPro
./install.sh
source .venv/bin/activate
dnsmospro path/to/audio.wav
```

That installs a terminal command called `dnsmospro`, so students do not need to remember `python cli.py ...`.

On Windows:

```bat
install.bat
.venv\Scripts\activate
dnsmospro path\to\audio.wav
```

### GUI

Students who do not want to use the terminal can launch the desktop app:

```bash
source .venv/bin/activate
dnsmospro-gui
```

Or directly:

```bash
python gui.py
```

The GUI lets them:

1. Add individual audio files.
2. Add a whole folder of recordings.
3. Score everything with one click.
4. View the MOS output in a results panel.

## Standalone app distribution

If you want students to avoid installing Python entirely, build native artifacts for each operating system and distribute those instead.

Recommended builder Python:

```bash
Python 3.12
```

Use Python 3.11 only if 3.12 gives you a wheel or packaging issue on a target platform. Do not use Apple Command Line Tools Python for GUI development or standalone builds.

macOS or Linux builder:

```bash
./build_standalone.sh
```

Windows builder:

```bat
build_standalone.bat
```

This creates a standalone artifact in `dist/`.

Outputs:

```bash
macOS: dist/DNSMOS Pro.app
Windows: dist/DNSMOS Pro/
Linux: dist/DNSMOS Pro/
```

Recommended distribution flow:

1. Build on each operating system you want to support.
2. Zip the finished app or `dist/` output for that operating system.
3. Send students the app directly instead of the source repo.
4. Keep the CLI install path only for advanced users.

Notes:

1. PyInstaller builds are platform-specific. One build does not run everywhere.
2. The bundled app includes the pretrained model files, so students do not need the repo checkout.
3. If macOS warns that the app is from an unidentified developer, you will need to codesign/notarize it for the smoothest distribution.
4. A GitHub Actions workflow is included at `.github/workflows/build-standalone.yml` to generate macOS, Windows, and Linux artifacts from tags or manual runs.

## Prerelease checklist

Before you cut a prerelease:

1. Test the CLI on a real audio file.
2. Test the GUI from source with Python 3.12.
3. Run `./build_standalone.sh` on macOS and confirm the app launches.
4. Push the repo and run the GitHub Actions matrix for macOS, Windows, and Linux.
5. Download each artifact and smoke-test it on the matching operating system.
6. Tag the repo with a prerelease version such as `v0.1.0-beta.1`.

### Common usage

Score one file:

```bash
dnsmospro speech.wav
```

Score several files:

```bash
dnsmospro samples/*.wav
```

Score a whole folder:

```bash
dnsmospro recordings/
```

Score a folder and its subfolders:

```bash
dnsmospro recordings/ --recursive
```

Show mean and variance:

```bash
dnsmospro speech.wav --verbose
```

Pick a different pretrained model:

```bash
dnsmospro speech.wav --model bvcc
```

The CLI automatically picks `cuda`, `mps`, or `cpu`, in that order, unless `--device` is supplied manually.

## Installation notes

### 1. Python

Use Python 3.9 or newer for CLI work. Use Python 3.11 or 3.12 for GUI and standalone builds.

### 2. One-command install

macOS and Linux:

```bash
./install.sh
```

Windows:

```bat
install.bat
```

The installer creates `.venv`, installs PyTorch, installs the project, and exposes both `dnsmospro` and `dnsmospro-gui`.

### 3. Manual install

If you prefer manual setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install torch
pip install -e .
```

## Inference in Python

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

## Making this easy for students

The main usability rules for a class setting are:

1. Give them one command to run after install: `dnsmospro file.wav`.
2. Avoid making them edit code or open Python.
3. Prefer a copy-paste setup block using a virtual environment.
4. Keep install commands platform-neutral unless you control the hardware.
5. Accept folders and globs so they can grade many files with one command.
6. Give non-technical users a GUI path as well as a CLI path.

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
