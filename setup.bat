@echo off
SETLOCAL EnableDelayedExpansion

echo ======================================================
echo LOS Competition Registration - Setup Script
echo ======================================================
echo.
echo This script will install Python 3.9, pip, and required dependencies
echo for the LOS Competition Registration tool.
echo.
echo Required components that will be installed:
echo  1. Python 3.9.x (if not already installed)
echo  2. pip (included with Python)
echo  3. Required Python packages: requests, tkinter
echo.
echo ======================================================
echo.

REM Check if Python is already installed
python --version > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Python is already installed. Checking version...
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo Detected Python version: %PYTHON_VERSION%
    
    REM Extract major and minor version
    for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
        set PYTHON_MAJOR=%%a
        set PYTHON_MINOR=%%b
    )
    
    if !PYTHON_MAJOR! LSS 3 (
        echo WARNING: Python version is less than 3.x
        set INSTALL_PYTHON=y
    ) else if !PYTHON_MAJOR! EQU 3 (
        if !PYTHON_MINOR! LSS 6 (
            echo WARNING: Python version is less than 3.6
            set INSTALL_PYTHON=y
        ) else (
            echo Python version is compatible, no need to install.
            set INSTALL_PYTHON=n
        )
    ) else (
        echo Python version is compatible, no need to install.
        set INSTALL_PYTHON=n
    )
) else (
    echo Python is not installed or not in PATH.
    set INSTALL_PYTHON=y
)

REM Check if pip is installed
pip --version > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo pip is already installed.
    set INSTALL_PIP=n
) else (
    echo pip is not installed or not in PATH.
    if "%INSTALL_PYTHON%"=="y" (
        echo pip will be installed with Python.
        set INSTALL_PIP=n
    ) else (
        echo Will attempt to install pip.
        set INSTALL_PIP=y
    )
)

REM Install Python if needed
if "%INSTALL_PYTHON%"=="y" (
    echo.
    echo ======================================================
    echo Installing Python 3.9...
    echo ======================================================
    echo.
    echo Downloading Python 3.9.13 installer...
    
    REM Create a temporary directory
    if not exist "temp" mkdir temp
    
    REM Download Python installer
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe' -OutFile 'temp\python-installer.exe'}"
    
    if not exist "temp\python-installer.exe" (
        echo Failed to download Python installer.
        goto ERROR
    )
    
    echo Running Python installer...
    echo Please follow the installation wizard.
    echo IMPORTANT: Make sure to check "Add Python to PATH" option!
    
    start /wait temp\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    echo Python installation completed.
    
    REM Delete temporary files
    rmdir /s /q temp
)

REM Install pip if needed
if "%INSTALL_PIP%"=="y" (
    echo.
    echo ======================================================
    echo Installing pip...
    echo ======================================================
    echo.
    
    REM Create a temporary directory
    if not exist "temp" mkdir temp
    
    echo Downloading get-pip.py...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'temp\get-pip.py'}"
    
    if not exist "temp\get-pip.py" (
        echo Failed to download get-pip.py.
        goto ERROR
    )
    
    echo Installing pip...
    python temp\get-pip.py
    
    echo pip installation completed.
    
    REM Delete temporary files
    rmdir /s /q temp
)

REM Install required Python packages
echo.
echo ======================================================
echo Installing required Python packages...
echo ======================================================
echo.

echo Installing requests...
pip install requests

echo.
echo Checking for tkinter...
python -c "import tkinter" > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo tkinter is not installed or not working properly.
    echo Note: tkinter should be included with Python installation.
    echo Please reinstall Python and make sure to select tkinter during installation.
) else (
    echo tkinter is already installed.
)

REM All done
echo.
echo ======================================================
echo Setup completed successfully!
echo ======================================================
echo.
echo You can now run the LOS Competition Registration application.
echo.
goto END

:ERROR
echo.
echo ======================================================
echo ERROR: Setup failed
echo ======================================================
echo.
echo Please check the error messages above and try again.
echo If the issue persists, you may need to install the components manually.
echo.

:END
pause