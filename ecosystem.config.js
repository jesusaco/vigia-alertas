// pm2 start ecosystem.config.js
module.exports = {
  apps: [
    {
      name: "vigia-btc",
      script: "python3",
      args: "-m vigia --simbolo BTCUSDT --entra 5 --sale 4 --intervalo 120",
      cwd: __dirname,
      autorestart: true,
      max_restarts: 20,
      restart_delay: 10000,
      // Las credenciales se cargan desde el entorno del shell que lanza pm2 (ver .env.example)
    },
  ],
};
