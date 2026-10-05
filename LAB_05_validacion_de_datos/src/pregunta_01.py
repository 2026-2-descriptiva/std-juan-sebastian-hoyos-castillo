import json
import re
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "supplier_id",
    "supplier",
    "country",
    "city",
    "purchase_date",
    "amount",
    "discount",
    "weight",
    "units",
    "unit_price",
    "contact_email",
]


def _normalize_column_name(column_name):
    value = str(column_name).replace("\ufeff", "").strip().lower()
    return re.sub(r"\s+", "_", value)


def pregunta_01():
    """
    Antes de limpiar o analizar un conjunto de datos, un analista debe
    documentar qué problemas tiene. En este laboratorio usted no va a limpiar
    `data/ventas.csv.gz`: va a construir un reporte de calidad que deje evidencia
    de sus problemas, tal como están en el archivo.

    Lea `data/ventas.csv.gz` sin modificar sus valores. Para trabajar con los
    encabezados, normalícelos: páselos a minúsculas, elimine los espacios al
    inicio y al final (y cualquier marca BOM) y reemplace los espacios
    internos por `_`. Las columnas requeridas son `supplier_id`, `supplier`,
    `country`, `city`, `purchase_date`, `amount`, `discount`, `weight`,
    `units`, `unit_price` y `contact_email`.

    Escriba el reporte en `submission/data_quality_report.json` con estas
    claves:

    - `row_count`: cantidad de filas de datos.
    - `column_count`: cantidad de columnas.
    - `missing_required_columns`: lista ordenada de columnas requeridas que no
      están en el archivo.
    - `unexpected_columns`: lista ordenada de columnas del archivo que no son
      requeridas.
    - `duplicate_row_count`: cantidad de filas idénticas a una fila anterior.
    - `duplicate_supplier_id_row_count`: cantidad de filas cuyo `supplier_id`
      aparece más de una vez (cuente todas esas filas, no solo las
      repetidas).
    - `missing_value_count_by_column`: diccionario con la cantidad de valores
      faltantes de cada columna. Considere faltantes las celdas vacías y las
      que contienen `N/A`.
    - `invalid_email_count`: cantidad de valores de `contact_email` que no
      tienen la forma `usuario@dominio.extension`.
    - `invalid_unit_count`: cantidad de valores numéricos de `units` que no son
      enteros positivos. Los valores faltantes no se cuentan aquí.
    - `country_values`: lista ordenada de los valores distintos de `country`,
      escritos exactamente como aparecen en el archivo.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "row_count": 103,
          "column_count": 11,
          "missing_required_columns": [],
          ...
          "country_values": [" Colombia ", "CO", ...]
        }
    """
    project_dir = Path(__file__).resolve().parent.parent
    data_path = project_dir / "data" / "ventas.csv.gz"
    submission_dir = project_dir / "submission"
    submission_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(data_path, compression="gzip")
    df.columns = [_normalize_column_name(col) for col in df.columns]

    present_columns = list(df.columns)
    missing_required_columns = sorted(set(REQUIRED_COLUMNS) - set(present_columns))
    unexpected_columns = sorted(set(present_columns) - set(REQUIRED_COLUMNS))

    duplicate_row_count = int(df.duplicated().sum())
    supplier_id = df.get("supplier_id")
    if supplier_id is not None:
        duplicate_supplier_id_row_count = int(
            supplier_id.value_counts(dropna=True)[lambda s: s > 1].sum()
        )
    else:
        duplicate_supplier_id_row_count = 0

    missing_value_count_by_column = {}
    for column in present_columns:
        series = df[column]
        mask = series.isna() | series.astype(str).str.strip().eq("") | series.astype(str).str.upper().eq("N/A")
        missing_value_count_by_column[column] = int(mask.sum())

    contact_email = df.get("contact_email")
    if contact_email is not None:
        email_pattern = r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$"
        email_values = contact_email.dropna().astype(str).str.strip()
        invalid_email_count = int((~email_values.str.fullmatch(email_pattern)).sum())
    else:
        invalid_email_count = 0

    units = df.get("units")
    if units is not None:
        numeric_units = pd.to_numeric(units.astype(str).str.replace(",", "", regex=False), errors="coerce")
        invalid_unit_count = int(
            ((numeric_units.notna()) & (~((numeric_units > 0) & (numeric_units % 1 == 0)))).sum()
        )
    else:
        invalid_unit_count = 0

    country_values = []
    if "country" in df.columns:
        country_values = sorted(df["country"].dropna().astype(str).unique().tolist())

    report = {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "missing_required_columns": missing_required_columns,
        "unexpected_columns": unexpected_columns,
        "duplicate_row_count": duplicate_row_count,
        "duplicate_supplier_id_row_count": duplicate_supplier_id_row_count,
        "missing_value_count_by_column": missing_value_count_by_column,
        "invalid_email_count": invalid_email_count,
        "invalid_unit_count": invalid_unit_count,
        "country_values": country_values,
    }

    output_file = submission_dir / "data_quality_report.json"
    output_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main():
    return pregunta_01()
