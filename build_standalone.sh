#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON:-python3}"
VENV_DIR=".build-standalone-venv"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python 3 is required but was not found."
  exit 1
fi

PYTHON_VERSION="$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
if [[ "$PYTHON_VERSION" != "3.11" && "$PYTHON_VERSION" != "3.12" ]]; then
  echo "Standalone builds should use Python 3.11 or 3.12."
  echo "Current interpreter: $PYTHON_VERSION ($PYTHON_BIN)"
  exit 1
fi

if [ ! -x "$VENV_DIR/bin/python" ]; then
  echo "Creating build environment in $VENV_DIR ..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

echo "Installing build dependencies ..."
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install pyinstaller torch
"$VENV_DIR/bin/python" -m pip install -e .

echo "Building standalone app ..."
"$VENV_DIR/bin/pyinstaller" --clean --noconfirm standalone.spec

echo
echo "Build complete."
if [ "$(uname)" = "Darwin" ]; then
  echo "App bundle: dist/DNSMOS Pro.app"
else
  echo "Portable folder: dist/DNSMOS Pro"
fi
echo "Build on each target operating system, or use the GitHub Actions matrix workflow."
