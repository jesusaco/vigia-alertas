"""Fuentes de datos. Cada fuente es una función sin argumentos que devuelve un float.

Incluye una fuente de ejemplo con la API pública de Binance (no requiere claves)
y una genérica para cualquier endpoint JSON.
"""
from __future__ import annotations

import json
import time
import urllib.request
from typing import Callable

Fuente = Callable[[], float]


def http_json(url: str, timeout: float = 10, intentos: int = 3) -> object:
    """GET con reintentos y espera creciente ante errores de red."""
    ultimo_error: Exception | None = None
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "vigia-alertas/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except (OSError, ValueError) as e:
            ultimo_error = e
            time.sleep(2 ** i)
    raise RuntimeError(f"no se pudo leer {url}: {ultimo_error}")


def json_campo(url: str, *ruta: str | int) -> Fuente:
    """Fuente genérica: lee un campo numérico de un JSON. Ej.: json_campo(url, "data", 0, "precio")."""
    def leer() -> float:
        dato = http_json(url)
        for clave in ruta:
            dato = dato[clave]  # type: ignore[index]
        return float(dato)  # type: ignore[arg-type]
    return leer


def binance_cambio_24h(simbolo: str) -> Fuente:
    """Variación porcentual absoluta en 24 h de un par spot (API pública, sin claves)."""
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={simbolo.upper()}"
    def leer() -> float:
        return abs(float(http_json(url)["priceChangePercent"]))  # type: ignore[index]
    return leer
