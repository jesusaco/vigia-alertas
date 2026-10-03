"""Bucle principal: lee la fuente, decide con el Avisador, notifica y guarda estado."""
from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from . import estado
from .avisador import Avisador
from .fuentes import Fuente
from .notificador import Notificador


@dataclass
class Vigia:
    nombre: str
    fuente: Fuente
    avisador: Avisador
    notificador: Notificador
    ruta_estado: Path
    intervalo_s: float = 120
    reloj: Callable[[], float] = time.time

    def __post_init__(self) -> None:
        # Retoma donde quedó: tras un reinicio no repite una alerta ya enviada.
        self.avisador.cargar(estado.leer(self.ruta_estado))

    def ciclo(self) -> Optional[str]:
        valor = self.fuente()
        cambio = self.avisador.evaluar(valor, self.reloj())
        if cambio:
            umbral = self.avisador.entra if cambio == "ALERTA" else self.avisador.sale
            signo = ">" if cambio == "ALERTA" else "<"
            self.notificador.enviar(f"{self.nombre}: {cambio} · valor {valor:.4g} {signo} {umbral:g}")
            estado.guardar(self.ruta_estado, self.avisador.a_dict())
        return cambio

    def correr(self, max_ciclos: Optional[int] = None) -> None:
        n = 0
        while max_ciclos is None or n < max_ciclos:
            try:
                self.ciclo()
            except Exception as e:  # un error de red no debe matar el proceso
                print(f"[{self.nombre}] error en el ciclo: {e}")
            n += 1
            if max_ciclos is None or n < max_ciclos:
                time.sleep(self.intervalo_s)
