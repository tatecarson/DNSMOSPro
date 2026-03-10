@echo off
setlocal

set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%"

set PYTHON_BIN=python
set VENV_DIR=.build-standalone-venv

where %PYTHON_BIN% >nul 2>nul
if errorlevel 1 (
  echo Python 3 is required but was not found in PATH.
  exit /b 1
)

for /f %%i in ('%PYTHON_BIN% -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do set PYTHON_VERSION=%%i
if not "%PYTHON_VERSION%"=="3.11" if not "%PYTHON_VERSION%"=="3.12" (
  echo Standalone builds should use Python 3.11 or 3.12.
  echo Current interpreter: %PYTHON_VERSION% ^(%PYTHON_BIN%^)
  exit /b 1
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
  echo Creating build environment in %VENV_DIR% ...
  %PYTHON_BIN% -m venv %VENV_DIR%
)

echo Installing build dependencies ...
%VENV_DIR%\Scripts\python.exe -m pip install --upgrade pip
%VENV_DIR%\Scripts\python.exe -m pip install pyinstaller torch
%VENV_DIR%\Scripts\python.exe -m pip install -e .

echo Building standalone app ...
%VENV_DIR%\Scripts\pyinstaller.exe --clean --noconfirm standalone.spec

echo.
echo Build complete.
echo Portable folder: dist\DNSMOS Pro
echo Build on each target operating system, or use the GitHub Actions matrix workflow.
