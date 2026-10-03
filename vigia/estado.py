"""Estado persistente en un archivo JSON, escrito de forma atómica.

Si el proceso se cae o el servidor se reinicia a mitad de una escritura,
el archivo anterior queda intacto: se escribe a un temporal y se renombra.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path


def leer(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        # Un archivo corrupto no debe tumbar el vigía: se empieza de cero y se avisa en el log.
        print(f"[estado] {path} ilegible; se ignora")
        return {}


def guardar(path: Path, datos: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
