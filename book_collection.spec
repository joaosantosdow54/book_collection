# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['book_collection.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('books.db', '.'),     # Include books.db in the root of the dist folder
        ('livros.db', '.'),    # Include livros.db in the root of the dist folder
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='book_collection',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
