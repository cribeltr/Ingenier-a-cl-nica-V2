══════════════════════════════════════════════════════════════
HHHA · Sistema de Gestión de Equipos Biomédicos Críticos
Bundle completo — v0.24 · 28-05-2026
══════════════════════════════════════════════════════════════

CONTENIDO DEL ZIP
─────────────────────────────────────────────────────────────

📄 app.html                    Aplicación funcional (v0.24) — 100% offline.
                               Abre con doble clic en cualquier navegador.

📄 build_app.py                Script Python que genera app.html a partir
                               del seed JSON + SheetJS + lz-string embebido.
                               Si querés regenerar la app: python3 build_app.py

📄 seed.json                   Datos iniciales (893 equipos, 55 eventos
                               demo, 30 pendientes) embebidos en la app.

📁 docs/
   ├── pseudocodigo.md         Especificación funcional completa del sistema
                               (17 módulos: glosario, modelo de datos, máquina
                               de estados, ciclo correctivo, 7 tipos de evento,
                               MP, pendientes, baja, importación, etc.)
   ├── Programacion_MP_2026_original.xlsm
                               Archivo maestro de partida (PMP_2026 +
                               Registro_MP-2026).
   └── eventos_equipos_referencia.xlsx
                               Referencia inicial de catálogos
                               (eventos, pendientes, tareas, causales).

📁 sesiones/                   13 sesiones grabadas (usuario × app),
                               ordenadas cronológicamente. Cada una contiene
                               clicks, inputs, focus, navegación, think_times,
                               hovers prolongados, scroll, errores, modal
                               aborts y métricas resumen.

📁 data/                       11 backups JSON exportados durante el desarrollo.
                               Capturan el state completo en cada momento
                               (equipos, eventos, pendientes, conflictos,
                               importaciones, audit log).

📁 exports/                    11 exports XLSX con las hojas:
                               Equipos · PMP_2026 · Registro_MP-2026 · Eventos
                               · Pendientes · Conflictos · Ciclos correctivos.

📁 plantillas/                 4 plantillas de asignación de MP del mes
                               (Feb, Mar, Abr, May 2026) con formato real
                               del usuario, listas para subir.


CÓMO USAR
─────────────────────────────────────────────────────────────

1. Doble clic en app.html → abre en el navegador.
2. Verás banner amarillo "No detecto actividad del usuario en estos datos".
3. Click en Importar (header) y selecciona el data/11_hhhadata20260528_6.json
   (o el último que tengas como backup).
4. La migración se aplica automáticamente. Quedas en el estado donde dejaste.


VERSIONES IMPLEMENTADAS
─────────────────────────────────────────────────────────────

v0.1  Prototipo inicial (7 tipos de evento, ciclo correctivo, MP, pendientes).
v0.2  Rediseño minimalista + 3 tablas resumen clickeables.
v0.3  Conciliación con archivo maestro + 4 tipos de conflicto.
v0.4  Fix bug fechas (UTC) + MP rápida + export Excel.
v0.5  Protección anti-pérdida de datos + banner welcome.
v0.6  Compresión LZ de localStorage (10×).
v0.7  Confirmación al cerrar modal + búsqueda enriquecida.
v0.8  Anular evento revierte efectos + estado "Desconocido".
v0.9  Migración auto que limpia inconsistencias.
v0.10 Plantillas de asignación Excel (descargar/subir).
v0.11 Resolución masiva de conflictos + evento sintético.
v0.12 Detección de mes en nombre de plantilla.
v0.13 Agrupación de conflictos + hash de archivos.
v0.14 Dual theme + grabador auto-start enriquecido.
v0.15 Tarjeta de info del equipo en modales.
v0.16 Conflictos visibles desde el equipo.
v0.17 Resumen del equipo + Ctrl+K buscador global.
v0.18 Toggle Por ejecutor / Por mes en Dashboard.
v0.19 Fix botones del Resumen (closure roto).
v0.20 Registro masivo MP + modal anulación con motivos.
v0.21 Auto-completado en Conciliación (vacío en programa = autollena).
v0.22 Gramática visual unificada de iconos.
v0.23 Distinguir eventos auto-completados en bitácora.
v0.24 Fix bug de fechas UTC (MP del día 1 caía en el mes anterior en Chile).


ATAJOS DE TECLADO
─────────────────────────────────────────────────────────────

  Ctrl+K (o /)      Buscador global de equipos
  Esc               Cerrar modal
  Enter             Confirmar (en MP rápida, quick search, tareas)


REPOSITORIO
─────────────────────────────────────────────────────────────

  branch: claude/modest-thompson-Kg8Ih
  github.com/cribeltr/202605281230_EQUIPOS_CRITICOS_GESTION


══════════════════════════════════════════════════════════════
