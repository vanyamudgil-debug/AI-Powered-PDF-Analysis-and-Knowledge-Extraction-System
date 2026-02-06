@echo off
cd /d "%~dp0"

echo [INFO] Checking for Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python from python.org and tick "Add Python to PATH".
    pause
    exit /b
)

if not exist "venv" (
    echo [INFO] Virtual environment not found. Creating one now...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b
    )
    echo [INFO] Virtual environment created successfully.
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate

echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

if exist "requirements.txt" (
    echo [INFO] Installing dependencies from requirements.txt...
    pip install -r requirements.txt
) else (
    echo [WARNING] requirements.txt not found! Skipping installation.
)

echo [INFO] Installation complete. Launching the application...
echo.
echo [INFO] The application will open in your default browser.
echo [INFO] Press Ctrl+C in this window to stop the server.
echo.

python -m streamlit run app.py

pause