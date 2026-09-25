@echo off
chcp 65001 >nul
title ПРОЕКТСЕТЬ BOT
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
  echo Python не найден.
  echo Установите Python 3.11 или новее с https://www.python.org/downloads/
  echo При установке включите Add Python to PATH.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Создаю локальное окружение...
  py -3 -m venv .venv
)

echo [2/3] Проверяю зависимости...
".venv\Scripts\python.exe" -m pip install -q -r requirements.txt

if not exist ".env" (
  echo.
  echo Первый запуск.
  echo Сейчас будет создан файл .env.
  set /p BOT_TOKEN="Вставьте токен BotFather и нажмите Enter: "
  >.env echo TELEGRAM_BOT_TOKEN=%BOT_TOKEN%
  echo Токен сохранён локально в .env и не отправляется в GitHub.
)

echo [3/3] Запускаю ПРОЕКТСЕТЬ...
echo.
echo Не закрывайте это окно, пока бот должен работать.
echo Для остановки нажмите Ctrl+C.
echo.
".venv\Scripts\python.exe" bot.py

echo.
echo Бот остановлен.
pause
