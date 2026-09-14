@echo off
setlocal

:: Get the directory of this batch file
set "SCRIPT_DIR=%~dp0"

echo =================================================
echo  Starting All Automatic-Writing Servers...
echo =================================================
echo.

:: 1. Start Ollama Server in a new window
echo [1/3] Launching Ollama server...
start "Ollama Server" cmd /c "ollama serve"

:: 2. Start FastSD CPU Server in a new window (assuming default location)
echo [2/3] Launching FastSD CPU server...
start "FastSD CPU" "C:\Users\opera\OneDrive\Desktop\Github-Repository\fastsdcpu\start.bat"

echo.
echo =================================================
echo  All Servers Started!
echo =================================================
echo.
echo The following servers should now be running in new windows:
echo   - Ollama Server (LLM)
echo   - FastSD CPU Server (Image Generation)