#!/bin/bash
cd /workspaces/Aws

if [ -z "${DISCORD_BOT_TOKEN:-}" ]; then
  echo "ERROR: DISCORD_BOT_TOKEN missing"
  exit 1
fi

mkdir -p logs
nohup .venv/bin/python bot/main.py > logs/bot.log 2>&1 < /dev/null &
echo "Bot startup requested."
