"""Ejemplo de uso: alerta cuando un par de Binance se mueve más de X% en 24 h.

    python -m vigia --simbolo BTCUSDT --entra 5 --sale 4
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .avisador import Avisador
from .fuentes import binance_cambio_24h
from .notificador import desde_entorno
from .vigia import Vigia


def main() -> None:
    p = argparse.ArgumentParser(description="Vigía con alertas por Telegram")
    p.add_argument("--simbolo", default="BTCUSDT")
    p.add_argument("--entra", type=float, default=5.0, help="%% de cambio 24h para entrar en alerta")
    p.add_argument("--sale", type=float, default=4.0, help="%% para volver a normal")
    p.add_argument("--freno", type=float, default=1800, help="segundos mínimos entre cambios")
    p.add_argument("--intervalo", type=float, default=120, help="segundos entre lecturas")
    p.add_argument("--estado", type=Path, default=Path("estado"))
    p.add_argument("--ciclos", type=int, default=None, help="para pruebas; por defecto corre siempre")
    a = p.parse_args()

    Vigia(
        nombre=f"{a.simbolo} cambio 24h %",
        fuente=binance_cambio_24h(a.simbolo),
        avisador=Avisador(entra=a.entra, sale=a.sale, freno_s=a.freno),
        notificador=desde_entorno(),
        ruta_estado=a.estado / f"{a.simbolo.lower()}.json",
        intervalo_s=a.intervalo,
    ).correr(max_ciclos=a.ciclos)


if __name__ == "__main__":
    main()
