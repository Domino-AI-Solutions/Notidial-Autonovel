@echo off
:: ============================================================================
:: One-Time Setup for Automatic-Writing
:: This script creates separate virtual environments and installs dependencies
:: for the main pipeline and for the FastSD server.
:: ============================================================================

echo [INFO] Setting up virtual environment for Automatic-Writing project...
echo.

:: Create a local venv for this project if it doesn't exist
if not exist venv\Scripts\activate.bat (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)
if not exist venv\Scripts\activate.bat (
    echo [ERROR] Failed to create the project virtual environment. Please ensure Python is installed and in your PATH.
    if not "%NON_INTERACTIVE%"=="1" pause
    exit /b 1
)

echo.
echo [INFO] Installing dependencies from requirements.txt...
echo.
call venv\Scripts\activate.bat && python -m pip install --upgrade pip
call venv\Scripts\activate.bat && python -m pip install --prefer-binary -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies from requirements.txt.
    echo [ERROR] Please check your internet connection and run this setup again.
    if not "%NON_INTERACTIVE%"=="1" pause
    exit /b 1
)

echo.
echo [INFO] Setting up virtual environment for FastSD-CPU...
echo.
set "FASTSD_DIR=C:\Users\opera\OneDrive\Desktop\Github-Repository\fastsdcpu"

:: Use the official install script for FastSD-CPU only if it is not already installed
if exist "%FASTSD_DIR%\venv" (
    echo [INFO] FastSD-CPU virtual environment already exists at "%FASTSD_DIR%\venv". Skipping install.
) else (
    if exist "%FASTSD_DIR%\install.bat" (
        echo [INFO] Running FastSD-CPU's install.bat script...
        call "%FASTSD_DIR%\install.bat"
    ) else (
        echo [ERROR] FastSD-CPU install.bat not found at "%FASTSD_DIR%".
        if not "%NON_INTERACTIVE%"=="1" pause
        exit /b 1
    )
)

echo.
echo [SUCCESS] Project setup is complete! You can now use the launcher.
if not "%NON_INTERACTIVE%"=="1" pause
