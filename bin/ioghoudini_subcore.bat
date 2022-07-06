@echo off

:: The Houdini bin directory contains a 'hython' executable which wraps
:: a Python session and automatically initializes the session with the
:: Houdini libraries.
hython.exe "%~dp0\ioghoudini_subcore.py" %*
