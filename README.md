# vigia-alertas

Vigía en Python que lee una métrica cada pocos minutos y avisa por Telegram **solo cuando algo cambia de verdad**.
Pensado para correr 24/7 en un VPS con pm2, sobrevivir reinicios y no saturar de mensajes.

*English below.*

## Qué resuelve

Un bot de alertas ingenuo manda un mensaje cada vez que el valor cruza el umbral. Si el valor oscila cerca
del umbral, eso son decenas de mensajes por hora. Este vigía usa tres ideas:

| Idea | Cómo |
|---|---|
| **Histéresis** | Un umbral para entrar en alerta (`entra`) y otro, más bajo, para salir (`sale`). Oscilar entre ambos no genera mensajes. |
| **Freno de tiempo** | Mínimo de segundos entre dos cambios de estado (`freno_s`). |
| **Estado persistente** | El estado se guarda en JSON con escritura atómica. Tras un reinicio, el vigía no repite una alerta ya enviada. |

Además: reintentos con espera creciente ante errores de red, un error en un ciclo no mata el proceso,
y sin dependencias externas (solo la biblioteca estándar de Python 3.10+).

## Uso rápido

```bash
# modo consola (sin Telegram): imprime los avisos
python -m vigia --simbolo BTCUSDT --entra 5 --sale 4

# con Telegram
cp .env.example .env    # completa TELEGRAM_TOKEN y TELEGRAM_CHAT_ID
set -a; . ./.env; set +a
python -m vigia --simbolo ETHUSDT --entra 6 --sale 5 --intervalo 120
```

El ejemplo vigila la variación de 24 h de un par en la API **pública** de Binance (no requiere claves).
Para vigilar otra cosa, cualquier función sin argumentos que devuelva un `float` sirve como fuente:

```python
from pathlib import Path
from vigia import Avisador, Vigia
from vigia.fuentes import json_campo
from vigia.notificador import desde_entorno

Vigia(
    nombre="Cola de pedidos",
    fuente=json_campo("https://mi-api.example.com/stats", "cola", "pendientes"),
    avisador=Avisador(entra=500, sale=300, freno_s=900),
    notificador=desde_entorno(),
    ruta_estado=Path("estado/cola.json"),
).correr()
```

## Correr 24/7 con pm2

```bash
pm2 start ecosystem.config.js
pm2 save && pm2 startup   # vuelve solo tras reiniciar el servidor
```

## Tests

```bash
python -m unittest discover -s tests -t . -v
```

Cubren la histéresis, el freno de tiempo, la escritura atómica, un archivo de estado corrupto,
que un reinicio no repita alertas y que un error de red no tumbe el proceso.

## Seguridad

Las credenciales se leen de variables de entorno y nunca van en el código. `.env` está en `.gitignore`.

---

## English

A Python watcher that polls a metric and sends a Telegram message **only when its state really changes**.
Built to run 24/7 on a VPS under pm2, survive reboots and avoid alert floods.

- **Hysteresis**: separate enter/exit thresholds, so values oscillating around one threshold don't spam.
- **Cooldown**: minimum seconds between state changes.
- **Persistent state**: atomic JSON writes; after a restart it never repeats an alert already sent.
- Retries with backoff, a failing cycle never kills the process, standard library only (Python 3.10+).

Quick start: `python -m vigia --simbolo BTCUSDT --entra 5 --sale 4` (console mode; set `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID` for Telegram).
Any zero-argument function returning a `float` can be a data source. Run tests with
`python -m unittest discover -s tests -t . -v`.

## Licencia / License

MIT
