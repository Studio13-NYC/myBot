REM venv-util.bat
@echo off
if not exist .venv (
    echo Creating virtual environment...
    py -m venv .venv
)
echo Changing to .venv\Scripts directory...
cd .venv\Scripts
echo Activating virtual environment...
call activate.bat
echo Going back to the project root folder...
cd ..\..
echo You're now in the project root folder with the virtual environment activated.
cmd /k