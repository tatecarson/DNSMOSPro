# -*- mode: python ; coding: utf-8 -*-

import sys

from PyInstaller.utils.hooks import collect_data_files, collect_submodules


datas = [
    ("runs/NISQA/model_best.pt", "runs/NISQA"),
    ("runs/BVCC/model_best.pt", "runs/BVCC"),
    ("runs/VCC2018/model_best.pt", "runs/VCC2018"),
]
datas += collect_data_files("librosa")
datas += collect_data_files("soundfile")

hiddenimports = []
hiddenimports += collect_submodules("librosa")
hiddenimports += collect_submodules("numba")
hiddenimports += collect_submodules("soundfile")
hiddenimports += collect_submodules("scipy")
hiddenimports += collect_submodules("sklearn")
hiddenimports += collect_submodules("soxr")


a = Analysis(
    ["gui.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="DNSMOS Pro",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="DNSMOS Pro.app",
        icon=None,
        bundle_identifier="com.dnsmospro.app",
    )
else:
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=False,
        upx_exclude=[],
        name="DNSMOS Pro",
    )
