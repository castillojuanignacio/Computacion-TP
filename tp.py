import os
import pandas as pd

SALIDA_TXT = "salida.txt"


def emitir(lineas_salida, texto=""):
    """
    Muestra una línea por pantalla y también la guarda en la lista de salida.
    """
    print(texto)
    lineas_salida.append(str(texto))


def guardar_salida(lineas_salida, path_salida=SALIDA_TXT):
    """
    Guarda todo el informe generado en un archivo de texto.
    """
    with open(path_salida, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(lineas_salida))
        archivo.write("\n")

    print(f"\nInforme guardado correctamente en: {path_salida}")


def numero_sucursal(valor):
    """
    Convierte valores tipo 'SUC1', 'SUC12', etc. a entero.
    """
    texto = str(valor).replace("SUC", "").strip()
    return int(texto)


def clave_orden(registro):
    """
    Clave de ordenamiento:
    1) sucursal
    2) codigo de producto
    """
    return (numero_sucursal(registro["PRSUC"]), str(registro["PRCOD"]))


def ordenar_csv_burbuja(path_entrada, path_salida, lineas_salida):
    """
    Lee un CSV desordenado, lo ordena con burbuja y genera un nuevo CSV ordenado.
    """
    df = pd.read_csv(path_entrada)

    registros = df.to_dict(orient="records")
    n = len(registros)

    for i in range(n - 1):
        intercambio = False

        for j in range(n - 1 - i):
            if clave_orden(registros[j]) > clave_orden(registros[j + 1]):
                aux = registros[j]
                registros[j] = registros[j + 1]
                registros[j + 1] = aux
                intercambio = True

        if not intercambio:
            break

    df_ordenado = pd.DataFrame(registros, columns=df.columns)
    df_ordenado.to_csv(path_salida, index=False)

    emitir(lineas_salida, "")
    emitir(lineas_salida, "Archivo temporal ordenado generado correctamente.")
    emitir(lineas_salida, f"Ruta: {path_salida}")

    return path_salida


def procesar_compras(path_csv, lineas_salida):
    """
    Procesa el archivo ya ordenado y emite el informe.
    """
    df = pd.read_csv(path_csv)

    registros = df.to_dict(orient="records")

    n = len(registros)
    i = 0
    cansuc = 0
    totalimp = 0.0

    emitir(lineas_salida, "")
    emitir(lineas_salida, "=" * 60)
    emitir(lineas_salida, "INFORME DE COMPRAS")
    emitir(lineas_salida, "=" * 60)

    while i < n:
        suc_actual = registros[i]["PRSUC"]
        cansuc += 1

        totsuc = 0

        myprod = None
        myimpor = -1

        mnprod = None
        mnimpor = float("inf")

        emitir(lineas_salida, f"\nSucursal: {suc_actual}")

        while i < n and registros[i]["PRSUC"] == suc_actual:
            prod_actual = registros[i]["PRCOD"]

            totuni = 0
            totpes = 0.0

            while (
                i < n
                and registros[i]["PRSUC"] == suc_actual
                and registros[i]["PRCOD"] == prod_actual
            ):
                cantidad = int(registros[i]["PRCANT"])
                precio = float(registros[i]["PRPRE"])
                importe = cantidad * precio

                totuni += cantidad
                totpes += importe

                i += 1

            emitir(
                lineas_salida,
                f"  Producto {prod_actual} -> TOTUNI: {totuni} | TOTPES: ${totpes:.2f}"
            )

            totsuc += totuni
            totalimp += totpes

            if totpes > myimpor:
                myimpor = totpes
                myprod = prod_actual

            if totpes < mnimpor:
                mnimpor = totpes
                mnprod = prod_actual

        emitir(lineas_salida, f"  TOTSUC  : {totsuc}")
        emitir(lineas_salida, f"  MYPROD  : {myprod} | MYIMPOR: ${myimpor:.2f}")
        emitir(lineas_salida, f"  MNPROD  : {mnprod} | MNIMPOR: ${mnimpor:.2f}")

    emitir(lineas_salida, "")
    emitir(lineas_salida, "=" * 60)
    emitir(lineas_salida, "TOTALES GENERALES")
    emitir(lineas_salida, "=" * 60)
    emitir(lineas_salida, f"CANSUC   : {cansuc}")
    emitir(lineas_salida, f"TOTALIMP : ${totalimp:.2f}")


def pedir_opcion_ordenado():
    """
    Pide al usuario si el archivo ya está ordenado.
    """
    while True:
        opcion = input("El archivo está ordenado? (Y/N): ").strip().upper()

        if opcion in ("Y", "N"):
            return opcion

        print("Opción inválida. Ingrese Y o N.")


def main():
    lineas_salida = []

    emitir(lineas_salida, "=" * 60)
    emitir(lineas_salida, "PROCESAMIENTO DE COMPRAS")
    emitir(lineas_salida, "=" * 60)

    path_csv = input("Indique el path del csv: ").strip()

    while path_csv == "":
        print("Debe ingresar una ruta válida.")
        path_csv = input("Indique el path del csv: ").strip()

    emitir(lineas_salida, f"Archivo indicado: {path_csv}")

    opcion = pedir_opcion_ordenado()
    emitir(lineas_salida, f"Archivo ordenado: {opcion}")

    try:
        if opcion == "N":
            carpeta = os.path.dirname(path_csv)
            nombre_base = os.path.splitext(os.path.basename(path_csv))[0]
            path_temporal = os.path.join(
                carpeta if carpeta else ".",
                f"{nombre_base}_temporal_ordenado.csv"
            )

            path_a_procesar = ordenar_csv_burbuja(
                path_csv,
                path_temporal,
                lineas_salida
            )
        else:
            path_a_procesar = path_csv

        procesar_compras(path_a_procesar, lineas_salida)
        guardar_salida(lineas_salida)

    except FileNotFoundError:
        emitir(lineas_salida, "")
        emitir(lineas_salida, "Error: no se encontró el archivo indicado.")
        guardar_salida(lineas_salida)

    except KeyError as e:
        emitir(lineas_salida, "")
        emitir(lineas_salida, f"Error: falta la columna {e} en el CSV.")
        guardar_salida(lineas_salida)

    except Exception as e:
        emitir(lineas_salida, "")
        emitir(lineas_salida, f"Ocurrió un error: {e}")
        guardar_salida(lineas_salida)


if __name__ == "__main__":
    main()