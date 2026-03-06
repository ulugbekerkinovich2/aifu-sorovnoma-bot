module.exports = {
  apps: [
    {
      name: "aifu-survey-bot",
      script: "bot.py",
      cwd: "/var/www/workers/aifu-sorovnoma-bot",
      interpreter: "/var/www/workers/aifu-sorovnoma-bot/venv/bin/python",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "300M",
      env: {
        PYTHONUNBUFFERED: "1"
      },
      error_file: "/var/www/workers/aifu-sorovnoma-bot/logs/error.log",
      out_file: "/var/www/workers/aifu-sorovnoma-bot/logs/out.log",
      log_file: "/var/www/workers/aifu-sorovnoma-bot/logs/combined.log",
      time: true
    }
  ]
};
