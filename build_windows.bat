@echo off
cd /d "%~dp0"
py -3 -m venv .venv
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onedir --windowed --name EDULearningAssistant --hidden-import app --collect-all PIL --collect-all pytesseract windows_launcher.py
if errorlevel 1 goto failed
echo Build complete: dist\EDULearningAssistant
pause
exit /b 0
:failed
echo Build failed. See errors above.
pause
exit /b 1
