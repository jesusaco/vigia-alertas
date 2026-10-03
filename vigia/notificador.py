"""Envío de mensajes. Telegram si hay credenciales; si no, consola (modo prueba)."""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Protocol


class Notificador(Protocol):
    def enviar(self, texto: str) -> None: ...


class Consola:
    def enviar(self, texto: str) -> None:
        print(f"[aviso] {texto}")


class Telegram:
    def __init__(self, token: str, chat_id: str, timeout: float = 10):
        self._url = f"https://api.telegram.org/bot{token}/sendMessage"
        self._chat_id = chat_id
        self._timeout = timeout

    def enviar(self, texto: str) -> None:
        datos = urllib.parse.urlencode({"chat_id": self._chat_id, "text": texto}).encode()
        with urllib.request.urlopen(self._url, data=datos, timeout=self._timeout) as r:
            resp = json.loads(r.read().decode("utf-8"))
        if not resp.get("ok"):
            raise RuntimeError(f"Telegram rechazó el mensaje: {resp.get('description')}")


def desde_entorno() -> Notificador:
    """Lee TELEGRAM_TOKEN y TELEGRAM_CHAT_ID. Las claves nunca van en el código."""
    token, chat = os.getenv("TELEGRAM_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    if token and chat:
        return Telegram(token, chat)
    print("[vigia] sin TELEGRAM_TOKEN/TELEGRAM_CHAT_ID: modo consola")
    return Consola()
