#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
excel_a_seed.py — Convierte un export XLSX de HHHA (hojas Eventos / Pendientes /
Ciclos correctivos) en el seed.json que consume el programa.

Para qué sirve
--------------
El programa puede EXPORTAR sus datos a un Excel (botón "Excel"). Este script hace
el camino inverso: toma ese Excel y vuelve a meter sus eventos y pendientes como
datos iniciales del programa, conservando del seed actual lo que el Excel NO trae
(el catálogo de equipos y la programación de mantención anual).

Importante (el export es "con pérdida"):
  - El Excel NO incluye el catálogo de equipos ni la matriz MP anual -> se
    conservan tal cual del seed.json actual.
  - Los CICLOS correctivos no se guardan en el seed: el programa los reconstruye
    solo, a partir de las "Solicitudes de trabajo" con folio.
  - Los ESTADOS de cada equipo tampoco se guardan: el programa los recalcula
    desde los eventos.

El mapeo de columnas es el inverso EXACTO de la función exportExcel() de
build_app.py. Si esa función cambia, actualizar aquí también.

Uso
---
    python3 tools/excel_a_seed.py [ruta_al_excel.xlsx] [salida_seed.json]

Por defecto usa docs/origen_datos_20260528.xlsx y escribe seed.json en la raíz.
"""
import json, re, sys, zipfile, pathlib
import xml.etree.ElementTree as ET

RAIZ = pathlib.Path(__file__).resolve().parent.parent
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

# Etiqueta visible de pendiente -> clave interna (inverso de TIPO_PENDIENTE)
LABEL_A_TIPO = {
    "Documento faltante": "documento_faltante",
    "Reprogramación MP": "reprogramacion",
    "Recomendación técnica": "recomendacion_tecnica",
    "Gestión general": "gestion_general",
}


def _col_idx(ref):
    letras = re.match(r"([A-Z]+)", ref).group(1)
    n = 0
    for ch in letras:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def leer_xlsx(ruta):
    """Devuelve {nombre_hoja: [ {encabezado: valor, ...}, ... ]}."""
    z = zipfile.ZipFile(ruta)
    compartidas = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")):
            compartidas.append("".join(t.text or "" for t in si.iter(NS + "t")))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap = {r.get("Id"): r.get("Target") for r in rels}
    out = {}
    for s in wb.iter(NS + "sheet"):
        rid = s.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        sh = ET.fromstring(z.read("xl/" + relmap[rid].replace("../", "")))
        matriz = []
        for row in sh.iter(NS + "row"):
            celdas, maxc = {}, 0
            for c in row.iter(NS + "c"):
                ci = _col_idx(c.get("r"))
                v = c.find(NS + "v")
                val = ""
                if v is not None:
                    val = compartidas[int(v.text)] if c.get("t") == "s" else v.text
                celdas[ci] = val or ""
                maxc = max(maxc, ci)
            matriz.append([celdas.get(i, "") for i in range(maxc + 1)])
        hdr = matriz[0]
        out[s.get("name")] = [
            dict(zip(hdr, fila + [""] * (len(hdr) - len(fila)))) for fila in matriz[1:]
        ]
    return out


def iso(s):
    """'DD-MM-YYYY' -> 'YYYY-MM-DD'. Vacío o '—' -> None. Por texto, sin new Date
    (respeta la invariante de zona horaria del proyecto)."""
    s = (s or "").strip()
    if not s or s == "—":
        return None
    m = re.match(r"^(\d{2})-(\d{2})-(\d{4})$", s)
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else s


def limpio(v):
    v = (v or "").strip()
    return v if v not in ("", "—") else None


def convertir(ruta_xlsx, seed_actual):
    ex = leer_xlsx(ruta_xlsx)

    eventos = []
    for r in ex["Eventos"]:
        e = {
            "id": int(r["ID"]),
            "inv": str(r["N° Inv."]).strip(),
            "equipo": limpio(r["Equipo"]) or "",
            "servicio": limpio(r["Servicio"]) or "",
            "tipo": r["Tipo"].strip(),
            "fecha": iso(r["Fecha del evento"]),
            "fechaReg": iso(r["Fecha registro"]),
            "ejecutor": limpio(r["Ejecutor"]),
            "estado": r["Estado equipo"].strip(),
        }
        for col, key in [("Resultado", "resultado"), ("Folio SIGEM", "folio"),
                         ("N° Envío", "nEnvio"), ("N° OC", "nOC"),
                         ("N° Cotización", "nCotiz"), ("Empresa", "empresa"),
                         ("Técnico", "tecnico"), ("Observación", "obs")]:
            val = limpio(r.get(col, ""))
            if val is not None:
                e[key] = val
        e["oficial"] = "Sí" if r.get("Oficial", "").strip().lower() in ("sí", "si") else "No"
        if e["fechaReg"]:
            e["actualizado"] = e["fechaReg"]
        cp = limpio(r.get("Creado por", ""))
        if cp:
            e["creadoPor"] = cp
        eventos.append(e)

    pendientes = []
    for r in ex["Pendientes"]:
        p = {
            "id": int(r["ID"]),
            "inv": str(r["N° Inv."]).strip(),
            "equipo": limpio(r["Equipo"]) or "",
            "servicio": limpio(r["Servicio"]) or "",
            "tipo": LABEL_A_TIPO.get(r["Tipo"].strip(), "gestion_general"),
            "desc": limpio(r["Descripción"]) or "",
            "ejecutor": limpio(r["Ejecutor"]),
            "fechaCrea": iso(r["Fecha creación"]),
            "fechaComp": iso(r["Fecha compromiso"]),
            "estado": r["Estado"].strip(),
            "origen": limpio(r["Origen"]) or "manual",
        }
        fc = iso(r["Fecha cierre"])
        if fc:
            p["fechaCierre"] = fc
        if p["fechaCrea"]:
            p["actualizado"] = p["fechaCrea"]
        pendientes.append(p)

    # Lo que el Excel NO trae se conserva del seed actual.
    return {
        "equipos": seed_actual["equipos"],
        "eventos": eventos,
        "pendientes": pendientes,
        "tareas": [],
        "meses": seed_actual["meses"],
    }


def main():
    ruta_xlsx = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "docs" / "origen_datos_20260528.xlsx"
    salida = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else RAIZ / "seed.json"
    seed_actual = json.loads((RAIZ / "seed.json").read_text(encoding="utf-8"))
    seed = convertir(ruta_xlsx, seed_actual)
    salida.write_text(json.dumps(seed, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"OK · {salida}: {len(seed['equipos'])} equipos, "
          f"{len(seed['eventos'])} eventos, {len(seed['pendientes'])} pendientes")
    print("Recuerda regenerar el programa:  python3 build_app.py")


if __name__ == "__main__":
    main()
