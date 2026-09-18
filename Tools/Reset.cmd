@echo off
setlocal
title Reset System Cursors

:: ============================================================================
:: Reset.cmd - Cursor Concept System Maintenance Utility
:: Purpose: Self-elevates with Administrator rights to safely purge legacy/test
::          cursor folders from C:\Windows\Cursors, keeping only the active suite.
:: ============================================================================

:: Check for Administrative Permissions and Self-Elevate
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting Administrator privileges to reset C:\Windows\Cursors...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

echo ======================================================================
echo           Resetting and Cleaning C:\Windows\Cursors
echo ======================================================================
echo.

if exist "C:\Windows\Cursors\Moga-Dark-Free" (
    echo Removing "C:\Windows\Cursors\Moga-Dark-Free"...
    rd /s /q "C:\Windows\Cursors\Moga-Dark-Free"
)

if exist "C:\Windows\Cursors\Moga-Purple-Black" (
    echo Removing "C:\Windows\Cursors\Moga-Purple-Black"...
    rd /s /q "C:\Windows\Cursors\Moga-Purple-Black"
)

if exist "C:\Windows\Cursors\Moga-Purple-White" (
    echo Removing "C:\Windows\Cursors\Moga-Purple-White"...
    rd /s /q "C:\Windows\Cursors\Moga-Purple-White"
)

echo.
echo ======================================================================
echo [SUCCESS] Old folders deleted! 
echo The clean folder "Moga Purple (White Outline)" (with all 34 cursors) remains.
echo ======================================================================
echo.
timeout /t 3 >nul
exit /b 0
