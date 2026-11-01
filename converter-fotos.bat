@echo off
setlocal
cd /d "%~dp0"
python scripts\convert_webp.py %*
set "conversion_exit=%ERRORLEVEL%"
echo.
if not "%conversion_exit%"=="0" echo A conversao encontrou erros. Veja as mensagens acima.
pause
exit /b %conversion_exit%
