#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de la app HTML nueva (diseño moderno) sobre la lógica v0.63.

- Toma la lógica TAL CUAL del archivo app_logica.js (v0.63), sin tocarla.
- Le inyecta datos de EJEMPLO (no son los 893 equipos reales; para esos,
  el usuario importa su backup JSON desde el botón "Importar").
- La envuelve en un armazón HTML moderno con CSS propio + LZString embebido.
- Escribe app_v063_nueva.html junto a la raíz del repo.

No edites el .html a mano: edita este script y vuelve a correrlo.
"""
import json, pathlib, datetime, random

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOGICA = pathlib.Path("/root/.claude/uploads/740a4f5b-9026-4773-b698-7cfae4fa2140/f57d6bf0-app_logica.js")
APP_HTML = ROOT / "app.html"
OUT = ROOT / "app_v063_nueva.html"

# ----------------------------------------------------------------------
# 1) DATOS DE EJEMPLO (seed). Estructura espejada de init() y las vistas.
# ----------------------------------------------------------------------
random.seed(42)
YEAR = 2026
MESES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']

SERVICIOS = [
    ("UCI Adultos", "Box"), ("Pabellón Central", "Quirófano"),
    ("Urgencias", "Reanimación"), ("Neonatología", "Incubadora"),
    ("Imagenología", "Sala"), ("Hemodiálisis", "Puesto"),
    ("Laboratorio", "Bancada"), ("Cardiología", "Box"),
]
FAMILIAS = [
    ("Ventilador mecánico", "Maquet", "Servo-i"),
    ("Monitor multiparámetro", "Philips", "MX450"),
    ("Bomba de infusión", "B.Braun", "Infusomat"),
    ("Desfibrilador (DEA)", "Zoll", "AED Plus"),
    ("Electrobisturí", "Valleylab", "FX8"),
    ("Incubadora neonatal", "Drager", "C2000"),
    ("Máquina de anestesia", "GE", "Aespire"),
    ("Ecógrafo", "Mindray", "DC-70"),
    ("Bomba jeringa", "Fresenius", "Injectomat"),
    ("Monitor de transporte", "Mindray", "uMEC12"),
]
EJECUTORES = ['Carlos Bahamondes Seguel','Cristián Beltrán Oviedo','Cristina Rozas Urrutia',
              'Daniel Díaz Neira','Ignacio Berner Bergara','Macarena Toledo','Marco Ulloa',
              'Matías Soazo Garrido','Ricardo Matus Aroca','Tito Millapán Riquelme','Personal externo']

equipos = []
inv_n = 12000
for i in range(40):
    fam, marca, modelo = random.choice(FAMILIAS)
    serv, uni_base = random.choice(SERVICIOS)
    inv_n += random.randint(3, 40)
    inv = f"INV-{inv_n}"
    # Programación PMP: la mayoría programada cada ~3 meses (X), algunas RA/PM
    prog = {}
    cadencia = random.choice([2, 3, 3, 4, 6])
    offset = random.randint(0, cadencia - 1)
    for m_idx, mes in enumerate(MESES):
        if (m_idx % cadencia) == offset:
            prog[mes] = random.choice(['X', 'X', 'X', 'RA', 'PM'])
    # Registro de resultados de MP (carta gantt) para los meses ya transcurridos
    registro = {}
    for m_idx, mes in enumerate(MESES):
        if mes in prog and m_idx <= 4:  # hasta mayo (mes actual)
            r = random.choices(['Si', 'Si', 'Si', 'C1', 'C2', 'C3', 'FS', 'NU'],
                               weights=[40, 40, 40, 8, 6, 6, 3, 1])[0]
            registro[mes] = {"R": r}
    equipos.append({
        "id": i + 1, "inv": inv, "carpeta": f"C-{1000 + i}",
        "serie": f"SN{random.randint(100000, 999999)}",
        "fam": fam, "equipo": fam, "marca": marca, "modelo": modelo,
        "ano": str(random.randint(2012, 2023)), "proc": random.choice(["Donación", "Compra MINSAL", "Compra hospital"]),
        "servicio": serv, "unidad": f"{uni_base} {random.randint(1, 12)}",
        "ubic": f"Piso {random.randint(1, 5)}", "clasif": random.choice(["Crítico", "Crítico", "Relevante"]),
        "vur": f"{random.randint(1, 10)} años", "freq": f"{random.choice([3,4,6,12])} meses",
        "prog": prog, "registro": registro,
    })

# Eventos de ejemplo: un ciclo correctivo abierto + algunas MP + una reprogramación
def f(m, d):  # fecha YYYY-MM-DD del año vigente
    return f"{YEAR}-{m:02d}-{d:02d}"

eq_sol = equipos[3]; eq_st = equipos[7]; eq_mp = equipos[1]; eq_repro = equipos[5]
eventos = [
    {"id": 1, "inv": eq_sol["inv"], "tipo": "Solicitud de trabajo", "fecha": f(5, 6),
     "folio": "SIGEM-2026-0142", "ejecutor": EJECUTORES[1], "estado": "no operativo",
     "obs": "Falla en válvula espiratoria, pantalla con alarma persistente.", "oficial": "Sí", "fechaReg": f(5, 6)},
    {"id": 2, "inv": eq_sol["inv"], "tipo": "Visita técnica", "tipoVisita": "diagnostica", "fecha": f(5, 9),
     "folio": "SIGEM-2026-0142", "ejecutor": EJECUTORES[3], "estado": "no operativo",
     "obs": "Se requiere repuesto: sensor de flujo.", "oficial": "Sí", "fechaReg": f(5, 9)},
    {"id": 3, "inv": eq_st["inv"], "tipo": "Envío a servicio técnico", "fecha": f(4, 22),
     "folio": "SIGEM-2026-0131", "ejecutor": EJECUTORES[10], "estado": "en servicio técnico",
     "obs": "Enviado a taller externo por falla de placa.", "oficial": "Sí", "fechaReg": f(4, 22)},
    {"id": 4, "inv": eq_mp["inv"], "tipo": "Mantención preventiva", "fecha": f(3, 14),
     "resultado": "Si", "ejecutor": EJECUTORES[0], "estado": "operativo",
     "obs": "MP trimestral completa, equipo conforme.", "oficial": "Sí", "fechaReg": f(3, 14)},
    {"id": 5, "inv": eq_repro["inv"], "tipo": "Mantención preventiva", "fecha": f(5, 2),
     "resultado": "C1", "ejecutor": EJECUTORES[5], "estado": "",
     "obs": "No fue posible desocupar el equipo del paciente.", "oficial": "Sí", "fechaReg": f(5, 2)},
]

pendientes = [
    {"id": 1, "inv": eq_sol["inv"], "equipo": eq_sol["equipo"], "servicio": eq_sol["servicio"],
     "tipo": "documento_faltante", "desc": "Falta cotización del sensor de flujo para emitir OC.",
     "estado": "en_proceso", "fechaCrea": f(5, 9), "fechaComp": f(5, 23), "origen": "manual",
     "ejecutor": EJECUTORES[3]},
    {"id": 2, "inv": equipos[12]["inv"], "equipo": equipos[12]["equipo"], "servicio": equipos[12]["servicio"],
     "tipo": "firma_faltante", "desc": "Pauta de monitoreo diario del DEA sin firma del jefe de equipo médico.",
     "estado": "no_iniciado", "fechaCrea": f(5, 12), "fechaComp": f(6, 1), "origen": "manual",
     "ejecutor": EJECUTORES[6]},
    {"id": 3, "inv": equipos[20]["inv"], "equipo": equipos[20]["equipo"], "servicio": equipos[20]["servicio"],
     "tipo": "recomendacion_tecnica", "desc": "Reemplazo de batería recomendado por antigüedad (>5 años).",
     "estado": "no_iniciado", "fechaCrea": f(4, 28), "fechaComp": None, "origen": "manual",
     "ejecutor": EJECUTORES[0]},
]

SEED = {
    "equipos": equipos,
    "eventos": eventos,
    "pendientes": pendientes,
    "tareas": [],
}
seed_json = json.dumps(SEED, ensure_ascii=False)

# ----------------------------------------------------------------------
# 2) Lógica v0.63 con SEED inyectado (sin tocar nada más)
# ----------------------------------------------------------------------
logica = LOGICA.read_text(encoding="utf-8")
PLACEHOLDER = "const SEED = {/* datos iniciales: ver seed.json (893 equipos, eventos, pendientes) */};"
assert PLACEHOLDER in logica, "No se encontró el placeholder de SEED en app_logica.js"
logica = logica.replace(PLACEHOLDER, f"const SEED = {seed_json};")

# Datos en localStorage por ruta de archivo: usar una key propia para no chocar
# con la app real si ambas se abren desde la misma carpeta.
logica = logica.replace("const STORAGE_KEY = 'hhha_v1_data';",
                        "const STORAGE_KEY = 'hhha_v063_nueva_data';")

# ----------------------------------------------------------------------
# 3) LZString embebido (reutilizado del app.html existente, ya probado)
# ----------------------------------------------------------------------
app_existing = APP_HTML.read_text(encoding="utf-8")
i0 = app_existing.index("<script>var LZString=function()")
i1 = app_existing.index("</script>", i0) + len("</script>")
lzstring_tag = app_existing[i0:i1]

# ----------------------------------------------------------------------
# 4) CSS moderno propio
# ----------------------------------------------------------------------
CSS = pathlib.Path(__file__).resolve().parent.joinpath("estilo_v063.css").read_text(encoding="utf-8")

# ----------------------------------------------------------------------
# 5) Armazón HTML
# ----------------------------------------------------------------------
SHELL_BODY = """
<div class="app">
  <aside class="sidebar">
    <div class="s-logo">HHHA <small>Equipos Críticos · v__V__ · demo</small></div>
    <nav id="nav"></nav>
    <div class="s-foot"><span class="user-tag">👤 Cristian</span></div>
  </aside>
  <div class="content">
    <header class="topbar">
      <button id="btn-sidebar" class="icon-btn" title="Mostrar/ocultar menú">☰</button>
      <div style="flex:1"></div>
      <span id="state-indicator" class="state-indicator" title="">—</span>
      <button id="btn-theme" class="theme-btn" title="Cambiar tema claro/oscuro">🌞</button>
      <button id="btn-excel" title="Exportar a Excel (.xlsx)">📊 Excel</button>
      <button id="btn-export" title="Exportar backup JSON">💾 Backup</button>
      <button id="btn-import" title="Importar backup JSON">📥 Importar</button>
      <button id="btn-reset" title="Resetear a datos de ejemplo">↻ Reset</button>
    </header>
    <main id="main"></main>
  </div>
</div>

<div id="modal-root"></div>
<div id="toast-root"></div>

<div class="rec-widget minimized" id="rec-widget" style="left:18px;bottom:18px">
  <div class="rw-hd">
    <span class="ttl"><span class="dot"></span>REC</span>
    <span style="display:flex;gap:4px">
      <button class="ghost-btn" id="rw-toggle" title="Minimizar">▢</button>
    </span>
  </div>
  <div class="rw-bd">
    <div class="info" id="rw-info">Detenido · 0 eventos</div>
    <div class="row">
      <button id="rw-rec">● Grabar</button>
      <button id="rw-pause" disabled>⏸ Pausar</button>
    </div>
    <button id="rw-stop" disabled>■ Detener y exportar</button>
  </div>
</div>
""".replace("__V__", "0.63")

HTML = f"""<!DOCTYPE html>
<html lang="es" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HHHA — Gestión de Equipos Biomédicos Críticos (v0.63 · demo)</title>
<!-- SheetJS para importar/exportar Excel (solo con conexión). Sin él, la app funciona igual salvo Excel. -->
<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
{lzstring_tag}
<style>
{CSS}
</style>
</head>
<body>
{SHELL_BODY}
<script>
{logica}
</script>
</body>
</html>
"""

OUT.write_text(HTML, encoding="utf-8")
print(f"OK -> {OUT}  ({len(HTML)//1024} KB)  ·  {len(equipos)} equipos demo, {len(eventos)} eventos, {len(pendientes)} pendientes")
