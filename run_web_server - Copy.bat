cd /d %~dp0

cmd.exe /K "conda activate iot_env & python.exe server.py 80"

rem http://localhost