"""Decide cuándo una métrica merece una alerta.

Usa histéresis (un umbral para entrar en alerta y otro para salir) y un freno
de tiempo entre cambios de estado, para que el ruido alrededor del umbral no
se convierta en una lluvia de mensajes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Avisador:
    entra: float            # el valor debe superar esto para pasar a ALERTA
    sale: float             # y bajar de esto para volver a NORMAL
    freno_s: float = 1800   # mínimo de segundos entre dos cambios de estado
    alerta: bool = False
    ultimo_cambio: float = field(default=float("-inf"))

    def __post_init__(self) -> None:
        if self.sale > self.entra:
            raise ValueError("'sale' debe ser <= 'entra' para que haya histéresis")

    def evaluar(self, valor: float, ahora: float) -> Optional[str]:
        """Devuelve "ALERTA" o "NORMAL" solo cuando el estado cambia; si no, None."""
        umbral = self.sale if self.alerta else self.entra
        nuevo = valor > umbral
        if nuevo == self.alerta:
            return None
        if ahora - self.ultimo_cambio < self.freno_s:
            return None
        self.alerta, self.ultimo_cambio = nuevo, ahora
        return "ALERTA" if nuevo else "NORMAL"

    # --- persistencia ---------------------------------------------------
    def a_dict(self) -> dict:
        return {"alerta": self.alerta, "ultimo_cambio": self.ultimo_cambio}

    def cargar(self, d: dict) -> None:
        self.alerta = bool(d.get("alerta", False))
        self.ultimo_cambio = float(d.get("ultimo_cambio", float("-inf")))
