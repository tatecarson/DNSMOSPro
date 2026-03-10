@echo off
setlocal

set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%"

set PYTHON_BIN=python
set VENV_DIR=.venv
where %PYTHON_BIN% >nul 2>nul
if errorlevel 1 (
  echo Python is required but was not found in PATH.
  exit /b 1
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
  echo Creating virtual environment in %VENV_DIR% ...
  %PYTHON_BIN% -m venv %VENV_DIR%
) else (
  echo Using existing virtual environment in %VENV_DIR% ...
)

echo Upgrading pip ...
%VENV_DIR%\Scripts\python.exe -m pip install --upgrade pip

echo Installing PyTorch ...
%VENV_DIR%\Scripts\python.exe -m pip install torch

echo Installing DNSMOS Pro ...
%VENV_DIR%\Scripts\python.exe -m pip install -e .

echo.
echo Install complete.
echo Activate with: %VENV_DIR%\Scripts\activate
echo CLI: dnsmospro path\to\audio.wav
echo GUI: dnsmospro-gui
