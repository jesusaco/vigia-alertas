import json
import tempfile
import unittest
from pathlib import Path

from vigia import Avisador, Vigia
from vigia import estado


class Recolector:
    def __init__(self):
        self.mensajes = []

    def enviar(self, texto):
        self.mensajes.append(texto)


class TestAvisador(unittest.TestCase):
    def test_histeresis_evita_rebotes(self):
        a = Avisador(entra=5, sale=4, freno_s=0)
        self.assertEqual(a.evaluar(5.1, 0), "ALERTA")
        # oscila entre 4 y 5: sigue en alerta, sin mensajes nuevos
        for t, v in enumerate([4.9, 4.2, 4.8, 4.1], start=1):
            self.assertIsNone(a.evaluar(v, t))
        self.assertEqual(a.evaluar(3.9, 10), "NORMAL")

    def test_freno_de_tiempo(self):
        a = Avisador(entra=5, sale=4, freno_s=60)
        self.assertEqual(a.evaluar(6, 0), "ALERTA")
        self.assertIsNone(a.evaluar(3, 30))       # demasiado pronto
        self.assertEqual(a.evaluar(3, 61), "NORMAL")

    def test_umbrales_invertidos_fallan(self):
        with self.assertRaises(ValueError):
            Avisador(entra=4, sale=5)


class TestEstado(unittest.TestCase):
    def test_guardar_y_leer(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "sub" / "e.json"
            estado.guardar(p, {"alerta": True})
            self.assertEqual(estado.leer(p), {"alerta": True})
            self.assertEqual([x.name for x in p.parent.iterdir()], ["e.json"])  # sin temporales

    def test_archivo_corrupto_no_rompe(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "e.json"
            p.write_text("{no es json")
            self.assertEqual(estado.leer(p), {})


class TestVigia(unittest.TestCase):
    def _vigia(self, valores, ruta, rec, reloj):
        it = iter(valores)
        return Vigia("prueba", lambda: next(it), Avisador(5, 4, freno_s=0), rec, ruta,
                     intervalo_s=0, reloj=reloj)

    def test_avisa_solo_en_cambios(self):
        with tempfile.TemporaryDirectory() as d:
            rec, t = Recolector(), iter(range(100))
            v = self._vigia([1, 6, 7, 4.5, 3], Path(d) / "e.json", rec, lambda: next(t))
            v.correr(max_ciclos=5)
            self.assertEqual(len(rec.mensajes), 2)
            self.assertIn("ALERTA", rec.mensajes[0])
            self.assertIn("NORMAL", rec.mensajes[1])

    def test_reinicio_no_repite_alerta(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "e.json"
            rec1 = Recolector()
            self._vigia([6], ruta, rec1, lambda: 0).correr(max_ciclos=1)
            self.assertEqual(json.loads(ruta.read_text())["alerta"], True)
            # "reinicio": proceso nuevo, mismo archivo de estado, el valor sigue alto
            rec2 = Recolector()
            self._vigia([6.5], ruta, rec2, lambda: 1).correr(max_ciclos=1)
            self.assertEqual(rec2.mensajes, [])

    def test_error_de_fuente_no_mata_el_proceso(self):
        def falla():
            raise RuntimeError("sin red")
        with tempfile.TemporaryDirectory() as d:
            v = Vigia("prueba", falla, Avisador(5, 4), Recolector(), Path(d) / "e.json", intervalo_s=0)
            v.correr(max_ciclos=2)  # no lanza


if __name__ == "__main__":
    unittest.main()
