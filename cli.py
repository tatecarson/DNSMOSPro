#!/usr/bin/env python3
"""CLI for DNSMOS Pro - Speech quality/intelligibility assessment."""

import argparse
import glob
import sys
from pathlib import Path
from typing import Optional

import librosa
import torch

import utils


MODELS = {
    'nisqa': 'runs/NISQA/model_best.pt',
    'bvcc': 'runs/BVCC/model_best.pt',
    'vcc2018': 'runs/VCC2018/model_best.pt',
}


def app_root() -> Path:
    """Return the directory that contains bundled resources."""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def default_device() -> str:
    """Pick a sensible device automatically for student laptops."""
    if torch.cuda.is_available():
        return 'cuda'
    if torch.backends.mps.is_available():
        return 'mps'
    return 'cpu'


def predict(audio_path: str, model: torch.jit.ScriptModule, device: str) -> tuple[float, float]:
    """Run MOS prediction on an audio file."""
    samples, _ = librosa.load(audio_path, sr=16000)
    spec = torch.FloatTensor(utils.stft(samples)).to(device)

    with torch.no_grad():
        prediction = model(spec[None, None, ...])

    mean = prediction[0, 0].item()
    variance = prediction[0, 1].item()
    return mean, variance


def expand_audio_inputs(inputs: list[str], recursive: bool) -> list[Path]:
    """Resolve files, directories, and shell-like glob patterns into audio files."""
    resolved: list[Path] = []
    seen: set[Path] = set()
    audio_suffixes = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}

    for value in inputs:
        path = Path(value)
        matches: list[Path] = []

        if path.exists():
            if path.is_dir():
                pattern = '**/*' if recursive else '*'
                matches = [
                    candidate for candidate in path.glob(pattern)
                    if candidate.is_file() and candidate.suffix.lower() in audio_suffixes
                ]
            elif path.is_file():
                matches = [path]
        else:
            matches = [
                Path(candidate) for candidate in glob.glob(value, recursive=recursive)
                if Path(candidate).is_file()
            ]

        for match in matches:
            if match not in seen:
                resolved.append(match)
                seen.add(match)

    return resolved


def load_model(model_name: str, device: str) -> torch.jit.ScriptModule:
    """Load one of the bundled pretrained models."""
    model_path = app_root() / MODELS[model_name]
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found at {model_path}")

    model = torch.jit.load(str(model_path), map_location=device)
    model.eval()
    return model


def score_audio_files(
    inputs: list[str],
    model_name: str = 'nisqa',
    device: Optional[str] = None,
    recursive: bool = False,
    progress_callback=None,
) -> list[tuple[Path, float, float]]:
    """Resolve inputs and return MOS scores for each audio file."""
    resolved_device = device or default_device()
    audio_files = expand_audio_inputs(inputs, recursive=recursive)
    if not audio_files:
        raise FileNotFoundError(
            'No audio files found. Pass a file, directory, or glob like "samples/*.wav".'
        )

    model = load_model(model_name, resolved_device)
    results: list[tuple[Path, float, float]] = []
    total_files = len(audio_files)
    for index, audio_file in enumerate(audio_files, start=1):
        mean, variance = predict(str(audio_file), model, resolved_device)
        results.append((audio_file, mean, variance))
        if progress_callback is not None:
            progress_callback(index, total_files, audio_file)

    return results


def main():
    parser = argparse.ArgumentParser(
        description='DNSMOS Pro - Predict speech quality MOS scores',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  dnsmospro speech.wav
  dnsmospro samples/*.wav
  dnsmospro recordings/ --recursive --verbose
        """
    )
    parser.add_argument(
        'audio_files',
        nargs='+',
        help='Audio files, directories, or glob patterns to analyze'
    )
    parser.add_argument(
        '--model', '-m',
        choices=list(MODELS.keys()),
        default='nisqa',
        help='Model to use (default: nisqa)'
    )
    parser.add_argument(
        '--device', '-d',
        default=default_device(),
        help='Device: cpu, mps, or cuda (default: auto-detect)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show variance alongside MOS'
    )
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='When a directory or glob is given, include files in subfolders'
    )

    args = parser.parse_args()

    try:
        results = score_audio_files(
            args.audio_files,
            model_name=args.model,
            device=args.device,
            recursive=args.recursive,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    for audio_file, mean, variance in results:
        if args.verbose:
            print(f"{audio_file}: MOS={mean:.2f} (var={variance:.4f})")
        else:
            print(f"{audio_file}: {mean:.2f}")


if __name__ == '__main__':
    main()
