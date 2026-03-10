#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON:-python3}"
VENV_DIR=".venv"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python 3 is required but was not found."
  exit 1
fi

if [ ! -x "$VENV_DIR/bin/python" ] || [ ! -x "$VENV_DIR/bin/pip" ]; then
  echo "Creating virtual environment in $VENV_DIR ..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
else
  echo "Using existing virtual environment in $VENV_DIR ..."
fi

echo "Upgrading pip ..."
"$VENV_DIR/bin/python" -m pip install --upgrade pip

echo "Installing PyTorch ..."
"$VENV_DIR/bin/python" -m pip install torch

echo "Installing DNSMOS Pro ..."
"$VENV_DIR/bin/python" -m pip install -e .

echo
echo "Install complete."
echo "Activate with: source $VENV_DIR/bin/activate"
echo "CLI: dnsmospro path/to/audio.wav"
echo "GUI: dnsmospro-gui"
