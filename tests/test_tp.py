import os
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from tp import numero_sucursal, clave_orden, ordenar_csv_burbuja, pedir_opcion_ordenado


class TestProcesamientoCompras(unittest.TestCase):

    def test_numero_sucursal_convierte_suc_a_entero(self):
        resultado = numero_sucursal("SUC12")
        self.assertEqual(resultado, 12)

    def test_clave_orden_ordena_por_sucursal_y_producto(self):
        registro = {
            "PRSUC": "SUC2",
            "PRCOD": "A10"
        }

        resultado = clave_orden(registro)

        self.assertEqual(resultado, (2, "A10"))

    def test_ordenar_csv_burbuja_genera_archivo_ordenado(self):
        with tempfile.TemporaryDirectory() as carpeta:
            path_entrada = os.path.join(carpeta, "compras.csv")
            path_salida = os.path.join(carpeta, "compras_ordenado.csv")

            df = pd.DataFrame([
                {"PRSUC": "SUC2", "PRCOD": "B", "PRCANT": 1, "PRPRE": 10},
                {"PRSUC": "SUC1", "PRCOD": "C", "PRCANT": 1, "PRPRE": 20},
                {"PRSUC": "SUC1", "PRCOD": "A", "PRCANT": 1, "PRPRE": 30},
            ])

            df.to_csv(path_entrada, index=False)

            lineas_salida = []
            ordenar_csv_burbuja(path_entrada, path_salida, lineas_salida)

            df_ordenado = pd.read_csv(path_salida)

            sucursales = list(df_ordenado["PRSUC"])
            productos = list(df_ordenado["PRCOD"])

            self.assertEqual(sucursales, ["SUC1", "SUC1", "SUC2"])
            self.assertEqual(productos, ["A", "C", "B"])

    def test_pedir_opcion_ordenado_acepta_y(self):
        with patch("builtins.input", return_value="Y"):
            resultado = pedir_opcion_ordenado()

        self.assertEqual(resultado, "Y")

    def test_pedir_opcion_ordenado_reintenta_si_la_opcion_es_invalida(self):
        with patch("builtins.input", side_effect=["X", "N"]):
            resultado = pedir_opcion_ordenado()

        self.assertEqual(resultado, "N")
    
    def test_error_intencional_para_simular_pipeline_fallida(self):
        resultado = numero_sucursal("SUC12")
        self.assertEqual(resultado, 99)


if __name__ == "__main__":
    unittest.main()