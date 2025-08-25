@echo off
cls

:: Define a variável para o link do repositório
set REPO_URL=http://binario.caixa:8081/repository/pypi-repo/simple/
set TRUSTED_HOST=binario.caixa
set DRIVER_PATH=%cd%\bin\Driver\webdriver.exe

:: Verifica se o Selenium está instalado
pip show selenium >nul 2>&1
if errorlevel 1 (
    echo Selenium nao encontrado, instalando...
    pip install selenium --quiet --index-url %REPO_URL% --trusted-host %TRUSTED_HOST%
) else (
    echo Selenium ja esta instalado, pulando instalacao...
)

:: Verifica se o BuiltFullSoap4 está instalado
pip show bs4 >nul 2>&1
if errorlevel 1 (
    echo BuiltFullSoap4 nao encontrado, instalando...
    pip install bs4 --quiet --index-url %REPO_URL% --trusted-host %TRUSTED_HOST%
) else (
    echo BuiltFullSoap4 ja esta instalado, pulando instalacao...
)

cls
echo ==============================================
echo =           INSIRA O NUMERO DO IB            =
echo ==============================================
set /p IB=Numero do IB: 

cls
echo ==============================================
echo =           INSIRA SEU USUARIO               =
echo ==============================================
set /p USER=Seu Usuario: 

cls
echo ==============================================
echo =           INSIRA SUA SENHA                 =
echo ==============================================
set /p PASSWORD=Sua Senha: <nul
for /f "delims=" %%P in ('powershell -Command "$password = Read-Host -AsSecureString; $password = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)); Write-Output $password"') do set PASSWORD=%%P
cls
echo Executando programa...
py "%cd%\bin\criar_tarefas.py" --ib "%IB%" --user "%USER%" --password "%PASSWORD%" --driver-path "%DRIVER_PATH%"
pause