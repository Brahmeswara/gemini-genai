@echo off
IF "%CONFIG_FILE%"=="" (
    echo Error: CONFIG_FILE environment variable is not set.
    exit /b 1
)
IF "%GENAI_API_KEY%"=="" (
    echo Error: GENAI_API_KEY environment variable is not set.
    exit /b 1
)

IF "%MPH_GENAI_FW_HOME%"=="" (
    echo Error: MPH_GENAI_FW_HOME environment variable is not set.
    exit /b 1
)
IF "%BASE_PROJECT_FOLDER%"=="" (
    echo Error: BASE_PROJECT_FOLDER environment variable is not set.
    exit /b 1
)
::IF "%GENAI_OUTPUT_FILE%"=="" (
::    echo Error: GENAI_OUTPUT_FILE environment variable is not set.
::   exit /b 1
::)
echo All required environment variables are set.

set PYTHONPATH=%MPH_GENAI_FW_HOME%;%MPH_GENAI_FW_HOME%\core;%MPH_GENAI_FW_HOME%\tools


echo Changing directory to %MPH_GENAI_FW_HOME%
cd %MPH_GENAI_FW_HOME%
echo GENAI_OUTPUT_FILE: %GENAI_OUTPUT_FILE%
:: python tools\ttj.py
python mph-decorator.py
echo 'Done.'
