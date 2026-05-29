#!/usr/bin/env python3
"""Build app.html with embedded seed JSON."""
import json, pathlib

with open("/tmp/seed.min.json", "r", encoding="utf-8") as f:
    seed_str = f.read()

HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>HHHA · Gestión de Equipos Biomédicos Críticos</title>
<!-- SheetJS mini (xlsx.mini.min.js, ~250KB) embebido para parsear XLSX/XLSM 100% offline. -->
<script>__SHEETJS_PLACEHOLDER__</script>
<!-- lz-string (~5KB) para comprimir el state en localStorage y evitar cuota excedida. -->
<script>__LZSTRING_PLACEHOLDER__</script>
<!--
CHANGELOG
v0.49 [2026-05-29] Rediseño minimalista (paso 1): paleta azul, densidad compacta, sidebar contraíble.
  - Sin perder ninguna función (solo capa visual). Nueva paleta neutra fría con ACENTO AZUL
    (claro y oscuro), foco azul en campos. Densidad COMPACTA (fuentes/paddings/tablas más juntas).
  - Barra lateral oscura ahora CONTRAÍBLE: botón ☰ en la barra superior la pliega/expande y se
    recuerda la preferencia (sidebarColapsada).
  - Tablas más limpias (hover de fila, encabezados compactos), tarjetas/secciones con esquinas
    más suaves y sombra sutil, botones con radio 6px y foco accesible.
v0.48 [2026-05-29] Autocorrección: guardián automático que bloquea las clases de error cometidas.
  - tools/guard.js corre solo tras build (junto a la prueba de humo) y BLOQUEA: estado de MP no
    derivado de estadoMPDesdeResultado en algún sitio, patrones legacy prohibidos, y cualquier
    vista que falle al dibujarse con un respaldo real. Avisa de funciones muertas y clases CSS de
    layout agresivo compartidas por varias tablas. Probado que habría atajado los bugs v0.39/v0.45.
  - CLAUDE.md: guardián obligatorio + regla de diseño visual (lo que el headless no ve, lo ve el
    usuario; revisar todas las vistas que comparten clase/dato).
v0.47 [2026-05-29] Fix: la vista Registro MP se veía aplastada (letra por letra).
  - Causa: el estilo "ajustar a pantalla" de v0.42 (ancho 100% + partir palabras + títulos que
    envuelven) se aplicó a la clase `eq-grid`, que comparten Buscar equipos (13 columnas) y
    Registro MP (~42 columnas). Con 42 columnas, forzar ancho 100% aplastaba cada columna y
    partía el texto carácter por carácter.
  - Arreglo: ese estilo se mueve a una clase propia `buscar-grid` (solo Buscar equipos).
    Registro MP recupera anchos naturales con desplazamiento horizontal (su diseño de carta
    gantt; el botón "Ocultar meses" sigue colapsando las 24 columnas de meses).
v0.46 [2026-05-29] Completa el fix v0.45: faltaban 2 lugares que guardaban mal el estado de la MP.
  - Error propio: en v0.45 corregí el estado de la MP en 3 sitios + el cálculo, pero OMITÍ:
    (1) el formulario completo de evento, donde "Estado resultante" era un menú manual (por
    defecto "operativo") independiente del resultado — registrar un C2 dejando "operativo"
    volvía a romper el estado; (2) la creación de MP al ACEPTAR un conflicto en Conciliación
    (origen 'conciliacion'), que seguía con la fórmula vieja.
  - Arreglo: el "Estado resultante" del formulario ahora es automático (solo lectura, derivado
    del resultado con estadoMPDesdeResultado) y la conciliación usa el mismo helper. Es la misma
    causa raíz de siempre: arreglar un patrón en N sitios y omitir M. Ahora son los 5 sitios.
v0.45 [2026-05-29] Fix: equipos "en servicio técnico" desaparecían tras subir el maestro.
  - Causa: la MP guardaba mal su estado resultante. La fórmula solo distinguía Si→operativo y
    Baja→baja; TODO lo demás (incluido C2 = "equipo en servicio técnico" y C3/FS/NU = "no
    operativo") quedaba como "operativo". Al subir el maestro se crean MP automáticas, y esos
    eventos "operativos" tapaban el "en servicio técnico" que antes se deducía de la carta gantt.
  - Arreglo: el estado de una MP se deriva de su RESULTADO/causal (helper estadoMPDesdeResultado,
    espejo de MP_CAUSAL_ESTADO): C2→en servicio técnico, C3/FS/NU→no operativo, Baja→baja,
    Si→operativo; C1 y C4–C8 (reprogramación) NO declaran estado. Aplicado en el cálculo
    (recalcEstadoEquipo), en los 3 puntos que crean MP (ficha, MP rápida, automáticas del maestro)
    y en la columna Estado del historial. Corrige los datos existentes sin re-subir nada.
v0.44 [2026-05-29] Cada evento del historial tiene botón "➕ Pend." (pendiente ligado).
  - En la columna Acciones del historial, cada evento (no anulado) suma "➕ Pend." que abre el
    formulario de pendiente con el equipo precargado y LIGADO a ese evento (eventoOrigen). El
    nuevo pendiente aparece de inmediato en la columna Pendientes de esa misma fila.
  - nuevoPendiente acepta opts.eventoOrigen, guarda el vínculo y muestra un aviso "🔗 ligado a…".
v0.43 [2026-05-29] Historial de eventos en COLUMNAS + columna de Pendientes (cap. 4.3).
  - El historial pasa de tarjetas a una TABLA con columnas: Fecha · Descripción · Estado ·
    Ejecutor · Pendientes · Acciones. La columna "Pendientes" muestra, al lado de cada evento,
    los pendientes asociados (clic para abrirlos); "—" si no tiene.
  - Descripción agrupa tipo, sellos (Oficial/Borrador/🔗 Auto-maestro/⚡ Lote), folio, resultado,
    empresa, observación y, si está anulado, el motivo. Acciones (Oficializar/Editar/Anular) en
    su columna. Se conserva el botón 🖨 Imprimir.
v0.42 [2026-05-29] Buscar equipos cabe en pantalla (sin desplazamiento lateral).
  - Lo que faltaba del pedido anterior: la planilla seguía siendo más ancha que la pantalla.
  - Se quita la columna "Acciones" del extremo derecho (la fila ya abre la ficha; los ➕ están
    dentro de la ficha). Los títulos de columna ahora ENVUELVEN (antes en una sola línea
    forzaban el ancho), las celdas parten palabras largas y el espaciado es más compacto.
  - Resultado: las 13 columnas (ID … Pendientes) entran en el ancho normal sin scroll lateral.
v0.41 [2026-05-29] Ajustes pedidos tras la primera sesión de uso real.
  - Buscar equipos: hacer CLIC EN LA FILA abre la ficha (se quita el botón "Ficha"). Los
    botones ➕ Evento / ➕ Pend. no abren la ficha (no propagan el clic). Menos
    desplazamiento lateral (en la sesión el usuario se trababa al estirarse al botón).
  - MP con causal C1–C8: además del pendiente de reprogramación, marca de inmediato una "R"
    (reprogramado) en la PROGRAMACIÓN del MES SIGUIENTE de la carta gantt (registro[mesSig].P).
    No pisa una programación ya puesta. La ficha lee P desde registro.P (como la planilla).
  - Historial de eventos: nuevo botón "🖨 Imprimir" que abre una hoja limpia con la hoja de
    vida del equipo y lanza el diálogo de impresión (o guardar como PDF), 100% offline.
  - Verificado que al subir el maestro los resultados R de la gantt aparecen en el historial
    como eventos "🔗 Auto-maestro" (ya ocurría desde v0.21; confirmado con prueba).
v0.40 [2026-05-29] Alineación con la especificación funcional (vistas).
  - "Equipos" pasa a llamarse "Buscar equipos" (menú y título), como en el documento.
  - Columnas de la planilla en el orden de la especificación + se agrega la columna SERIE:
    ID · N° Inventario · Serie · Equipo · Marca · Modelo · Servicio · Unidad · Ubicación ·
    Procedencia · Estado · Días en estado · Pendientes. Las celdas se generan desde la
    definición de columnas (reordenar es seguro). Filtro/orden por columna intactos.
  - Ficha del equipo: las pestañas se reemplazan por SECCIONES CONTRAÍBLES, una bajo otra
    (Datos del equipo · Programación PMP · Historial de eventos · Pendientes · Ciclos
    correctivos · Conflictos), todas pliegan/despliegan. Cap. 4 de la especificación.
  - Programación PMP de la ficha: se agrega la fila EJECUTOR (Mes / P / R / Ejecutor),
    como pide el documento (4.2).
v0.39 [2026-05-29] Fix: la lista de Equipos (y Registro MP) quedaba VACÍA.
  - Causa: 18 equipos tienen "modelo" y 3 "ubicación" guardados como número (no texto).
    Las planillas de Equipos (v0.37) y Registro MP (v0.38) ordenan/filtran por texto con
    localeCompare, que se cae ante un número -> el dibujado se aborta y la tabla queda vacía.
    Reproducido headless: navegar a Equipos lanzaba "a.localeCompare is not a function";
    0 filas. El resto de las vistas funcionaba.
  - Arreglo de raíz: normalizarEquipos() convierte a texto los campos de identificación del
    equipo (modelo, ubicación, marca, serie, etc.) al cargar el seed, al cargar un respaldo
    y al importar. Defensa adicional: valoresUnicos, el orden y el filtro de columna de AMBAS
    planillas envuelven el valor en String() para no volver a caerse ante un número suelto.
  - Verificado headless con el seed y con respaldos reales de data/: Equipos y Registro MP
    muestran 894 filas; filtros por columna y orden funcionan.
v0.38 [2026-05-28] Nueva vista "Registro MP" (carta gantt navegable).
  - Réplica de la hoja Registro_MP: todas las columnas de identificación del equipo + los 12
    meses con P (programado) y R (realizado) + Estado, Días en estado y Pendientes al final.
  - Filtro y orden en todas las columnas (como la planilla de Equipos); "Abrir" lleva a la
    ficha. Botón "Ocultar/Mostrar meses" para colapsar las 24 columnas de P/R (se recuerda).
  - En el menú, grupo GESTIONAR. R='Si' en verde, causales C1-C8 en ámbar.
v0.37 [2026-05-28] Equipos como planilla tipo Excel.
  - Ordenar por cualquier columna (clic en el título, ▲/▼) y un FILTRO por columna: lista de
    valores para texto categórico (Servicio, Estado, Marca, Modelo, Unidad, Ubicación,
    Procedencia, Equipo) y "contiene" para ID / N° Inventario / Pendientes / Días.
  - Cada fila trae botones para registrar al instante: "➕ Evento", "➕ Pend." y "Ficha".
  - Los accesos rápidos (En servicio técnico / No operativos / Con pendientes / Todos) aplican
    esos filtros; la búsqueda global se mantiene; se quitaron los selects redundantes del toolbar.
v0.36 [2026-05-28] Barra lateral agrupada (Gestionar/Registrar) + accesos rápidos en Equipos.
  - Barra lateral en dos grupos: GESTIONAR (Por resolver, Equipos, Resumen) y REGISTRAR
    (MP del mes, Conciliación). Pendientes/Ciclos/Eventos salen del menú (siguen accesibles
    desde "Por resolver" y la ficha del equipo) -> menos ruido.
  - Equipos: botones de acceso rápido con conteo — "En servicio técnico (N)", "No operativos
    (N)", "Con pendientes (N)", "Todos" — para responder al vuelo. En servicio técnico / no
    operativo se muestra el encargado (encargadoDe: ingeniero del ciclo o último ejecutor).
v0.35 [2026-05-28] Rediseño de navegación: barra lateral izquierda + columnas de Equipos.
  - El menú horizontal superior pasa a una BARRA LATERAL izquierda fija (oscura, estilo de
    la referencia del usuario): logo arriba, todos los apartados visibles con su contador,
    el activo resaltado. Se elimina el desplegable "Más".
  - Los botones (Excel, Backup, Importar, Reset, tema, indicador) pasan a una franja
    superior delgada a la derecha. Layout: .app pasa de grid por filas a columnas
    (232px barra lateral + contenido).
  - Vista Equipos con las columnas pedidas: ID, N° Carpeta, N° Inventario, Equipo,
    Servicio, Unidad, Ubicación, Procedencia, Marca, Modelo, Estado, Pendientes, Días en estado.
v0.34 [2026-05-28] Estado del equipo: se infiere de la carta gantt; por defecto operativo.
  - Antes el estado operativo se calculaba SOLO desde eventos: 811 de 894 equipos quedaban
    "Desconocido" porque su actividad vive en la carta gantt (mismo patrón que el bug de MP).
  - Ahora recalcEstadoEquipo, sin eventos con estado, infiere de la matriz (MP_CAUSAL_ESTADO):
    C2 -> en servicio técnico, C3/FS/NU -> no operativo, Baja -> baja. Si la gantt no indica
    falla -> operativo. Datos reales: ~858 operativo, 15 serv. técnico, 16 no operativo, 5 baja,
    en vez de 811 desconocido.
v0.33 [2026-05-28] Fix MP del mes (carta gantt + eventos), navegación de meses/año, grabador.
  - BUG: la MP del mes se consideraba "pendiente" mirando SOLO eventos, ignorando la
    matriz registro[mes].R (carta gantt). Un equipo con la MP marcada en la gantt pero
    sin evento aparecía como pendiente. Ahora resultadoMPMes() / mpEstadoMes() consideran
    AMBAS fuentes (evento del mes y matriz del año vigente). Estados: ejecutada (Si) /
    reprogramada (C1-C8) / otro (FS,NU,Baja,No) / pendiente (nada). Aplicado en el Resumen
    (por mes y por ejecutor), la ficha del equipo y la vista MP del mes (filtro +
    etiqueta). mpDelMesEjecutada ahora deriva de mpEstadoMes.
  - El filtro "Reprogramadas" mira el resultado (C1-C8), no la programación.
  - MP del mes: navegación con flechas y selector de año (antes el año quedaba fijo).
  - Grabador: captura todos los avisos (resultado de acciones), el cambio de filtros con
    la opción elegida, y más contexto de estado (conflictos, borradores, por resolver).
v0.32 [2026-05-28] Excel autónomo: hoja oculta para lo automático + guía + "Por resolver".
  - exportExcel() reestructurado para que el archivo sirva como respaldo de trabajo
    sin el programa:
    · Hoja "Léeme": resumen (totales) y qué contiene cada hoja.
    · Hoja "Por resolver": pendientes abiertos + ciclos abiertos + borradores, con
      columna "Hecho" para marcar en papel.
    · Hoja "Eventos": SOLO lo que el usuario registró (incluye borradores).
    · Hoja "Eventos (automáticos)" marcada como OCULTA (Workbook.Sheets[].Hidden=1):
      eventos generados al conciliar el maestro (origen conciliacion/conciliacion_auto).
    · Todas las tablas con anchos de columna y autofiltro para ordenar/buscar.
  - Se verificó con SheetJS mini que la hoja oculta se escribe y relee como oculta.
v0.31 [2026-05-28] Menú simplificado: principales + desplegable "Más".
  - Arriba quedan solo las vistas frecuentes (según el análisis de sesiones):
    Por resolver · Equipos · Conciliación · MP del mes.
  - Resumen, Pendientes, Ciclos correctivos y Eventos pasan a un desplegable "Más ▾"
    (no se elimina nada; siguen a un clic y también se llegan desde "Por resolver").
  - El botón "Más" se marca activo cuando la vista actual es una de esas. El menú se
    cierra al elegir o al hacer click fuera. NAV_PRINCIPAL/NAV_SECUNDARIO centralizan
    la lista para no duplicarla.
v0.30 [2026-05-28] Look más moderno (aprobado en muestra) + "Por resolver" en tarjetas.
  - Capa de estilo moderno añadida al final del <style> (sin alterar la estructura
    ni los selectores existentes, para no romper): bordes redondeados mayores y
    sombras suaves en botones/campos/KPIs/tablas/tarjetas; navegación tipo "pastilla"
    (activo con fondo de acento); ventanas flotantes (modales) con esquinas más
    redondeadas, sombra profunda y fondo desenfocado (backdrop blur).
  - VIEWS.porResolver reescrita con tarjetas accionables: banda de color por urgencia
    (rojo vencido / gris no iniciado / ámbar en proceso / teal ciclo), título, detalle
    y botones Empezar/Resolver. Mantiene la misma lógica de datos de v0.29.
  - Tema claro/oscuro se conserva (preferencia recordada por el usuario).
v0.29 [2026-05-28] Pendientes orientados a la acción + pantalla "Por resolver".
  - Pendientes con estados No iniciado -> En proceso -> Resuelto (internos
    'no_iniciado'/'en_proceso'/'cerrado'; 'cerrado' se conserva para no romper los
    conteos !== 'cerrado'). Nacen "No iniciado". Migración: 'creado'/'abierto' de
    datos previos -> 'no_iniciado' (en init() y en migrate()).
  - Tabla de pendientes: estado con color (badgePend) y botones rápidos "Empezar"
    y "Resolver". Filtro de la vista y selector de edición con los nuevos nombres.
  - Nueva vista "Por resolver" como pantalla de inicio: bandeja accionable con
    pendientes vencidos / no iniciados / en proceso, ciclos abiertos, borradores por
    oficializar y conflictos con el maestro. Contador en el menú.
  - El "Dashboard" de números pasa a llamarse "Resumen" (sigue accesible).
v0.28 [2026-05-28] El folio del ciclo se preselecciona; aviso si no hay ciclo abierto.
  - En los eventos que se vinculan a un ciclo (Visita, Orden de Compra, Envío,
    Recepción, Reparación), el campo "Folio SIGEM" ahora PRESELECCIONA el ciclo
    correctivo abierto del equipo en vez de quedar en "— sin ciclo —". El folio se
    carga solo, y así la Reparación/Recepción operativa cierra el ciclo correcto
    (antes, si el usuario no elegía el folio, no se cerraba).
  - Si el equipo no tiene ciclo abierto, Reparación y Recepción muestran un aviso
    claro (en vez de una casilla muda): revisar si la Solicitud fue anulada o cerrada.
  - Unificado en el helper folioCicloControl(), reutilizado en los 5 formularios
    (antes era la misma expresión repetida 5 veces).
v0.27 [2026-05-28] El número de versión del encabezado se sincroniza solo.
  - El encabezado mostraba "v0.23" fijo (escrito a mano), sin actualizarse al subir
    APP_VERSION en versiones siguientes. Ahora usa el placeholder __APP_VERSION__
    que build_app.py reemplaza con el valor real de APP_VERSION al generar: una
    sola fuente de verdad, no vuelve a quedar desfasado.
v0.26 [2026-05-28] Cierre de ciclo por Recepción + Reparación "en servicio técnico".
  - Flujo de reparación externa: la "Recepción" en estado Operativo ahora CIERRA
    el ciclo correctivo (el equipo retornó funcionando). Antes solo lo cerraban la
    Reparación y la Visita correctiva operativas, así que un equipo reparado afuera
    y recibido dejaba el ciclo abierto para siempre.
  - Aplicado en los 3 puntos del mismo patrón: aplicarEfectosEvento (registro en
    vivo), reconstrucción de ciclos al cargar el seed (bootstrap) y reapertura al
    anular (si se anula la Recepción/Reparación que cerró y no hay otra operativa).
  - La "Reparación" admite estado resultante "En servicio técnico": permite
    registrar "reparado en el servicio técnico externo, aún sin retornar" sin
    cerrar el ciclo y dejando el equipo en servicio técnico.
v0.25 [2026-05-28] Carga de datos reales del usuario como nuevo seed.
  - El programa arranca ahora con los datos reales del usuario: 85 eventos, 34
    pendientes y 3 ciclos correctivos (reconstruidos desde las Solicitudes de
    trabajo), sobre el catálogo de 893 equipos y su programación MP anual.
  - Se reemplazaron los eventos/pendientes de demostración por los del export
    XLSX del usuario (hojas Eventos/Pendientes), traducidos al formato interno
    invirtiendo el mapeo de exportExcel(): fechas DD-MM-YYYY -> YYYY-MM-DD por
    split (sin new Date, respetando la invariante de zona horaria), tipo de
    pendiente por etiqueta, causales C3/C8 preservadas en 'resultado'.
  - init(): los pendientes del seed ahora respetan su 'tipo' y 'origen' si vienen
    dados; si faltan, se derivan del texto como antes (retrocompatible). Evita
    que 2 'Reprogramacion MP' (desc "abril") se reclasifiquen como 'Gestion general'.
  - El generador escribe app.html junto al propio build_app.py (antes apuntaba a
    una ruta absoluta del entorno de construccion).
v0.24 [2026-05-28] Fix bug de fechas UTC en dos puntos omitidos.
  - El parseo seguro new Date(f+'T00:00:00') se usaba en 4 lugares pero faltaba
    en mpDelMesEjecutada (lectura) y aplicarEfectosEvento/MP (escritura).
  - Sin el 'T00:00:00', en zona horaria negativa (Chile) una MP del día 1 se
    leía en el mes anterior: se guardaba en la celda equivocada de la matriz y
    no se detectaba como ejecutada en su mes. Reproducido y corregido.
  - Detectado en revisión completa siguiendo el protocolo (grep del patrón en
    todo el archivo).
v0.1 [2026-05-28] Prototipo inicial. Features:
  - Importación del maestro (893 equipos), Registro_MP-2026, eventos (55) y pendientes (30) embebidos como seed.
  - 7 tipos de evento operativos (Solicitud, Visita, OC, Envío, Recepción, Reparación, MP).
  - Ciclo correctivo: apertura automática en Solicitud (Folio SIGEM), cierre en Reparación operativa.
  - Máquina de estados: operativo / no_operativo / en_servicio_tecnico / baja + sub-estados.
  - Pendientes con 4 tipos, creación auto por causal C1-C8, ciclo de vida creado→abierto→cerrado, tareas, seguimientos.
  - Matriz MP anual (12 meses) con códigos P/R, vista de MP del mes con asignación de ejecutores.
  - Búsqueda full-text en maestro + filtros combinados (servicio/estado/familia/freq).
  - Ficha de equipo: datos, matriz MP, bitácora, ciclos, pendientes.
  - Dashboard con KPIs, alertas >30 días, MP pendientes del mes.
  - Grabador de sesión flotante (clicks/inputs/focus/nav), exporta JSON.
  - Persistencia localStorage versionada (hhha_v1_data), export/import/reset.
  - Audit log de cambios.
v0.2 [2026-05-28] Rediseño minimalista + tablas resumen clickeables.
  - Paleta neutral (blanco/grises/un accent azul), tipografía sobria, bordes sutiles, espaciado amplio.
  - Header simplificado, navegación con tipografía limpia, eliminado el efecto de tarjetas pesadas.
  - Dashboard reorganizado en 3 tablas resumen + 1 fila compacta de KPIs:
      · MP del año: filas=mes, cols=Si / Reprogramadas / FS / NU / Baja / Sin registro / Total.
      · Equipos por servicio: filas=servicio, cols=Op / NoOp / ST / Baja / Pend. / Total.
      · MP del mes por ejecutor: Asignadas / Ejecutadas / Pendientes / %.
  - Cada celda con valor navega a la vista correspondiente con filtros pre-aplicados.
  - Sistema de filtros vía params en cada vista (equipos, mp, pendientes, eventos).
  - Chip de filtros activos visible y limpiable en cada vista.
v0.23 [2026-05-28] Distinguir visualmente eventos auto-completados en bitácora.
  - Diagnóstico 2-115785: usuario veía 2 MPs (May 18 manual + Feb 15 sintético
    de v0.21 al subir maestro) sin distinción visual → confusión "no registré
    el de Feb".
  - Fix: badge 🔗 Auto-maestro para eventos origen='conciliacion_auto',
    🔗 Conciliación para 'conciliacion', ⚡ Lote para 'masivo'.
  - Borde lateral verde + fondo sutil para eventos auto en bitácora.
  - Timestamp de creación visible junto a la fecha del evento (DD-MM HH:MM)
    para distinguir "cuándo se creó" vs "fecha del evento físico".
  - Tooltips explican el origen de cada badge.
v0.22 [2026-05-28] Auditoría de diseño: iconografía unificada en botones.
  - Gramática visual consistente:
    · ➕ crear (MP, Evento, Pendiente, Registrar MP a todos, Nuevo pendiente)
    · ⊘ destructivo (Anular, Dar de baja)
    · ✓ confirmar/positivo (Oficializar, Aceptar maestro)
    · ✗ rechazar (Mantener programa)
    · ⏸ pausar (Posponer)
    · ✎ editar
    · 📊 Excel · 💾 Backup · 📥 Importar/Descargar · 📤 Subir · ↻ Reset
    · 🔍 Buscar · 🌞🌙 Tema
  - Tooltips informativos en botones de la ficha (qué hace cada acción).
  - Botones de bitácora con iconos: ✓ Oficializar, ✎ Editar, ⊘ Anular.
v0.21 [2026-05-28] Auto-completado en Conciliación: celdas vacías se llenan con datos del maestro.
  - Antes: cualquier diferencia generaba conflicto (con 894 equipos × 24 celdas
    inflaba la cola a >900).
  - Ahora: si el programa está vacío y el maestro tiene dato → auto-completa
    sin generar conflicto. Solo se genera conflicto cuando ambos tienen valor
    distinto, o el programa tiene dato y el maestro está vacío (protege dato).
  - Auto-completados de columna R con valor del catálogo MP (Si/C1-C8/etc) crean
    evento sintético "Mantención preventiva" con fecha día 15, marcado origen
    'conciliacion_auto' para trazabilidad.
  - Reporte de importación: nueva métrica "Auto-completados" en tarjetas de
    historial, con color verde si >0.
  - compararMaestro ahora retorna {conflictos, autoCompletados, eventosSinteticos}.
v0.20 [2026-05-28] Auditoría: registro masivo MP + asignación masiva + fecha sugerida + modal anulación.
  - Vista MP del mes: checkbox por fila + bulk-bar con:
    · "+ Registrar MP a todos" → modal con fecha/resultado/ejecutor/observación
      común, omite duplicados del mes por default.
    · "Asignar a ejecutor" en lote.
    · "Seleccionar todos los visibles".
  - Fecha sugerida: día 5 del mes seleccionado en lugar de hoy (patrón observado).
  - Anulación de evento ahora con modal: select de motivos predefinidos
    (Mal ingresado, Equipo equivocado, Fecha errónea, Resultado equivocado,
    Duplicado, Ejecutor equivocado, Documentación faltante, Otro) + detalle
    opcional. Reemplaza prompt() feo.
  - Audit: confirmado que no hay closures rotos, save no contabiliza saves
    internos en metrics.
v0.19 [2026-05-28] Fix: botones del tab Resumen no funcionaban.
  - Bug: renderResumenEquipo es función externa, sus botones "Resolver →",
    "Ver bitácora →", "Ver todos →", "Ver →" referenciaban tab/renderTabs/
    renderTabBody del closure de VIEWS.equipo → click no hacía nada.
  - Fix: VIEWS.equipo pasa callback setTab(name) que sí está en el closure
    correcto. Los 4 botones del Resumen ahora navegan.
  - Audit completo del resto del programa: no hay otros closures rotos.
v0.18 [2026-05-28] Dashboard: toggle "Por ejecutor / Por mes" en MP del mes.
  - Nueva tabla "MP del año por mes" con 12 filas: Programadas, Asignadas,
    Sin asignar, Ejecutadas, Pendientes, Cumplimiento %.
  - Toggle en el header de la sección persiste en prefs.mpSumModo.
  - Cada celda navega a MP del mes filtrada (mes + estadoMP/sinAsignar).
v0.17 [2026-05-28] Resumen del equipo + buscador global Ctrl+K + confirmación Oficializar.
  - Pestaña "Resumen" como default al abrir la ficha de un equipo. Consolida:
    matriz MP mini, últimos 3 eventos con resultado/oficialidad, pendientes
    abiertos, conflictos con maestro y ciclos correctivos abiertos.
    Cada bloque tiene link al tab detallado y acción rápida (+ Registrar MP).
  - Ctrl+K (o "/") abre buscador global flotante con autocompletado por inv,
    serie, equipo, marca, modelo, servicio, unidad, carpeta. Flechas + Enter
    para navegar resultados. Muestra estado y count de conflictos.
  - Oficializar evento ahora pide confirmación con:
    · Explicación de qué congela el oficializar.
    · Datos del evento (tipo, fecha, ejecutor, resultado).
    · Lista de documentos esperados según tipo (preventivo o correctivo).
v0.16 [2026-05-28] Conflictos visibles desde el equipo (sin pasar por Conciliación).
  - Tabla Equipos: nueva columna "Conf." con N° de conflictos pendientes por equipo
    (badge rojo si >0).
  - Ficha de equipo: tab "Conflictos (N)" cuando los hay, destacado en rojo.
    Render inline con acciones Aceptar/Mantener/Posponer por conflicto + botones
    masivos "Aceptar maestro a todos" / "Mantener programa en todos".
  - eq-info-card en modales de Pendiente, +Evento y +MP rápida: badge clickeable
    "N conflictos" que abre la ficha directo en el tab Conflictos.
  - Helper conflictosDe(inv) compartido. navigate(equipo,{openTab:'conflictos'})
    salta al tab al cargar.
v0.15 [2026-05-28] Tarjeta de info del equipo en modales.
  - Modal de pendiente, modal de "+ Evento" y modal "+ MP rápida" muestran
    ahora una eq-info-card con: N° Carpeta, Serie, Marca, Modelo, Servicio,
    Unidad, Ubicación, Frecuencia MP + estado actual + N° Inv.
  - En el modal de pendiente, link "Ver ficha →" para abrir la ficha completa.
  - Helper eqInfoCell para celdas con label/valor consistente.
  - Tema-aware (claro/oscuro).
v0.14 [2026-05-28] Rediseño dual theme + grabador auto-start enriquecido.
  - Tema claro suave (off-white tibio, acento verde-azul #0d7a6b) por default;
    toggle ☀/🌙 en el header conmuta a tema oscuro moderno. Persiste en prefs.theme.
  - Variables CSS organizadas con :root + [data-theme="dark"] para contraste AA.
  - Grabador auto-start al cargar la app (configurable en prefs.recorderAutoStart).
    Captura nuevos eventos:
    · think_time: pausas >3s entre acciones (señal de duda)
    · hover_long: hover >2s sobre el mismo elemento (una vez por elemento)
    · scroll_depth: hitos 25/50/75/100% por vista
    · form_error: cuando aparece toast tipo error
    · modal_abort: modal cerrado sin guardar (con campo descartado)
  - Al detener, calcula meta.metrics: vistas visitadas, eventos creados,
    clicks repetidos, tiempo activo vs idle, duración formularios.
v0.13 [2026-05-28] Agrupación de conflictos + hash de archivos + etiquetado.
  - Conciliación: nuevo selector "Agrupar por" (Sin agrupar / Tipo / Servicio /
    Equipo). En modo agrupado, cabecera por grupo con contador de pendientes y
    botones masivos "Aceptar maestro al grupo" / "Mantener programa al grupo".
    Mucho más rápido para procesar +900 conflictos.
  - Importaciones: cada subida calcula SHA-256 del contenido del archivo. Si
    el mismo hash ya fue importado, pide confirmación con la fecha y resumen
    de la importación previa. Evita acumular conflictos por reimportar el
    mismo .xlsm sin cambios.
  - Modal de pendiente: etiquetas más claras (Descripción / Tareas /
    Seguimientos) con separación visual mejorada para evitar confusión entre
    el textarea de descripción y el input de nueva tarea.
v0.12 [2026-05-28] Validación mes plantilla + migración estado desconocido.
  - subirPlantillaMP detecta el mes del nombre del archivo
    (Plantilla_Asignacion_<Mes>_<Año>.xlsx → Ene/Feb/.../Dic, Enero/Febrero/...).
    Si difiere del mes seleccionado en el dropdown, muestra diálogo con tres
    opciones: "Cargar en el mes del archivo", "Cargar en el mes del dropdown",
    "Cancelar". Evita asignaciones al mes equivocado por descuido.
  - Migración limpiarEfectosAnulados ahora también realinea equipos del state
    pre-v0.8: equipos con estado 'operativo' que no tienen ningún evento no
    anulado con estado declarado pasan a 'desconocido' (criterio actual).
v0.11 [2026-05-28] Resolución masiva de conflictos + evento sintético al aceptar.
  - FIX: al aceptar un conflicto mp_diferencia de la columna R con valor en el
    catálogo de resultados MP (Si/C1-C8/FS/NU/Baja/No), se crea automáticamente
    un evento sintético "Mantención preventiva" con fecha=día 15 del mes,
    resultado del maestro, observación "[Conciliación] origen importación
    maestro" y campo origen='conciliacion'. Soluciona el problema de bitácora
    vacía aunque la matriz mostraba la MP ejecutada.
  - Selección masiva en Conciliación:
    · Checkbox por cada card de conflicto.
    · Barra fija arriba con "N seleccionados" + 3 acciones bulk: Aceptar
      maestro, Mantener programa, Posponer.
    · Botón "Seleccionar todos los visibles" (respeta filtros activos).
    · Save único al final del bulk, no por cada conflicto (mucho más rápido
      con 958 conflictos).
    · Confirmación previa si seleccionas más de 50.
  - Toast resumen tras bulk: "X resueltos · Y eventos sintéticos creados".
v0.10 [2026-05-28] Plantillas de asignación MP del mes.
  - En la vista "MP del mes": 2 botones nuevos.
    · "Descargar plantilla": genera Plantilla_Asignacion_<Mes>_<Año>.xlsx con
      el formato exacto del usuario: hoja "Asignación" con las 13 columnas
      (N° Carpeta, N° Inventario, Equipo, Servicio, Unidad, Ubicación, Marca,
      Modelo, Serie, Año, Frecuencia MP, Programado en mes, Responsable) +
      hoja "Responsables_oficiales" con los 11 ejecutores como drop-down de
      validación en la columna Responsable.
    · "Subir plantilla": lee la hoja Asignación, valida cada fila contra el
      maestro y el catálogo de ejecutores, carga las asignaciones a
      state.asignacionesMP[keyMes]. Las asignaciones previas que no vienen
      en el archivo se conservan (no destructivo).
  - Reporte detallado tras subir: cuántas cargadas, sobrescritas, ignoradas
    (por inv no encontrado o ejecutor inválido).
  - 100% compatible con las plantillas que el usuario ya usa.
v0.9 [2026-05-28] Auditoría + visibilidad de eventos anulados.
  - FIX CRÍTICO de datos heredados: al cargar el state, migración limpia los
    efectos huérfanos de eventos anulados en versiones previas (v0.7 y antes
    no revertían). Si un evento MP anulado dejó un R="Si" en eq.registro y
    no hay otra MP no anulada en ese mes, se limpia. Se recalcula estado y
    ciclos. Idempotente: correr varias veces no rompe nada.
  - Bitácora ahora muestra TAMBIÉN los eventos anulados, con badge rojo
    "Anulado", texto tachado, motivo y fecha de anulación. Soluciona el
    problema de "no aparece mi registro en la bitácora" — ahora siempre
    queda visible la trazabilidad.
  - Contador de la pestaña Bitácora separa activos y anulados: "Bitácora (3 + 1 anulado)".
  - Auditoría: verificado que en todas las vistas y agregaciones los
    eventos anulados se excluyen de conteos productivos (MP del mes,
    matriz, dashboards, KPIs) pero se conservan en la bitácora.
v0.8 [2026-05-28] Reversión de eventos anulados + alertas + columnas.
  - FIX CRÍTICO: anular un evento ahora revierte sus efectos sobre el equipo.
    · Si era MP con resultado → limpia el R del mes en la matriz (o usa el
      siguiente más reciente del mismo mes).
    · Si declaró estado del equipo → recalcula desde el resto de eventos no anulados.
    · Si era Solicitud de trabajo → si no quedan más eventos en el ciclo, marca
      el ciclo como anulado.
    · Si era Reparación operativa que cerró el ciclo → reabre el ciclo si no hay
      otra reparación operativa posterior.
    · Si era MP con causal C1-C8 → anula también el pendiente automático generado.
  - Alerta al registrar MP en mes sin programación: si el equipo no tiene
    código X/R/RA/PM en el mes de la fecha → pregunta con la lista de meses
    programados antes de guardar.
  - Nuevo estado "desconocido" en la máquina: equipos sin eventos parten
    aquí (antes asumían 'operativo'). Visible en filtros y dashboard.
  - Excel: nueva columna "Creado" con timestamp completo (fecha + hora) en
    la hoja Eventos.
  - Tabla Equipos: se quitan columna y filtro de Frecuencia MP. Se agregan
    columnas ID y N° Carpeta a la izquierda.
  - Botón "← Volver" reimplementado con una pila de navegación propia, no
    depende de history.back() (que fallaba en archivos file://).
v0.7 [2026-05-28] Fixes UX detectados en sesión grabada.
  - Modal con confirmación al cerrar: si el formulario tiene datos sin guardar,
    pide confirmación antes de cerrar por click en el backdrop. Aplica a "+ Evento",
    "+ MP rápida" y "+ Pendiente". Evita perder formulario por click accidental.
  - Búsqueda en Eventos enriquecida con datos del equipo: serie, marca, modelo,
    ubicación, unidad. Buscar "ASNM-0003" en la vista Eventos ahora encuentra los
    eventos del equipo con esa serie.
  - Tooltip en celdas con resultado MP (Si/C1-C8/FS/NU/Baja): muestra fecha,
    ejecutor y observación del evento que dejó ese resultado, sin necesidad de click.
  - Indicador "N eventos hoy" en la ficha del equipo (cuando hay registros del día).
  - Auto-focus reforzado en MP rápida: fecha si vacío, ejecutor si fecha lista,
    observación si ya todo viene precargado.
  - Confirmación reforzada al anular eventos creados hace menos de 1 hora: muestra
    cuántos minutos pasaron desde la creación para evitar anular por error.
v0.6 [2026-05-28] Compresión de localStorage + auto-recuperación de cuota.
  - Embebida la librería lz-string (4.8 KB) para comprimir el state antes de
    guardar. Ratio típico observado: 14× (770 KB → 55 KB en UTF-16). Saca
    completamente al usuario del riesgo de cuota excedida con el state actual.
  - save() ahora guarda como "LZv1:..." comprimido. load() detecta el prefijo
    y descomprime automáticamente. Backward compatible con state v0.5 sin
    comprimir (lo lee, lo migra y reescribe comprimido).
  - Auto-recuperación si el setItem aún falla (state >5 MB después de
    comprimir): descarga el backup, poda conflictos resueltos del historial,
    reintenta el save. Si sigue fallando, ofrece reset preservando equipos +
    eventos críticos.
  - Diálogo del error de cuota explica exactamente cuántos resueltos hay para
    podar y qué se mantiene.
v0.5 [2026-05-28] Protección anti-pérdida de datos.
  - Banner de bienvenida en el Dashboard cuando se detecta state "fresh"
    (sin eventos del usuario sobre el seed) con drop-zone integrada para
    importar backup JSON al instante.
  - Indicador en el header: nº de eventos del usuario y fecha de la última
    actualización, con tooltip explicando dónde está el localStorage.
  - Auto-backup: cada 10 cambios significativos (eventos/pendientes/MPs/
    conflictos resueltos) muestra toast persistente "Backup recomendado"
    con botón directo de descarga.
  - Drop-zone para importar visible también en la pantalla vacía.
  - Mensaje educativo al detectar pérdida: explica la limitación de localStorage
    per-file de Chrome (mover el archivo a otra carpeta = otro storage) y
    recomienda exportar al cerrar la sesión.
  - Migración no-destructiva v0.4 → v0.5 (sin cambios estructurales).
v0.4 [2026-05-28] Fix fechas, MP rápida, export Excel, mejoras de tiempo.
  - FIX CRÍTICO: bug de zona horaria al mostrar fechas. fmtFecha() ahora trata
    "YYYY-MM-DD" como fecha local (no UTC), por lo que ya no aparece corrida
    un día atrás en zonas UTC negativas.
  - Exportar a Excel: nuevo botón "Excel" en el header. Genera .xlsx con 6 hojas:
    Equipos, PMP_2026 (espejo del maestro), Registro_MP-2026 (espejo), Eventos,
    Pendientes, Conflictos. Listo para pegar en la planilla oficial.
  - MP rápida: nuevo botón "+ MP" en la ficha del equipo y en la vista MP del mes.
    Modal mínimo con 4 campos (fecha, resultado, ejecutor, observación) que
    recuerda el último ejecutor/resultado entre registros consecutivos.
  - Click en una celda P programada y sin resultado en la matriz MP → abre MP rápida
    con la fecha del mes pre-llenada.
  - Auto-focus en el buscador de Equipos al entrar a la vista.
  - Toast persiste 4 s (era 2.8 s) y muestra acción "Ver" cuando aplica.
  - Persistencia de preferencias del usuario (último ejecutor, último resultado MP).
  - Regresiones verificadas: conciliación con maestro, dashboard, 7 tipos de evento,
    ciclo correctivo, pendientes auto C1, ficha completa, grabador, persistencia.
v0.3 [2026-05-28] Conciliación con archivo maestro.
  - Nueva vista "Conciliación" + badge de conflictos pendientes en nav.
  - Importación del .xlsm/.xlsx del maestro vía SheetJS mini embebido inline (~250 KB),
    funciona 100% offline sin CDN.
  - Comparación celda a celda de las matrices P (PMP_2026) y P+R (Registro_MP-2026)
    en los 12 meses, sin sobreescribir nada.
  - 3 tipos de conflicto: mp_diferencia (celda distinta), equipo_nuevo (en maestro
    pero no en programa), equipo_faltante (en programa pero no en maestro).
  - 4 acciones por conflicto: aceptar maestro · mantener programa · editar manualmente · posponer.
  - Marca visual de conflicto pendiente en la matriz MP de la ficha del equipo (borde rojo + tooltip).
  - Historial de importaciones: archivo, fecha, totales generados/resueltos/pendientes.
  - Valores fuera de catálogo (ej. "S2") se conservan y muestran; el sistema no decide.
  - Re-subir el mismo maestro no duplica conflictos: actualiza los existentes.
  - Audit log: cada resolución de conflicto registra usuario, timestamp, acción y valor final.
  - Regresiones verificadas: dashboard rediseñado, 7 tipos de evento, ciclo correctivo,
    pendientes auto C1, ficha de equipo, MP del mes, grabador de sesión, export/import/reset.
-->
<style>
:root{
  /* Tema CLARO minimalista — neutro frío, acento azul */
  --bg:#f5f6f8;
  --surface:#ffffff;
  --surface-2:#eef1f5;
  --border:#e6e9ee;
  --border-strong:#d2d7df;
  --text:#161a20;
  --text-2:#39414d;
  --muted:#6b7280;
  --muted-2:#9aa1ac;
  --accent:#2563eb;
  --accent-2:#1d4ed8;
  --accent-soft:#e7eefe;
  --hover:#eef2f7;
  --soft:#eef1f5;
  --op:#15803d;
  --noop:#dc2626;
  --st:#b45309;
  --baja:#6b7280;
  --shadow-sm:0 1px 2px rgba(16,24,40,.05);
  --shadow:0 1px 3px rgba(16,24,40,.08),0 1px 2px rgba(16,24,40,.04);
  --shadow-lg:0 10px 30px rgba(16,24,40,.12);
  --font:-apple-system,BlinkMacSystemFont,"Inter","Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
[data-theme="dark"]{
  /* Tema OSCURO — gris-azul profundo, acento azul */
  --bg:#0f1216;
  --surface:#161a20;
  --surface-2:#1e232b;
  --border:#272d36;
  --border-strong:#39404a;
  --text:#e7eaee;
  --text-2:#c2c7cf;
  --muted:#8b919b;
  --muted-2:#5b616b;
  --accent:#3b82f6;
  --accent-2:#60a5fa;
  --accent-soft:#172338;
  --hover:#1e232b;
  --soft:#161a20;
  --op:#4ade80;
  --noop:#f87171;
  --st:#fbbf24;
  --baja:#8b919b;
  --shadow-sm:0 1px 2px rgba(0,0,0,.3);
  --shadow:0 2px 8px rgba(0,0,0,.35);
  --shadow-lg:0 12px 28px rgba(0,0,0,.5);
}
*{box-sizing:border-box}
html,body{margin:0;padding:0;height:100%;font-family:var(--font);font-size:13.5px;color:var(--text);background:var(--bg);-webkit-font-smoothing:antialiased;font-feature-settings:"cv11","ss01";line-height:1.45;transition:background-color .2s,color .2s}
.theme-btn{font-size:14px;width:30px;height:28px;padding:0!important;display:inline-flex;align-items:center;justify-content:center;border:1px solid var(--border)!important}
button{font-family:inherit;font-size:inherit;cursor:pointer;border:1px solid var(--border-strong);background:var(--surface);color:var(--text);padding:5px 11px;border-radius:6px;transition:background .12s,border-color .12s,color .12s,box-shadow .12s;font-weight:500}
button:hover:not(:disabled){background:var(--hover)}
button:disabled{opacity:.4;cursor:not-allowed}
button.primary{background:var(--accent);color:#fff;border-color:var(--accent)}
button.primary:hover:not(:disabled){background:var(--accent-2);border-color:var(--accent-2)}
button.danger{background:#fff;color:var(--noop);border-color:#e8c8c5}
button.danger:hover:not(:disabled){background:#fff5f4;border-color:var(--noop)}
button.small{padding:3px 9px;font-size:12px}
button.ghost{border-color:transparent;background:transparent;color:var(--muted)}
button.ghost:hover{background:var(--hover);color:var(--text)}
input,select,textarea{font-family:inherit;font-size:inherit;padding:6px 9px;border:1px solid var(--border-strong);border-radius:6px;background:var(--surface);color:var(--text);width:100%}
input:focus,select:focus,textarea:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-soft)}
input[readonly]{background:var(--soft);color:var(--muted)}
label{display:block;font-size:11px;color:var(--muted);margin-bottom:4px;font-weight:500;text-transform:uppercase;letter-spacing:.04em}
textarea{min-height:64px;resize:vertical;font-family:inherit;line-height:1.5}

.app{display:grid;grid-template-columns:230px 1fr;height:100vh;overflow:hidden;background:var(--bg);transition:grid-template-columns .18s ease}
.app.sb-collapsed{grid-template-columns:0 1fr}
/* Barra lateral oscura, contraíble */
.sidebar{background:#0f172a;color:#cbd5e1;display:flex;flex-direction:column;overflow-y:auto;overflow-x:hidden;white-space:nowrap}
.s-logo{padding:18px 16px 14px;font-weight:700;font-size:16px;color:#fff;letter-spacing:-.01em}
.s-logo small{display:block;font-weight:500;font-size:10px;color:#64748b;margin-top:3px;text-transform:uppercase;letter-spacing:.04em}
.sidebar nav{display:flex;flex-direction:column;gap:2px;padding:8px 10px;flex:1}
.sidebar nav button{display:flex;align-items:center;gap:10px;width:100%;text-align:left;background:transparent;border:none;color:#cbd5e1;padding:10px 12px;border-radius:8px;font-weight:500;font-size:13.5px;cursor:pointer;transition:background .12s,color .12s}
.sidebar nav button:hover{background:#1e293b;color:#fff}
.sidebar nav button.active{background:var(--accent);color:#fff;font-weight:600}
.sidebar nav button .nav-badge{margin-left:auto;background:var(--noop);color:#fff;border-radius:99px;font-size:11px;font-weight:700;padding:1px 8px;min-width:18px;text-align:center;line-height:1.5}
.sidebar .s-group{font-size:10px;font-weight:700;letter-spacing:.08em;color:#475569;text-transform:uppercase;padding:14px 12px 5px}
.s-foot{padding:12px 16px;border-top:1px solid rgba(255,255,255,.08);font-size:12px;color:#94a3b8}
.content{display:grid;grid-template-rows:48px 1fr;overflow:hidden;min-width:0}
.topbar{display:flex;align-items:center;gap:6px;padding:0 14px;background:var(--surface);border-bottom:1px solid var(--border)}
.topbar button{font-size:12.5px;padding:5px 10px;color:var(--muted);border:1px solid var(--border);border-radius:6px;background:var(--surface)}
.topbar button:hover{color:var(--text);background:var(--surface-2)}
.sb-toggle{border:none!important;background:transparent!important;color:var(--muted);font-size:17px!important;padding:4px 9px!important;border-radius:6px;line-height:1}
.sb-toggle:hover{background:var(--surface-2)!important;color:var(--text)}
.quick-access{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}
.qa-btn{font-size:13px;font-weight:600;padding:8px 14px;border-radius:99px;border:1px solid var(--border-strong);background:var(--surface);color:var(--text-2);cursor:pointer;transition:.12s}
.qa-btn:hover{background:var(--surface-2);box-shadow:var(--shadow-sm)}
.qa-btn.st{border-color:#ecd4a3;color:var(--st)}
.qa-btn.noop{border-color:#f0c5c1;color:var(--noop)}
.th-sort{cursor:pointer;white-space:nowrap;user-select:none}
.th-sort:hover{color:var(--accent)}
tr.filtros-col th{position:static;background:var(--surface-2);padding:4px 6px}
tr.filtros-col input,tr.filtros-col select{width:100%;font-size:11px;padding:5px 7px;border-radius:6px;font-weight:400}
.mp-col{text-align:center;min-width:30px}
td.mp-ok{color:var(--op);font-weight:700}
td.mp-rep{color:var(--st);font-weight:600}
header.top h1{font-size:14px;margin:0;font-weight:600;letter-spacing:-.01em}
header.top h1 small{font-weight:400;color:var(--muted);margin-left:8px}
header.top nav{display:flex;gap:0;flex:1;align-items:center;height:100%}
header.top nav button{background:transparent;border:none;color:var(--muted);padding:0 14px;height:100%;border-radius:0;border-bottom:2px solid transparent;font-weight:500;font-size:13px;letter-spacing:-.005em}
header.top nav button:hover{color:var(--text);background:transparent}
header.top nav button.active{color:var(--text);border-bottom-color:var(--accent)}
header.top .tools{display:flex;gap:4px;align-items:center;font-size:12px}
header.top .tools button{font-size:12px;padding:5px 10px;color:var(--muted);border:1px solid var(--border)}
header.top .tools button:hover{color:var(--text);background:var(--hover)}
header.top .user-tag{color:var(--muted);font-size:12px;margin-right:6px}

main{overflow:auto;padding:28px 32px 60px}
.view{max-width:1280px;margin:0 auto}
.view h2{margin:0 0 6px;font-size:22px;font-weight:600;letter-spacing:-.015em}
.view h3{margin:24px 0 12px;font-size:13px;font-weight:600;color:var(--text);text-transform:uppercase;letter-spacing:.05em}
.subtitle{color:var(--muted);font-size:13px;margin-bottom:24px}

/* KPI strip — minimal */
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:0;border:1px solid var(--border);border-radius:6px;margin-bottom:28px;background:var(--surface);overflow:hidden}
.kpi{padding:14px 18px;border-right:1px solid var(--border);cursor:pointer;transition:background .1s}
.kpi:last-child{border-right:none}
.kpi:hover{background:var(--hover)}
.kpi .lbl{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;font-weight:500;margin-bottom:6px}
.kpi .val{font-size:24px;font-weight:600;color:var(--text);letter-spacing:-.02em}
.kpi .val small{font-size:12px;color:var(--muted);font-weight:400;margin-left:4px}
.kpi.alert .val{color:var(--noop)}
.kpi.warn .val{color:var(--st)}

/* Summary tables — clickeables */
.sum-table{width:100%;border-collapse:collapse;background:var(--surface);border:1px solid var(--border);border-radius:6px;overflow:hidden;font-size:13px;margin-bottom:24px}
.sum-table th{background:var(--surface-2);text-align:right;padding:10px 12px;font-weight:500;border-bottom:1px solid var(--border);color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap}
.sum-table th:first-child{text-align:left}
.sum-table td{padding:9px 12px;border-bottom:1px solid var(--border);text-align:right;font-variant-numeric:tabular-nums}
.sum-table td:first-child{text-align:left;font-weight:500;color:var(--text)}
.sum-table tr:last-child td{border-bottom:none}
.sum-table tr.total-row{background:var(--surface-2);font-weight:600}
.sum-table tr.total-row td{border-top:1px solid var(--border-strong)}
.sum-table tr:hover:not(.total-row){background:var(--soft)}
.sum-table td.cell{cursor:pointer;color:var(--text);transition:color .1s}
.sum-table td.cell:hover{color:var(--accent-2);background:#f0f7ff}
.sum-table td.cell.zero{color:var(--muted-2);cursor:default}
.sum-table td.cell.zero:hover{color:var(--muted-2);background:transparent}
.sum-table td.cell .v{font-weight:500}
.sum-section{margin-bottom:32px}
.sum-section-hd{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:10px}
.sum-section-hd h3{margin:0}
.sum-section-hd .hint{font-size:12px;color:var(--muted)}

/* Toolbar */
.toolbar{display:flex;gap:8px;align-items:center;margin-bottom:14px;flex-wrap:wrap}
.toolbar .grow{flex:1;min-width:240px}
.toolbar input[type=search]{padding-left:34px;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23888' stroke-width='2'><circle cx='11' cy='11' r='7'/><path d='m21 21-4.3-4.3'/></svg>");background-repeat:no-repeat;background-position:11px center;background-size:15px}

/* Filter chips */
.filters{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-bottom:14px;min-height:24px}
.filter-chip{display:inline-flex;align-items:center;gap:6px;padding:3px 10px;background:var(--soft);border:1px solid var(--border);border-radius:99px;font-size:12px;color:var(--text-2)}
.filter-chip .x{cursor:pointer;color:var(--muted);font-weight:500}
.filter-chip .x:hover{color:var(--text)}
.filter-chip .k{color:var(--muted);font-size:11px}
.filter-clear{font-size:12px;color:var(--muted);cursor:pointer;padding:3px 8px;border:none;background:transparent}
.filter-clear:hover{color:var(--text);text-decoration:underline}

/* Data tables */
table.data{width:100%;border-collapse:collapse;background:var(--surface);border:1px solid var(--border);border-radius:6px;overflow:hidden;font-size:13px}
table.data th{background:var(--surface-2);text-align:left;padding:7px 10px;font-weight:600;border-bottom:1px solid var(--border);color:var(--muted);white-space:nowrap;position:sticky;top:0;z-index:1;font-size:11px;text-transform:uppercase;letter-spacing:.03em}
table.data td{padding:6px 10px;border-bottom:1px solid var(--border);vertical-align:top}
table.data tbody tr:hover td{background:var(--hover)}
table.data tr:last-child td{border-bottom:none}
table.data tr.clickable{cursor:pointer}
table.data tr.clickable:hover{background:var(--soft)}
table.data td.actions{white-space:nowrap;text-align:right}
table.data .num{font-variant-numeric:tabular-nums;text-align:right}

/* Badges — bordes en lugar de fondos pesados */
.badge{display:inline-block;padding:1px 8px;border-radius:99px;font-size:11px;font-weight:500;line-height:1.7;white-space:nowrap;border:1px solid var(--border-strong);background:var(--surface);color:var(--text-2)}
.badge.op{color:var(--op);border-color:#bbe2c9;background:#f0faf3}
.badge.noop{color:var(--noop);border-color:#f0c5c1;background:#fdf3f2}
.badge.st{color:var(--st);border-color:#ecd4a3;background:#fdf6e8}
.badge.baja{color:var(--baja);border-color:var(--border-strong);background:var(--soft)}
.badge.desconocido{color:var(--muted);border-color:var(--border);background:#fafafa;font-style:italic}
.badge.creado{color:var(--muted);background:var(--soft)}
.badge.abierto{color:var(--st);border-color:#ecd4a3;background:#fdf6e8}
.badge.cerrado{color:var(--op);border-color:#bbe2c9;background:#f0faf3}
.badge.ofic-si{color:var(--accent);border-color:var(--accent);background:var(--accent-soft)}
.badge.ofic-no{color:var(--muted);background:var(--soft)}
.badge.mp-si{color:var(--op);border-color:#bbe2c9;background:#f0faf3}
.badge.mp-cause{color:var(--st);border-color:#ecd4a3;background:#fdf6e8}
.badge.mp-no{color:var(--noop);border-color:#f0c5c1;background:#fdf3f2}
.tag{display:inline-block;padding:1px 7px;border-radius:3px;font-size:11px;background:var(--soft);color:var(--muted);margin-right:4px;border:1px solid var(--border)}
.pill{display:inline-block;padding:1px 7px;font-size:11px;border-radius:3px;background:var(--soft);color:var(--muted);margin-left:6px;font-variant-numeric:tabular-nums}

/* Empty states */
.empty{text-align:center;padding:48px 24px;color:var(--muted);background:var(--surface);border:1px dashed var(--border);border-radius:6px;font-size:13px}
.empty.small{padding:22px}

/* Layout helpers */
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.row{display:flex;gap:10px;align-items:flex-end}
.row > *{flex:1}

/* Section card */
.section{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:15px;margin-bottom:15px;box-shadow:var(--shadow-sm)}
/* Ficha: secciones contraíbles (cap. 4 de la especificación) */
.ficha-sec{background:var(--surface);border:1px solid var(--border);border-radius:8px;margin-bottom:12px;overflow:hidden}
.ficha-sec>summary{cursor:pointer;list-style:none;padding:13px 16px;font-weight:600;font-size:14px;display:flex;align-items:center;gap:8px;user-select:none}
.ficha-sec>summary::-webkit-details-marker{display:none}
.ficha-sec>summary::before{content:'▸';color:var(--muted);transition:transform .15s;font-size:12px}
.ficha-sec[open]>summary::before{transform:rotate(90deg)}
.ficha-sec>summary:hover{background:var(--bg)}
.ficha-sec-body{padding:4px 16px 16px}
.ficha-sec-body>.section{border:none;padding:0;margin:0;background:transparent}
/* Buscar equipos: la fila completa abre la ficha al hacer clic */
.eq-grid tbody tr.row-click{cursor:pointer}
.eq-grid tbody tr.row-click:hover td{background:var(--bg)}
/* "Ajustar a pantalla" (ancho 100%, títulos que envuelven, sin scroll lateral) SOLO para
   Buscar equipos (13 columnas). NO para Registro MP, que tiene ~42 columnas y necesita
   desplazamiento horizontal: ahí se dejan anchos naturales. */
/* La planilla cabe en el ancho de la pantalla (sin scroll lateral): títulos que
   envuelven, celdas que parten palabras largas y espaciado compacto. */
.buscar-grid{width:100%}
.buscar-grid th.th-sort{white-space:normal;vertical-align:bottom}
.buscar-grid th,.buscar-grid td{padding:7px 8px;font-size:12px;overflow-wrap:anywhere;word-break:break-word}
.section h3{margin-top:0}

/* Key-value */
.kv{display:grid;grid-template-columns:140px 1fr;gap:8px 16px;font-size:13px}
.kv dt{color:var(--muted);font-weight:400}
.kv dd{margin:0;color:var(--text)}

/* MP matrix */
.mp-matrix{width:100%;border-collapse:collapse;font-size:12px;background:var(--surface);font-variant-numeric:tabular-nums}
.mp-matrix th,.mp-matrix td{border:1px solid var(--border);padding:6px 8px;text-align:center;min-width:46px}
.mp-matrix th{background:var(--surface-2);font-weight:500;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.05em}
.mp-matrix .lbl-row{background:var(--surface-2);text-align:right;font-weight:500;color:var(--muted);padding-right:12px}
.mp-cell-x{background:#fef9c3;color:#854d0e}
.mp-cell-r{background:#ede9fe;color:#5b21b6}
.mp-cell-ra{background:#fce7f3;color:#9d174d}
.mp-cell-pm{background:#dbeafe;color:#1e40af}
.mp-cell-si{background:#dcfce7;color:#166534}
.mp-cell-c{background:#fed7aa;color:#9a3412}
.mp-cell-fs{background:#fecaca;color:#991b1b}
.mp-cell-baja{background:#e5e7eb;color:#374151}
.mp-cell-nu{background:#fef3c7;color:#854d0e}

/* Modal */
.modal-backdrop{position:fixed;inset:0;background:rgba(17,17,17,.45);display:flex;align-items:center;justify-content:center;z-index:100;padding:24px}
.modal{background:var(--surface);border-radius:8px;box-shadow:0 20px 50px rgba(0,0,0,.18);max-width:780px;width:100%;max-height:92vh;display:flex;flex-direction:column}
.modal.wide{max-width:1100px}
.modal header{display:flex;justify-content:space-between;align-items:center;padding:18px 22px;border-bottom:1px solid var(--border)}
.modal header h2{margin:0;font-size:16px;font-weight:600;letter-spacing:-.01em}
.modal .body{padding:22px;overflow:auto;flex:1}
.modal footer{padding:14px 22px;border-top:1px solid var(--border);display:flex;justify-content:flex-end;gap:8px;background:var(--surface-2)}

/* Bitácora */
.bitacora{display:flex;flex-direction:column;gap:0}
.bitacora .ev{border-bottom:1px solid var(--border);padding:14px 0;font-size:13px}
.bitacora .ev:last-child{border-bottom:none}
.bitacora .ev.anulado{opacity:.55;background:#fef2f2;margin:0 -8px;padding-left:8px;padding-right:8px;border-bottom-color:#fecaca}
.bitacora .ev.anulado .hd strong{text-decoration:line-through;color:var(--muted)}
.bitacora .ev.anulado .obs{text-decoration:line-through;color:var(--muted)}
.bitacora .ev.auto{background:linear-gradient(to right, rgba(13,122,107,.06), transparent);border-left:3px solid var(--accent);margin:0 -8px;padding-left:8px;padding-right:8px}
.badge.auto-badge{color:var(--accent);border-color:var(--accent);background:var(--accent-soft);font-weight:600;cursor:help}
.badge.anulado-badge{color:var(--noop);border-color:#f0c5c1;background:#fdf3f2;font-weight:600}
.anulacion-info{margin-top:6px;padding:6px 10px;background:#fef2f2;border:1px solid #fecaca;border-radius:4px;font-size:12px;color:#991b1b;font-style:italic}
.bitacora .ev .hd{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;gap:8px;flex-wrap:wrap}
.bitacora .ev .hd strong{font-size:13px;font-weight:600}
.bitacora .ev .hd .fecha{color:var(--muted);font-size:12px;font-variant-numeric:tabular-nums}
.bitacora .ev .meta{color:var(--muted);font-size:12px;margin-bottom:6px}
.bitacora .ev .obs{color:var(--text-2);font-size:13px;white-space:pre-wrap;line-height:1.5;padding:6px 0}

.ciclo-card{border:1px solid var(--border);border-left:3px solid var(--st);padding:12px 14px;border-radius:0 4px 4px 0;margin-bottom:8px;background:var(--surface)}
.ciclo-card.cerrado{border-left-color:var(--op)}

/* Tabs */
.tabs{display:flex;border-bottom:1px solid var(--border);margin-bottom:18px;gap:0;overflow-x:auto}
.tabs button{background:transparent;border:none;padding:11px 16px;border-radius:0;border-bottom:2px solid transparent;color:var(--muted);font-weight:500;white-space:nowrap;font-size:13px}
.tabs button.active{color:var(--text);border-bottom-color:var(--accent)}
.tabs button:hover:not(.active){color:var(--text);background:transparent}

/* Notice */
.notice{padding:10px 14px;border-radius:4px;margin-bottom:14px;font-size:13px;border:1px solid var(--border)}
.notice.warn{background:#fef9c3;color:#854d0e;border-color:#fde68a}
.notice.info{background:#eff6ff;color:#1e40af;border-color:#bfdbfe}
.notice.danger{background:#fef2f2;color:#991b1b;border-color:#fecaca}

/* Toast */
.toast{position:fixed;bottom:22px;right:22px;background:var(--text);color:#fff;padding:11px 18px;border-radius:6px;font-size:13px;z-index:200;animation:slideUp .25s ease;max-width:420px;box-shadow:0 8px 20px rgba(0,0,0,.2);display:flex;align-items:center;gap:14px}
.toast.error{background:var(--noop)}
.toast.success{background:var(--op)}
.toast-action{background:transparent;border:1px solid rgba(255,255,255,.4);color:#fff;padding:3px 10px;font-size:12px;border-radius:4px;cursor:pointer;font-weight:500}
.toast-action:hover{background:rgba(255,255,255,.12)}
@keyframes slideUp{from{transform:translateY(20px);opacity:0}to{transform:translateY(0);opacity:1}}

/* Recorder — sin cambios */
.rec-widget{position:fixed;bottom:18px;left:18px;background:#0f172a;color:#fff;border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,.18);font-size:12px;z-index:150;user-select:none;min-width:180px}
.rec-widget.minimized{min-width:auto}
.rec-widget .rw-hd{padding:8px 10px;cursor:move;display:flex;justify-content:space-between;align-items:center;gap:8px;border-bottom:1px solid #1e293b}
.rec-widget .rw-hd .ttl{font-weight:600;font-size:12px;letter-spacing:.3px}
.rec-widget .rw-hd .dot{display:inline-block;width:8px;height:8px;border-radius:99px;background:#475569;margin-right:5px;vertical-align:middle}
.rec-widget.recording .rw-hd .dot{background:#dc2626;animation:pulse 1.2s infinite}
.rec-widget.paused .rw-hd .dot{background:var(--st)}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}
.rec-widget .rw-bd{padding:8px 10px;display:flex;flex-direction:column;gap:6px}
.rec-widget.minimized .rw-bd{display:none}
.rec-widget button{background:#1e293b;color:#fff;border:1px solid #334155;padding:5px 9px;border-radius:4px;font-size:11px;font-weight:500}
.rec-widget button:hover{background:#334155}
.rec-widget .row{display:flex;gap:5px}
.rec-widget .row button{flex:1}
.rec-widget .info{font-size:11px;color:#94a3b8;text-align:center}
.rec-widget .ghost-btn{background:transparent;border:none;color:#94a3b8;padding:2px 5px;font-size:14px;line-height:1}
.rec-widget .ghost-btn:hover{color:#fff;background:transparent}

small.muted{color:var(--muted);font-size:11px}

.event-type-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin-bottom:18px}
.event-type-grid button{text-align:left;padding:12px 14px;border-radius:6px}
.event-type-grid button strong{display:block;margin-bottom:3px;font-weight:600}
.event-type-grid button small{color:var(--muted);font-size:11px}
.event-type-grid button.selected{background:var(--accent);color:#fff;border-color:var(--accent)}
.event-type-grid button.selected small{color:rgba(255,255,255,.75)}

/* Mini bar chart (sparkline-ish) */
.bar{display:inline-block;height:4px;background:var(--accent);border-radius:99px;vertical-align:middle;margin-right:6px}

/* Nav badge para conciliación */
header.top nav button .nav-badge{display:inline-block;margin-left:6px;padding:0 6px;background:var(--noop);color:#fff;border-radius:99px;font-size:10px;font-weight:600;line-height:14px;height:14px;vertical-align:middle;min-width:14px;text-align:center}

/* Conflict markers en matriz MP */
.mp-matrix td.has-conflict{outline:2px solid var(--noop);outline-offset:-2px;position:relative}
.mp-matrix td.has-conflict::after{content:"!";position:absolute;top:0;right:2px;font-size:10px;color:var(--noop);font-weight:700;line-height:1}

/* Conciliación */
.conf-row{display:flex;gap:0;margin-bottom:10px;align-items:stretch}
.conf-checkbox{padding:18px 8px 0 0;display:flex;align-items:flex-start;justify-content:center;min-width:32px}
.conf-checkbox input[type=checkbox]{width:18px;height:18px;cursor:pointer;margin:0}
.conf-row .conf-card{flex:1;margin-bottom:0}
/* Toggle group para alternar vistas */
.toggle-group{display:inline-flex;border:1px solid var(--border-strong);border-radius:4px;overflow:hidden}
.toggle-group button{border:none!important;border-radius:0!important;padding:4px 10px!important;font-size:12px!important}
.toggle-group button:first-child{border-right:1px solid var(--border-strong)!important}

/* Quick search (Ctrl+K) */
.quick-search{display:flex;flex-direction:column;gap:10px}
.quick-search-input{font-size:16px;padding:12px 14px}
.quick-search-results{max-height:60vh;overflow-y:auto;display:flex;flex-direction:column;gap:4px}
.qs-hint{padding:14px;color:var(--muted);font-size:13px;font-style:italic;text-align:center}
.qs-row{display:grid;grid-template-columns:120px 1fr auto auto;gap:12px;align-items:center;padding:8px 12px;border-radius:4px;cursor:pointer;border:1px solid transparent}
.qs-row:hover,.qs-row.selected{background:var(--accent-soft);border-color:var(--accent)}
.qs-row .qs-inv{font-family:var(--mono);font-size:13px;color:var(--text);font-weight:600}
.qs-row .qs-eq strong{font-size:13px}
.qs-row .qs-meta{font-size:11px;color:var(--muted);margin-top:2px}

/* Resumen de equipo */
.resumen-grid{display:grid;grid-template-columns:1fr;gap:14px}
.resumen-block{margin-bottom:0}
.resumen-block-hd{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:12px;flex-wrap:wrap}
.resumen-block-hd h3{margin:0}
.resumen-block-warn{border-left:3px solid var(--noop)}
.resumen-events{display:flex;flex-direction:column;gap:10px}
.resumen-event-row{padding:10px 12px;background:var(--surface-2);border-radius:4px;display:grid;grid-template-columns:90px 1fr 160px;gap:10px;align-items:center;font-size:13px}
.resumen-event-row .rev-fecha{font-family:var(--mono);font-size:12px;color:var(--muted)}
.resumen-event-row .rev-obs{grid-column:1/-1;font-size:12px;color:var(--text-2);padding-top:6px;border-top:1px dashed var(--border);margin-top:4px}
.resumen-pend-row{display:flex;gap:10px;padding:8px 0;border-bottom:1px solid var(--border);align-items:center;cursor:pointer;font-size:13px}
.resumen-pend-row:hover{background:var(--hover);margin:0 -8px;padding:8px 8px;border-radius:4px}
.resumen-pend-row:last-child{border-bottom:none}
.resumen-pend-row .rev-pend-desc{flex:1;color:var(--text-2)}
.resumen-pend-row .rev-pend-comp{font-size:11px;color:var(--muted);font-variant-numeric:tabular-nums}
@media (max-width:900px){
  .resumen-event-row{grid-template-columns:1fr}
}

/* Tab Conflictos destacado */
.tabs button.tab-conflict{color:var(--noop)!important;font-weight:600}
.tabs button.tab-conflict.active{border-bottom-color:var(--noop)!important}
.conflict-badge{cursor:pointer;transition:opacity .1s}
.conflict-badge:hover{opacity:.8}

/* Equipo info card en modales */
.eq-info-card{background:var(--surface-2);border:1px solid var(--border);border-radius:6px;padding:14px 16px;margin-bottom:18px}
.eq-info-hd{display:flex;align-items:center;gap:10px;margin-bottom:12px;padding-bottom:10px;border-bottom:1px solid var(--border);flex-wrap:wrap}
.eq-info-hd strong{font-size:15px;font-weight:600;color:var(--text)}
.eq-info-inv{color:var(--muted);font-family:var(--mono);font-size:13px}
.eq-info-link{margin-left:auto !important;font-size:12px}
.eq-info-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px 16px}
.eq-info-cell{font-size:12px}
.eq-info-lbl{color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.05em;font-weight:500;margin-bottom:2px}
.eq-info-val{color:var(--text);font-weight:500;font-size:13px;font-variant-numeric:tabular-nums;word-break:break-word}
.eq-info-val.empty{color:var(--muted-2);font-style:italic;font-weight:400}

/* Pendiente modal: secciones más claras */
.pend-section{margin:18px 0;padding:14px;border:1px solid var(--border);border-radius:6px;background:var(--surface-2)}
.pend-section .pend-section-lbl{display:block;font-size:12px;font-weight:600;color:var(--text);text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px}
.pend-section .pend-section-hint{font-size:11px;color:var(--muted);margin-bottom:10px;font-style:italic}
.pend-section textarea, .pend-section input[type=text]{background:var(--surface)}
.pend-new-row{display:flex;align-items:center;gap:8px;margin-top:8px}
.pend-new-row .plus-icon{display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;background:var(--accent);color:#fff;font-weight:700;flex-shrink:0;font-size:14px}
.pend-new-row input{flex:1}

.conf-group{margin-bottom:14px;border:1px solid var(--border);border-radius:6px;background:var(--surface);overflow:hidden}
.conf-group-hd{display:flex;align-items:center;gap:10px;padding:10px 14px;background:var(--surface-2);border-bottom:1px solid var(--border);flex-wrap:wrap}
.conf-group-hd .tw{cursor:pointer;color:var(--muted);font-size:11px;width:14px;display:inline-block}
.conf-group-hd .lbl{cursor:pointer;font-weight:600;font-size:13px;flex:1;color:var(--text)}
.conf-group-hd .cnt{font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}
.conf-group-hd .acts{display:flex;gap:5px;flex-wrap:wrap}
.conf-group-bd{padding:10px 12px;background:var(--surface)}
.conf-group-bd .conf-row{margin-bottom:8px}
.conf-group-bd .conf-row:last-child{margin-bottom:0}

.bulk-bar{position:sticky;top:0;z-index:20;background:var(--accent);color:#fff;padding:10px 16px;border-radius:6px;margin-bottom:14px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;box-shadow:0 4px 12px rgba(0,0,0,.15)}
.bulk-bar .bulk-count{font-weight:600;font-size:13px;margin-right:6px}
.bulk-bar button{background:rgba(255,255,255,.12);color:#fff;border:1px solid rgba(255,255,255,.3);font-weight:500}
.bulk-bar button:hover{background:rgba(255,255,255,.2);border-color:rgba(255,255,255,.5)}
.bulk-bar button.primary{background:#fff;color:var(--accent);border-color:#fff}
.bulk-bar button.primary:hover{background:#f5f5f5}

.conf-card{border:1px solid var(--border);border-radius:6px;background:var(--surface);padding:14px 16px;margin-bottom:10px}
.conf-card.urgent{border-left:3px solid var(--noop)}
.conf-card.altas{border-left:3px solid var(--accent-2)}
.conf-card.faltante{border-left:3px solid var(--st)}
.conf-card .hd{display:flex;justify-content:space-between;align-items:start;gap:10px;flex-wrap:wrap;margin-bottom:8px}
.conf-card .hd .title{font-weight:600;font-size:13px}
.conf-card .hd .meta{font-size:11px;color:var(--muted)}
.conf-diff{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:10px 0;font-size:13px}
.conf-diff > div{padding:8px 10px;border-radius:4px;font-variant-numeric:tabular-nums}
.conf-diff .prog{background:#eff6ff;border:1px solid #bfdbfe}
.conf-diff .mast{background:#fef3c7;border:1px solid #fde68a}
.conf-diff .lbl{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;margin-bottom:3px;font-weight:500}
.conf-diff .val{font-size:14px;font-weight:600;color:var(--text);font-family:var(--mono)}
.conf-diff .val.empty{color:var(--muted-2);font-style:italic;font-weight:400}
.conf-actions{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}
.conf-actions button{font-size:12px;padding:5px 10px}
.conf-card .ctx{font-size:12px;color:var(--muted);margin-top:6px;padding-top:8px;border-top:1px dashed var(--border)}
.imp-history{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:14px;margin-bottom:18px}
.imp-card{padding:12px 14px;background:var(--surface);border:1px solid var(--border);border-radius:6px}
.imp-card .name{font-size:12px;font-weight:600;color:var(--text);margin-bottom:4px;word-break:break-all}
.imp-card .date{font-size:11px;color:var(--muted);font-variant-numeric:tabular-nums;margin-bottom:8px}
.imp-card .nums{display:flex;gap:14px;font-size:12px}
.imp-card .nums .n{font-weight:600;font-size:14px;color:var(--text);display:block}
.imp-card .nums small{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
.drop-zone{border:2px dashed var(--border-strong);border-radius:8px;padding:32px;text-align:center;background:var(--surface-2);transition:all .15s;cursor:pointer}
.drop-zone:hover,.drop-zone.dragging{border-color:var(--accent-2);background:#eff6ff}
.drop-zone strong{display:block;font-size:14px;margin-bottom:4px}
.drop-zone small{color:var(--muted)}
.imp-progress{margin:16px 0;padding:14px;background:var(--surface-2);border:1px solid var(--border);border-radius:6px;font-family:var(--mono);font-size:12px}
.imp-progress .step{margin:2px 0;color:var(--muted)}
.imp-progress .step.done{color:var(--op)}
.imp-progress .step.error{color:var(--noop)}

/* State indicator en header */
.state-indicator{font-size:11px;color:var(--muted);font-variant-numeric:tabular-nums;cursor:help;padding:3px 7px;border-radius:99px;background:var(--soft);border:1px solid var(--border)}
.state-indicator.fresh{color:var(--st);border-color:#ecd4a3;background:#fdf6e8}
.state-indicator.unsaved{color:var(--noop);border-color:#f0c5c1;background:#fdf3f2}

/* Welcome banner */
.welcome-banner{background:#fef9c3;border:1px solid #fde68a;border-radius:6px;padding:18px 20px;margin-bottom:24px;display:flex;gap:18px;align-items:start}
.welcome-banner .icon{font-size:28px;line-height:1;flex-shrink:0}
.welcome-banner .content{flex:1}
.welcome-banner h3{margin:0 0 6px;font-size:14px;color:#854d0e;text-transform:none;letter-spacing:0;font-weight:600}
.welcome-banner p{margin:0 0 12px;font-size:13px;color:#854d0e;line-height:1.5}
.welcome-banner .mini-drop{border:1.5px dashed #d4a72c;background:#fffbeb;padding:14px;border-radius:6px;cursor:pointer;text-align:center;transition:all .15s}
.welcome-banner .mini-drop:hover{background:#fef3c7;border-color:#a16207}
.welcome-banner .mini-drop strong{display:block;color:#854d0e;font-size:13px;margin-bottom:2px}
.welcome-banner .mini-drop small{color:#a16207;font-size:11px}
.welcome-banner .dismiss{background:transparent;border:none;color:#a16207;font-size:11px;padding:0;cursor:pointer;text-decoration:underline}
.welcome-banner .dismiss:hover{color:#854d0e}

/* Backup pendiente */
.toast.warn-backup{background:var(--st);color:#fff}

/* Indicador "N eventos hoy" en ficha de equipo */
.today-chip{display:inline-flex;align-items:center;padding:3px 10px;border-radius:99px;background:#dcfce7;color:#166534;font-size:12px;font-weight:500;cursor:pointer;border:1px solid #bbf7d0;transition:background .1s}
.today-chip:hover{background:#bbf7d0}

@media (max-width:900px){
  main{padding:18px 16px 60px}
  .grid-2,.grid-3{grid-template-columns:1fr}
  .kv{grid-template-columns:1fr}
  .kv dt{font-weight:600;color:var(--text)}
  header.top{padding:0 14px;gap:12px}
  header.top nav{overflow:auto}
  header.top h1 small{display:none}
  .kpis{grid-template-columns:repeat(2,1fr)}
  .kpi{border-right:1px solid var(--border);border-bottom:1px solid var(--border)}
  .kpi:nth-child(2n){border-right:none}
  .view h2{font-size:18px}
}
/* ===== Capa de estilo moderno (v0.30) — sobre la base, sin alterar la estructura ===== */
:root{ --r:12px; --r-sm:9px; --r-lg:18px;
  --shadow-sm:0 1px 2px rgba(18,22,31,.05);
  --shadow:0 4px 16px rgba(18,22,31,.07);
  --shadow-lg:0 18px 48px rgba(18,22,31,.16); }
[data-theme="dark"]{
  --shadow-sm:0 1px 2px rgba(0,0,0,.4);
  --shadow:0 4px 16px rgba(0,0,0,.45);
  --shadow-lg:0 18px 48px rgba(0,0,0,.6); }
button{border-radius:var(--r-sm);padding:8px 14px;font-weight:600}
button.primary{box-shadow:0 2px 8px rgba(13,122,107,.26)}
button.primary:hover{filter:brightness(1.06)}
button.small{border-radius:8px;padding:6px 11px;font-weight:600}
button.ghost{box-shadow:none}
input,select,textarea{border-radius:var(--r-sm)}
header.top nav button{border-bottom:none;border-radius:9px;height:36px;padding:0 14px;font-weight:600}
header.top nav button:hover{background:var(--surface-2)}
header.top nav button.active{background:var(--accent-soft);color:var(--accent);border-bottom:none}
header.top .tools button{border-radius:9px}
.kpis{border-radius:var(--r);box-shadow:var(--shadow-sm)}
table.data{border-radius:var(--r);box-shadow:var(--shadow-sm)}
.badge{padding:2px 10px;font-weight:600}
.empty,.eq-info-card,.ciclo-card,.imp-card,.imp-progress,.notice,.drop-zone{border-radius:var(--r)}
.notice{padding:12px 15px}
.modal{border-radius:var(--r-lg);box-shadow:var(--shadow-lg)}
.modal-backdrop{background:rgba(15,18,22,.5);backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px)}
/* Pantalla "Por resolver" */
.pr-hero{margin-bottom:24px}
.pr-hero h2{font-size:28px;font-weight:750;letter-spacing:-.03em;margin:0 0 4px}
.pr-section{margin-bottom:24px}
.pr-section-hd{display:flex;align-items:center;gap:10px;margin:0 2px 12px}
.pr-section-hd h3{margin:0;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.04em}
.pr-section-hd .count{font-size:12px;font-weight:700;color:var(--muted);background:var(--surface-2);border:1px solid var(--border);border-radius:99px;padding:2px 9px}
.pr-card{display:flex;align-items:center;gap:15px;background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:15px 18px;margin-bottom:10px;box-shadow:var(--shadow-sm);position:relative;overflow:hidden;transition:box-shadow .15s,transform .15s,border-color .15s}
.pr-card:hover{box-shadow:var(--shadow);transform:translateY(-1px);border-color:var(--border-strong)}
.pr-card::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--border-strong)}
.pr-card.red::before{background:var(--noop)} .pr-card.amber::before{background:var(--st)} .pr-card.teal::before{background:var(--accent)} .pr-card.gray::before{background:var(--muted-2)}
.pr-card .pr-body{flex:1;min-width:0}
.pr-card .pr-title{font-weight:650;font-size:14.5px;letter-spacing:-.01em}
.pr-card .pr-sub{font-size:12.5px;color:var(--muted);margin-top:3px;overflow:hidden;text-overflow:ellipsis}
.pr-card .pr-acts{display:flex;gap:8px;flex:none}
.pr-allclear{text-align:center;padding:54px 20px;color:var(--muted);background:var(--surface);border:1px solid var(--border);border-radius:var(--r)}
/* Menú "Más" (navegación secundaria) */
header.top nav .nav-more{position:relative;height:100%;display:flex;align-items:center}
header.top nav .nav-more-menu{display:none;position:absolute;top:calc(100% - 7px);left:0;background:var(--surface);border:1px solid var(--border);border-radius:12px;box-shadow:var(--shadow-lg);padding:6px;min-width:200px;z-index:60}
header.top nav .nav-more.open .nav-more-menu{display:block}
header.top nav .nav-more-menu button{display:block;width:100%;text-align:left;background:transparent;border:none;border-radius:8px;padding:9px 12px;height:auto;color:var(--text-2);font-weight:600}
header.top nav .nav-more-menu button:hover{background:var(--surface-2);color:var(--text)}
header.top nav .nav-more-menu button.active{background:var(--accent-soft);color:var(--accent)}
</style>
</head>
<body>
<div class="app">
  <aside class="sidebar">
    <div class="s-logo">HHHA <small>Equipos Críticos · v__APP_VERSION__</small></div>
    <nav id="nav"></nav>
    <div class="s-foot"><span class="user-tag">👤 Cristian</span></div>
  </aside>
  <div class="content">
    <header class="topbar">
      <button id="btn-sidebar" class="sb-toggle" title="Plegar / expandir el menú lateral">☰</button>
      <div style="flex:1"></div>
      <span id="state-indicator" class="state-indicator" title="">—</span>
      <button id="btn-theme" title="Cambiar tema claro/oscuro" class="theme-btn">🌞</button>
      <button id="btn-excel" title="Exportar a Excel (.xlsx)">📊 Excel</button>
      <button id="btn-export" title="Exportar backup JSON">💾 Backup</button>
      <button id="btn-import" title="Importar backup JSON">📥 Importar</button>
      <button id="btn-reset" title="Resetear a seed inicial">↻ Reset</button>
    </header>
    <main id="main"></main>
  </div>
</div>

<div id="modal-root"></div>
<div id="toast-root"></div>

<!-- SESSION RECORDER -->
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

<script>
//==============================================================
// SEED DATA (extraído de los archivos del usuario)
//==============================================================
const SEED = __SEED_PLACEHOLDER__;

//==============================================================
// CONSTANTES & CATÁLOGOS
//==============================================================
const APP_VERSION = '0.49';
const STORAGE_KEY = 'hhha_v1_data';
const MESES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
const MES_NUM = {Ene:0,Feb:1,Mar:2,Abr:3,May:4,Jun:5,Jul:6,Ago:7,Sep:8,Oct:9,Nov:10,Dic:11};
const NUM_MES = MESES;

const EJECUTORES = [
  'Carlos Bahamondes Seguel','Cristián Beltrán Oviedo','Cristina Rozas Urrutia',
  'Daniel Díaz Neira','Ignacio Berner Bergara','Macarena Toledo','Marco Ulloa',
  'Matías Soazo Garrido','Ricardo Matus Aroca','Tito Millapán Riquelme','Personal externo'
];

const TIPOS_EVENTO = [
  {k:'solicitud',     label:'Solicitud de trabajo',     desc:'Abre ciclo correctivo'},
  {k:'visita',        label:'Visita técnica',           desc:'Diagnóstica o correctiva'},
  {k:'oc',            label:'Orden de Compra',          desc:'Gestión dentro del ciclo'},
  {k:'envio',         label:'Envío a servicio técnico', desc:'Equipo sale del hospital'},
  {k:'recepcion',     label:'Recepción',                desc:'Equipo retorna'},
  {k:'reparacion',    label:'Reparación',               desc:'Cierre típico del ciclo'},
  {k:'mp',            label:'Mantención preventiva',    desc:'Programada / ejecutada'}
];

const CAUSALES = {
  C1:{desc:'Imposibilidad de desocupar el equipo del paciente',                       reprog30:true},
  C2:{desc:'Equipo en servicio técnico',                                              reprog30:false},
  C3:{desc:'Equipo no operativo, espera de repuestos/accesorios',                     reprog30:false},
  C4:{desc:'Equipo en préstamo a otro hospital',                                      reprog30:false},
  C5:{desc:'No disponibilidad de HH funcionario SEC (carga laboral)',                 reprog30:true},
  C6:{desc:'No disponibilidad de HH servicio técnico externo',                        reprog30:true},
  C7:{desc:'Ausencia funcionario SEC > 15 días',                                      reprog30:true},
  C8:{desc:'Contingencia hospitalaria',                                               reprog30:true}
};

const ESTADOS_PRIMARIOS = ['desconocido','operativo','no_operativo','en_servicio_tecnico','baja'];
const ESTADO_LABEL = {desconocido:'Desconocido',operativo:'Operativo',no_operativo:'No operativo',en_servicio_tecnico:'En servicio técnico',baja:'Baja'};

const SUBESTADOS_NOOP = ['esperando_visita_tecnica','esperando_cotizacion','esperando_OC','esperando_repuestos','en_reparacion_interna','otro'];
const SUBESTADOS_ST  = ['enviado','cotizacion_pendiente','OC_emitida','en_reparacion_externa','despachado_de_regreso'];

const DOCS_CORRECTIVO = ['Solicitud SIGEM con tarea cerrada','Cotización','Informe técnico trato directo','Orden de compra','Guía de despacho de repuestos','Informe visita diagnóstica','Informe visita correctiva','Hoja de envío','Informe técnico ST externo','Guía de despacho de retorno'];
const DOCS_PREVENTIVO = ['Protocolo / hoja de MP','Pauta de monitoreo diario (DEA)','Firma jefe equipo médico','Informe técnico de empresa externa'];

const TIPO_PENDIENTE = {documento_faltante:'Documento faltante',reprogramacion:'Reprogramación MP',recomendacion_tecnica:'Recomendación técnica',gestion_general:'Gestión general'};
// Estados de pendiente orientados a la acción: No iniciado -> En proceso -> Resuelto.
// 'cerrado' se conserva como estado final (= Resuelto) para no romper los conteos existentes (!== 'cerrado').
const ESTADO_PEND_LABEL = {no_iniciado:'No iniciado', en_proceso:'En proceso', cerrado:'Resuelto'};
function normalizarEstadoPend(e){
  if(e==='cerrado'||e==='resuelto') return 'cerrado';
  if(e==='en_proceso'||e==='en proceso') return 'en_proceso';
  return 'no_iniciado'; // 'creado', 'abierto', vacío -> no iniciado
}
function badgePend(estado){
  const cls = estado==='cerrado' ? 'op' : (estado==='en_proceso' ? 'st' : 'noop');
  return el('span',{class:'badge '+cls}, ESTADO_PEND_LABEL[estado]||estado);
}
function cambiarEstadoPend(p, nuevo){
  const antes = p.estado;
  p.estado = nuevo;
  if(nuevo==='cerrado' && !p.fechaCierre) p.fechaCierre = hoyLocal();
  audit('pendiente', p.id, 'estado', antes, nuevo);
  save();
  navigate(currentView, viewParams);
}

//==============================================================
// STATE & PERSISTENCIA
//==============================================================
let state = null;

function load(){
  try{
    const raw = localStorage.getItem(STORAGE_KEY);
    if(!raw) return null;
    let json;
    if(raw.startsWith('LZv1:') && typeof LZString !== 'undefined'){
      json = LZString.decompressFromUTF16(raw.slice(5));
      if(!json) throw new Error('Decompresión falló');
    } else {
      json = raw;
    }
    const d = JSON.parse(json);
    if(d.__v !== APP_VERSION) return migrate(d);
    return d;
  }catch(e){console.error('load',e);return null}
}
function migrate(d){
  // Migración no destructiva. Asegura estructuras nuevas sin perder datos.
  if(!d.conflictos) d.conflictos = [];
  if(!d.importaciones) d.importaciones = [];
  if(!d.prefs) d.prefs = {};
  d.counters = d.counters || {};
  if(d.counters.conflicto == null) d.counters.conflicto = (d.conflictos.length||0) + 1;
  if(d.counters.importacion == null) d.counters.importacion = (d.importaciones.length||0) + 1;
  // Normalizar estados de pendientes de versiones previas (creado/abierto -> no_iniciado).
  (d.pendientes||[]).forEach(p => { p.estado = normalizarEstadoPend(p.estado); });
  d.__v = APP_VERSION;
  return d;
}

// Campos de texto del equipo que el Excel a veces trae como número (ej. modelo "840",
// ubicación "501"). Las planillas que ordenan/filtran por texto (Equipos, Registro MP)
// se caen con localeCompare sobre un número, dejando la lista vacía. Esto los uniforma.
const CAMPOS_TEXTO_EQUIPO = ['fam','equipo','servicio','unidad','ubic','proc','marca','modelo','serie','clasif','freq'];
function normalizarEquipos(){
  (state.equipos||[]).forEach(e => {
    CAMPOS_TEXTO_EQUIPO.forEach(k => {
      if(e[k] != null && typeof e[k] !== 'string') e[k] = String(e[k]);
    });
  });
}

// Limpia efectos huérfanos de eventos anulados que quedaron de versiones previas.
// Idempotente: correr varias veces no rompe nada.
function limpiarEfectosAnulados(){
  let cambios = 0;
  // Para cada equipo, revisar cada mes del registro
  state.equipos.forEach(eq => {
    if(!eq.registro) return;
    Object.keys(eq.registro).forEach(mes => {
      const r = (eq.registro[mes] || {}).R;
      if(!r) return;
      // ¿Hay un evento MP no anulado en este equipo/mes que justifique el R?
      const mIdx = MES_NUM[mes];
      const hayValido = state.eventos.some(ev =>
        ev.inv === eq.inv && !ev.anulado && ev.tipo === 'Mantención preventiva' &&
        ev.resultado && ev.fecha && new Date(ev.fecha+'T00:00:00').getMonth() === mIdx
      );
      if(!hayValido){
        // Limpia el R huérfano
        delete eq.registro[mes].R;
        if(Object.keys(eq.registro[mes]).length === 0) delete eq.registro[mes];
        cambios++;
      }
    });
  });
  // Recalcular estado de cada equipo (recalcEstadoEquipo ya devuelve 'desconocido'
  // si no hay eventos con estado declarado — realinea state pre-v0.8 que usaba 'operativo')
  state.equipos.forEach(eq => {
    const antes = eq.estado;
    recalcEstadoEquipo(eq);
    if(antes !== eq.estado) cambios++;
  });
  // Revisar ciclos: si todos sus eventos están anulados, marcar ciclo como anulado
  state.ciclos.forEach(c => {
    if(c.estado === 'anulado') return;
    const eventosVivos = state.eventos.filter(e => !e.anulado && e.folio === c.folio);
    if(eventosVivos.length === 0){
      c.estado = 'anulado';
      c.anulado = true;
      cambios++;
    }
  });
  // Anular pendientes auto con eventoOrigen anulado
  state.pendientes.forEach(p => {
    if(p.anulado || !p.eventoOrigen) return;
    const ev = state.eventos.find(e => e.id === p.eventoOrigen);
    if(ev && ev.anulado && p.estado !== 'cerrado'){
      p.anulado = true;
      p.motivoAnulacion = 'Evento MP origen anulado (limpieza automática)';
      cambios++;
    }
  });
  return cambios;
}
function persistirState(){
  // Devuelve {ok, bytes, error}.
  try{
    const json = JSON.stringify(state);
    const payload = (typeof LZString !== 'undefined')
      ? ('LZv1:' + LZString.compressToUTF16(json))
      : json;
    localStorage.setItem(STORAGE_KEY, payload);
    return {ok:true, bytes: payload.length * 2}; // UTF-16
  } catch(e){
    return {ok:false, error:e};
  }
}

function save(opts){
  state.__updated = new Date().toISOString();
  const isInternal = opts && opts.internal;
  if(!isInternal){
    state.__userActions = (state.__userActions || 0) + 1;
  }
  let res = persistirState();
  if(!res.ok){
    // Intento 1: limpiar conflictos resueltos antiguos
    const resCount = state.conflictos.filter(c => (c.estado||'').startsWith('resuelto')).length;
    if(resCount > 0){
      state.conflictos = state.conflictos.filter(c => !(c.estado||'').startsWith('resuelto'));
      res = persistirState();
      if(res.ok){
        toast(`Almacenamiento liberado: ${resCount} conflictos resueltos podados del historial. Tu backup JSON los conserva.`, 'warn-backup',
          {label:'Descargar backup', fn: exportData});
      }
    }
  }
  if(!res.ok){
    // Intento 2: forzar exportar y avisar
    toast('Almacenamiento del navegador lleno. Descarga el backup AHORA antes de seguir.', 'error',
      {label:'Descargar', fn: exportData});
    return;
  }
  // Auto-backup recordatorio cada N cambios reales del usuario
  if(!isInternal && state.__userActions > 0 && state.__userActions % 10 === 0){
    toast(`Llevas ${state.__userActions} cambios. Recuerda descargar backup.`, 'warn-backup',
      {label:'Descargar', fn: exportData});
  }
  // Si el banner welcome estaba visible y ya no aplica, quitarlo
  if(!stateEsFresh()){
    document.querySelectorAll('.welcome-banner').forEach(b => b.remove());
  }
  refreshStateIndicator();
}

// True si el state no tiene datos del usuario sobre el seed.
function stateEsFresh(){
  return state.eventos.length <= SEED.eventos.length &&
         state.pendientes.length <= SEED.pendientes.length &&
         (state.conflictos||[]).length === 0 &&
         Object.keys(state.asignacionesMP||{}).length === 0;
}

function refreshStateIndicator(){
  const ind = document.getElementById('state-indicator');
  if(!ind) return;
  const cnt = (state.__userActions || 0);
  const upd = state.__updated ? new Date(state.__updated) : null;
  const fresh = stateEsFresh();
  const txt = fresh ? 'Sin cambios' : `${cnt} cambio${cnt!==1?'s':''}`;
  const tip = fresh
    ? 'No hay actividad del usuario. Si tenías datos antes, importa el backup JSON.'
    : `${cnt} cambios desde el último arranque. Última actualización: ${upd ? upd.toLocaleString('es-CL') : '—'}. ` +
      'Recuerda descargar backup periódicamente (Backup en este header). ' +
      'IMPORTANTE: Chrome guarda los datos por ruta del archivo — si mueves app.html a otra carpeta, empieza vacío.';
  ind.textContent = txt;
  ind.title = tip;
  ind.classList.toggle('fresh', fresh);
}
function init(){
  // Construye state inicial desde SEED
  const equipos = SEED.equipos.map(e => ({
    ...e,
    estado: 'desconocido',
    subestado: null,
    estadoDesde: null,
    notas: null
  }));
  const eventos = SEED.eventos.map(e => ({
    ...e,
    anulado:false,
    creadoPor:'Cristian',
    actualizadoPor:'Cristian',
    ts: e.fechaReg ? new Date(e.fechaReg).toISOString() : new Date().toISOString()
  }));
  const ciclos = []; // se reconstruyen
  const pendientes = SEED.pendientes.map(p => {
    // Si el seed ya trae 'tipo' (datos importados con su clasificación real),
    // se respeta; si no (seed original sin tipo), se deriva del texto.
    let tipo = p.tipo;
    if(!tipo){
      tipo = 'gestion_general';
      if((p.desc||'').toLowerCase().includes('pauta de monitoreo')||(p.desc||'').toLowerCase().includes('firma')) tipo='documento_faltante';
      if((p.desc||'').toLowerCase().includes('reprogram')) tipo='reprogramacion';
    }
    return {...p, tipo, estado: normalizarEstadoPend(p.estado), origen: p.origen || 'manual', seguimientos:[], anulado:false};
  });
  const tareas = SEED.tareas.slice();
  // expand inline tareas from pendientes (string "[ ] ...")
  pendientes.forEach(p => {
    if(typeof p.tareas === 'string'){
      const ts = p.tareas.split('\n').filter(x=>x.trim()).map((x,i)=>({
        id: 1000+tareas.length+i, pendId:p.id, inv:p.inv, equipo:p.equipo,
        desc: x.replace(/^\[\s*\]\s*/,'').trim(), estado:'abierto'
      }));
      tareas.push(...ts);
      p.tareas = ts.map(t=>t.id);
    } else { p.tareas = []; }
  });
  return {
    __v: APP_VERSION,
    __created: new Date().toISOString(),
    __updated: new Date().toISOString(),
    equipos, eventos, ciclos, pendientes, tareas,
    counters: {evento: eventos.length+1, pend: pendientes.length+1, tarea: tareas.length+1, ciclo: 1, audit:1, conflicto:1, importacion:1},
    audit: [],
    asignacionesMP: {},
    correos: [],
    conflictos: [],
    importaciones: [],
    prefs: {}
  };
}
function resetState(){
  if(!confirm('¿Resetear todo a datos iniciales? Se perderán los cambios.')) return;
  localStorage.removeItem(STORAGE_KEY);
  state = init();
  save();
  navigate('porResolver');
  toast('Datos reseteados','success');
}

//==============================================================
// AUDIT
//==============================================================
function audit(entidad, idEnt, campo, vOld, vNew){
  state.audit.push({
    id: state.counters.audit++,
    entidad, idEnt, campo,
    valorAnterior: vOld, valorNuevo: vNew,
    usuario:'Cristian', ts:new Date().toISOString()
  });
}

//==============================================================
// LÓGICA DE DOMINIO
//==============================================================
function findEquipo(inv){ return state.equipos.find(e => e.inv === inv); }
function eventosDe(inv){ return state.eventos.filter(e => e.inv === inv && !e.anulado).sort((a,b)=> (a.fecha||'').localeCompare(b.fecha||'')); }
function eventosDeTodos(inv){ return state.eventos.filter(e => e.inv === inv).sort((a,b)=> (a.fecha||'').localeCompare(b.fecha||'')); }
function pendientesDe(inv){ return state.pendientes.filter(p => p.inv === inv && !p.anulado); }
function conflictosDe(inv){ return (state.conflictos||[]).filter(c => c.inv === inv && (c.estado === 'pendiente' || c.estado === 'pospuesto')); }
function ciclosDe(inv){ return state.ciclos.filter(c => c.inv === inv); }
function ciclosAbiertosDe(inv){ return state.ciclos.filter(c => c.inv === inv && c.estado === 'abierto'); }
// Encargado actual del equipo: ingeniero del ciclo abierto o, si no, el último ejecutor.
function encargadoDe(equipo){
  const c = ciclosAbiertosDe(equipo.inv)[0];
  if(c && c.ingenieroAsignado) return c.ingenieroAsignado;
  const evs = eventosDe(equipo.inv);
  for(let i = evs.length-1; i >= 0; i--){ if(evs[i].ejecutor) return evs[i].ejecutor; }
  return null;
}

// Mapeo de causal de MP de la carta gantt -> estado operativo del equipo.
// C2 = en servicio técnico, C3 = no operativo (espera repuestos), FS/NU = no operativo, Baja = baja.
// C1, C4-C8 y 'Si' NO indican falla del equipo -> se asume operativo.
const MP_CAUSAL_ESTADO = {C2:'en_servicio_tecnico', C3:'no_operativo', FS:'no_operativo', NU:'no_operativo', Baja:'baja'};
// Estado resultante (texto del formulario) de una MP según su resultado/causal. Espeja
// MP_CAUSAL_ESTADO para que el evento guarde el estado correcto (C2 = en servicio técnico, no
// "operativo"). C1 y C4–C8 son reprogramaciones sin falla: el equipo queda operativo.
function estadoMPDesdeResultado(resultado){
  if(resultado === 'Si') return 'operativo';
  if(resultado === 'C2') return 'en servicio técnico';
  if(resultado === 'C3' || resultado === 'FS' || resultado === 'NU') return 'no operativo';
  if(resultado === 'Baja') return 'baja';
  return ''; // C1, C4–C8 (reprogramación sin falla) y otros: no declaran estado
}
// Cuando no hay eventos que declaren estado, infiere desde la carta gantt usando el
// resultado del último mes registrado del año vigente. Devuelve {estado,fecha} o null.
function estadoDesdeMatriz(equipo){
  let ultR = null, ultMesIdx = -1;
  MESES.forEach((m, idx) => { const r = ((equipo.registro||{})[m]||{}).R; if(r){ ultR = r; ultMesIdx = idx; } });
  const est = MP_CAUSAL_ESTADO[ultR];
  if(est) return {estado: est, fecha: `${new Date().getFullYear()}-${String(ultMesIdx+1).padStart(2,'0')}-15`};
  return null;
}
function recalcEstadoEquipo(equipo){
  // Deriva estado actual del último evento que declaró estado.
  // Si no hay eventos no anulados con estado, devuelve 'desconocido'.
  const evs = eventosDe(equipo.inv);
  // Eventos MP con resultado 'Baja' tienen prioridad
  for(let i=evs.length-1; i>=0; i--){
    const ev = evs[i];
    if(ev.tipo === 'Mantención preventiva' && ev.resultado === 'Baja'){
      equipo.estado = 'baja';
      equipo.estadoDesde = ev.fecha;
      return;
    }
  }
  // Último evento con estado declarado
  for(let i=evs.length-1; i>=0; i--){
    const ev = evs[i];
    // Para una MP, el estado lo manda el RESULTADO/causal (misma matriz que la carta gantt),
    // NO el campo ev.estado (que en los eventos automáticos del maestro venía como "operativo"
    // y tapaba el "en servicio técnico" de un C2). C2→serv. técnico, C3/FS/NU→no operativo,
    // Baja→baja, Si→operativo. C1 y C4–C8 son reprogramaciones SIN falla: no declaran estado
    // (se sigue buscando hacia atrás / la carta gantt).
    if(ev.tipo === 'Mantención preventiva' && ev.resultado){
      if(ev.resultado === 'Si'){ equipo.estado='operativo'; equipo.estadoDesde=ev.fecha; return; }
      const estMP = MP_CAUSAL_ESTADO[ev.resultado];
      if(estMP){ equipo.estado=estMP; equipo.estadoDesde=ev.fecha; return; }
      continue; // C1, C4–C8: reprogramación sin falla declarada
    }
    if(ev.estado){
      const estado = ev.estado === 'operativo' ? 'operativo' :
                     ev.estado === 'en servicio técnico' ? 'en_servicio_tecnico' :
                     ev.estado === 'baja' ? 'baja' :
                     'no_operativo';
      equipo.estado = estado;
      equipo.estadoDesde = ev.fecha;
      return;
    }
  }
  // Sin eventos que declaren estado: inferir de la carta gantt (causal de MP del último
  // mes registrado). Si la gantt tampoco indica falla, se asume operativo (el equipo
  // funciona mientras no haya señal de problema). Antes quedaba 'desconocido'.
  const m = estadoDesdeMatriz(equipo);
  if(m){ equipo.estado = m.estado; equipo.estadoDesde = m.fecha; return; }
  equipo.estado = 'operativo';
  equipo.estadoDesde = null;
}

function diasEnEstado(equipo){
  if(!equipo.estadoDesde) return 0;
  return Math.max(0, diasEntreFechas(equipo.estadoDesde, hoyLocal()));
}

// Resultado de la MP del mes considerando AMBAS fuentes: el evento MP del mes (su
// resultado) y la matriz registro[mes].R de la carta gantt (para el año vigente).
// Devuelve el código ('Si','C1'..'C8','FS','NU','Baja','No') o null si no hay nada.
function resultadoMPMes(equipo, year, month){
  const ev = state.eventos.find(e => e.inv === equipo.inv && e.tipo === 'Mantención preventiva' && !e.anulado &&
    e.fecha && new Date(e.fecha + 'T00:00:00').getFullYear() === year && new Date(e.fecha + 'T00:00:00').getMonth() === month);
  if(ev) return ev.resultado || 'Si';
  if(year === new Date().getFullYear()){
    const r = ((equipo.registro||{})[NUM_MES[month]]||{}).R;
    if(r) return r;
  }
  return null;
}
// Estado de la MP del mes: ejecutada (Si) / reprogramada (C1-C8) / otro (FS,NU,Baja,No) / pendiente (nada).
function mpEstadoMes(equipo, year, month){
  const r = resultadoMPMes(equipo, year, month);
  if(r === 'Si') return 'ejecutada';
  if(/^C[1-8]$/.test(r||'')) return 'reprogramada';
  if(r) return 'otro';
  return 'pendiente';
}
function mpDelMesEjecutada(equipo, year, month){
  // "Ejecutada" = MP realizada (resultado Si), ya sea por evento o por la carta gantt.
  return mpEstadoMes(equipo, year, month) === 'ejecutada';
}

function mpProgramadaEnMes(equipo, mes){
  const p = (equipo.prog||{})[mes];
  return p && ['X','R','RA','PM'].includes(p);
}

function abrirCiclo(folio, inv, fecha, ingeniero, descripcion){
  if(!folio) folio = 'SIGEM-AUTO-' + String(state.counters.ciclo).padStart(4,'0');
  const yaAbierto = ciclosAbiertosDe(inv);
  if(yaAbierto.length > 0){
    if(!confirm(`El equipo ${inv} ya tiene un ciclo abierto (${yaAbierto[0].folio}). ¿Abrir otro de todos modos?`)) return null;
  }
  const ciclo = {
    folio, inv,
    fechaApertura: fecha,
    fechaCierre: null,
    estado:'abierto',
    descripcionInicial: descripcion || '',
    ingenieroAsignado: ingeniero || null,
    id: state.counters.ciclo++
  };
  state.ciclos.push(ciclo);
  audit('ciclo', ciclo.folio, 'estado', null, 'abierto');
  return ciclo;
}
function cerrarCiclo(folio, fecha, motivo){
  const c = state.ciclos.find(x => x.folio === folio);
  if(!c) return;
  c.estado = 'cerrado';
  c.fechaCierre = fecha || hoyLocal();
  if(motivo) c.motivoCierre = motivo;
  audit('ciclo', folio, 'estado', 'abierto', 'cerrado');
}

function crearPendienteAuto(inv, tipo, desc, ejecutor, eventoOrigenId, fechaCompromiso){
  const equipo = findEquipo(inv);
  const p = {
    id: state.counters.pend++,
    inv, equipo: equipo ? equipo.equipo : '', servicio: equipo ? equipo.servicio : '',
    tipo, desc, ejecutor: ejecutor || null,
    fechaCrea: hoyLocal(),
    fechaComp: fechaCompromiso || null,
    proxRecord: fechaCompromiso || null,
    fechaCierre: null,
    estado:'no_iniciado',
    origen:'auto_mp_causal',
    seguimientos:[],
    tareas:[],
    eventoOrigen: eventoOrigenId || null,
    anulado:false
  };
  state.pendientes.push(p);
  audit('pendiente', p.id, 'creado_auto', null, tipo);
  return p;
}

function aplicarEfectosEvento(ev){
  // Reglas según tipo
  const eq = findEquipo(ev.inv);
  if(!eq) return;
  const tipo = ev.tipo;
  // Estado
  if(ev.estado){
    const nuevo = ev.estado === 'operativo' ? 'operativo' :
                  ev.estado === 'en servicio técnico' ? 'en_servicio_tecnico' :
                  'no_operativo';
    if(eq.estado !== nuevo){
      audit('equipo', eq.inv, 'estado', eq.estado, nuevo);
      eq.estado = nuevo;
      eq.estadoDesde = ev.fecha;
    }
    if(ev.subestado){ eq.subestado = ev.subestado; }
  }
  // Ciclo
  if(tipo === 'Solicitud de trabajo'){
    abrirCiclo(ev.folio, ev.inv, ev.fecha, ev.ejecutor, ev.obs);
  }
  if(tipo === 'Reparación' && ev.estado === 'operativo' && ev.folio){
    const c = state.ciclos.find(x => x.folio === ev.folio && x.estado === 'abierto');
    if(c) cerrarCiclo(ev.folio, ev.fecha);
  }
  // Recepción operativa = el equipo retornó funcionando → cierra el ciclo (flujo de reparación externa).
  if(tipo === 'Recepción' && ev.estado === 'operativo' && ev.folio){
    const c = state.ciclos.find(x => x.folio === ev.folio && x.estado === 'abierto');
    if(c) cerrarCiclo(ev.folio, ev.fecha);
  }
  if(tipo === 'Visita técnica' && ev.tipoVisita === 'correctiva' && ev.estado === 'operativo' && ev.folio){
    const c = state.ciclos.find(x => x.folio === ev.folio && x.estado === 'abierto');
    if(c) cerrarCiclo(ev.folio, ev.fecha);
  }
  // MP
  if(tipo === 'Mantención preventiva'){
    const r = ev.resultado;
    const mesIdx = new Date(ev.fecha + 'T00:00:00').getMonth();
    const mes = NUM_MES[mesIdx];
    eq.registro = eq.registro || {};
    eq.registro[mes] = eq.registro[mes] || {};
    eq.registro[mes].R = r;
    // Si causal C1-C8 → pendiente reprogramación
    if(r && /^C[1-8]$/.test(r)){
      const c = CAUSALES[r];
      const fechaComp = c.reprog30 ? addDias(hoyLocal(),30) : null;
      crearPendienteAuto(ev.inv, 'reprogramacion',
        `Reprogramar MP por causal ${r} — ${c.desc}. ${c.reprog30?'Reprogramar dentro de 30 días.':'Esperar reintegro del equipo.'}`,
        ev.ejecutor, ev.id, fechaComp);
      // Una causal reprograma la MP: marca "R" (reprogramado) en la programación del MES
      // SIGUIENTE para que se vea de inmediato en la carta gantt. No pisa una programación
      // ya existente de ese mes (solo escribe si está vacía).
      if(mesIdx < 11){
        const mesSig = NUM_MES[mesIdx+1];
        eq.registro[mesSig] = eq.registro[mesSig] || {};
        if(!eq.registro[mesSig].P) eq.registro[mesSig].P = 'R';
      }
    }
    if(r === 'NU'){
      crearPendienteAuto(ev.inv,'gestion_general','Localizar equipo (resultado MP = NU)',ev.ejecutor,ev.id,null);
    }
    if(r === 'Baja'){
      eq.estado = 'baja';
      eq.estadoDesde = ev.fecha;
      audit('equipo',eq.inv,'estado','operativo','baja');
    }
  }
}

//==============================================================
// UTIL
//==============================================================
function $(sel,el=document){return el.querySelector(sel)}
function $$(sel,el=document){return Array.from(el.querySelectorAll(sel))}
function el(tag, attrs={}, ...children){
  const n = document.createElement(tag);
  for(const k in attrs){
    if(k === 'class') n.className = attrs[k];
    else if(k === 'style' && typeof attrs[k] === 'object') Object.assign(n.style,attrs[k]);
    else if(k.startsWith('on')) n.addEventListener(k.slice(2).toLowerCase(),attrs[k]);
    else if(k === 'html') n.innerHTML = attrs[k];
    else if(attrs[k] !== false && attrs[k] != null) n.setAttribute(k,attrs[k]);
  }
  for(const c of children){
    if(c == null || c === false) continue;
    if(Array.isArray(c)) c.forEach(x => x!=null && n.appendChild(x.nodeType?x:document.createTextNode(x)));
    else n.appendChild(c.nodeType ? c : document.createTextNode(c));
  }
  return n;
}
function fmt(v){ return v==null||v==='' ? '—' : v; }
// Sección contraíble para la ficha del equipo (se pliega/despliega; cap. 4 de la especificación).
function seccionColapsable(titulo, contenido, abierto){
  return el('details',{class:'ficha-sec', open: abierto!==false},
    el('summary',{}, titulo),
    el('div',{class:'ficha-sec-body'}, contenido)
  );
}
// FIX zona horaria: si el string es YYYY-MM-DD lo tratamos como fecha LOCAL,
// no UTC, así no aparece corrida un día (Chile UTC-3/-4).
function fmtFecha(v){
  if(!v) return '—';
  if(typeof v === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(v)){
    const [y,m,d] = v.split('-').map(Number);
    return String(d).padStart(2,'0')+'-'+String(m).padStart(2,'0')+'-'+y;
  }
  const d = new Date(v);
  if(isNaN(d)) return v;
  return d.toLocaleDateString('es-CL');
}
function hoyLocal(){
  const d = new Date();
  return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
}
function addDias(fechaLocal, n){
  if(!fechaLocal) fechaLocal = hoyLocal();
  const [y,m,d] = fechaLocal.split('-').map(Number);
  const dt = new Date(y, m-1, d + n);
  return dt.getFullYear()+'-'+String(dt.getMonth()+1).padStart(2,'0')+'-'+String(dt.getDate()).padStart(2,'0');
}
function diasEntreFechas(a, b){
  // Recibe dos YYYY-MM-DD locales y devuelve días enteros (b - a).
  if(!a) return 0;
  const [ay,am,ad] = a.split('-').map(Number);
  const dA = new Date(ay, am-1, ad);
  const dB = b ? (()=>{const [y,m,d]=b.split('-').map(Number); return new Date(y,m-1,d)})() : new Date();
  return Math.floor((dB - dA) / 86400000);
}
function getPref(k, def){ return (state.prefs && state.prefs[k]) || def; }
function setPref(k, v){ state.prefs = state.prefs || {}; state.prefs[k] = v; }

function setTheme(theme){
  document.documentElement.setAttribute('data-theme', theme);
  setPref('theme', theme);
  const btn = document.getElementById('btn-theme');
  if(btn){ btn.textContent = theme === 'dark' ? '🌙' : '🌞'; btn.title = `Cambiar a tema ${theme==='dark'?'claro':'oscuro'}`; }
  save({internal:true});
}
function toggleTheme(){
  const cur = document.documentElement.getAttribute('data-theme') || 'light';
  setTheme(cur === 'dark' ? 'light' : 'dark');
}
function toggleSidebar(){
  const app = document.querySelector('.app');
  const colapsada = app.classList.toggle('sb-collapsed');
  setPref('sidebarColapsada', colapsada);
  save({internal:true});
}
function toast(msg, type='', action){
  const t = el('div',{class:'toast '+type});
  t.appendChild(el('span',{}, msg));
  if(action){
    t.appendChild(el('button',{class:'toast-action', onclick:()=>{ action.fn(); t.remove(); }}, action.label));
  }
  $('#toast-root').appendChild(t);
  setTimeout(()=>t.remove(), 4000);
  // Captura para análisis: todo aviso es señal del RESULTADO de una acción.
  if(typeof recorder !== 'undefined' && recorder.status === 'recording'){
    recorder.event(type === 'error' ? 'form_error' : 'toast', {mensaje: String(msg).slice(0,180), kind: type||'info'});
  }
}
function badgeEstado(estado){
  const cls = {operativo:'op',no_operativo:'noop',en_servicio_tecnico:'st',baja:'baja',desconocido:'desconocido'}[estado] || '';
  return el('span',{class:'badge '+cls}, ESTADO_LABEL[estado] || estado || 'Desconocido');
}
function badgePendEstado(estado){
  return el('span',{class:'badge '+estado}, estado);
}

//==============================================================
// MODAL
//==============================================================
function modal({title, body, footer, wide=false, onClose, hasUnsavedData}){
  const root = $('#modal-root');
  root.innerHTML = '';
  function tryClose(reason){
    const had = hasUnsavedData && hasUnsavedData();
    if(reason === 'backdrop' && had){
      if(!confirm('Hay datos sin guardar en el formulario. ¿Cerrar y descartar?')) return;
    }
    if(had && typeof recorder !== 'undefined' && recorder.status === 'recording'){
      recorder.event('modal_abort', {titulo: title, reason});
    }
    close();
  }
  const bd = el('div',{class:'modal-backdrop',onclick:e=>{if(e.target===bd){tryClose('backdrop')}}});
  const m  = el('div',{class:'modal'+(wide?' wide':'')});
  const hd = el('header',{},
    el('h2',{},title),
    el('button',{class:'ghost',onclick:()=>tryClose('x'),title:'Cerrar'},'✕')
  );
  const body_ = el('div',{class:'body'});
  if(typeof body === 'string') body_.innerHTML = body;
  else if(body) body_.appendChild(body);
  const ft = el('footer',{});
  (footer||[]).forEach(b => ft.appendChild(b));
  m.appendChild(hd); m.appendChild(body_); if(footer && footer.length) m.appendChild(ft);
  bd.appendChild(m);
  root.appendChild(bd);
  // Esc también pide confirmación
  function onEsc(e){ if(e.key === 'Escape'){ tryClose('esc'); } }
  document.addEventListener('keydown', onEsc);
  function close(){ root.innerHTML=''; document.removeEventListener('keydown', onEsc); onClose && onClose(); }
  return {close};
}
function closeModal(){ $('#modal-root').innerHTML=''; }

//==============================================================
// ROUTER
//==============================================================
const VIEWS = {};
let currentView = 'dashboard';
let viewParams = {};
const navStack = []; // pila de {view, params} para "volver"

function navigate(view, params, opts){
  const replace = opts && opts.replace;
  if(!replace && currentView){
    // No empujar si vamos al mismo lugar
    const sameView = currentView === view && JSON.stringify(viewParams) === JSON.stringify(params||{});
    if(!sameView) navStack.push({view: currentView, params: {...viewParams}});
    // Limitar stack a 30
    if(navStack.length > 30) navStack.shift();
  }
  currentView = view; viewParams = params || {};
  $$('#nav button').forEach(b => b.classList.toggle('active', b.dataset.view === view));
  const main = $('#main');
  main.innerHTML = '';
  if(VIEWS[view]) VIEWS[view](main, viewParams);
  main.scrollTop = 0;
  recorder.event('nav',{view,params:viewParams});
}

function navBack(fallback){
  const prev = navStack.pop();
  if(prev){
    navigate(prev.view, prev.params, {replace:true});
  } else {
    navigate(fallback || 'equipos', {}, {replace:true});
  }
}

//==============================================================
// VIEWS
//==============================================================
VIEWS.dashboard = function(root){
  const today = new Date();
  const year = today.getFullYear(), month = today.getMonth();
  const mesActual = NUM_MES[month];
  state.equipos.forEach(recalcEstadoEquipo);

  const opCount = state.equipos.filter(e=>e.estado==='operativo').length;
  const noopCount = state.equipos.filter(e=>e.estado==='no_operativo').length;
  const stCount = state.equipos.filter(e=>e.estado==='en_servicio_tecnico').length;
  const bajaCount = state.equipos.filter(e=>e.estado==='baja').length;
  const alertaDias = state.equipos.filter(e => ['no_operativo','en_servicio_tecnico'].includes(e.estado) && diasEnEstado(e) > 30);
  const pendAbiertos = state.pendientes.filter(p => !p.anulado && p.estado !== 'cerrado');
  const ciclosAbiertos = state.ciclos.filter(c => c.estado === 'abierto');
  const eventosBorrador = state.eventos.filter(e => e.oficial !== 'Sí' && !e.anulado);

  // === KPI strip (clickeable) ===
  const kpis = el('div',{class:'kpis'},
    kpiCell('Total equipos', state.equipos.length, ()=>navigate('equipos',{})),
    kpiCell('Operativos', opCount, ()=>navigate('equipos',{estado:'operativo'}), ''),
    kpiCell('No operativos', noopCount, ()=>navigate('equipos',{estado:'no_operativo'}), noopCount>0?'alert':''),
    kpiCell('En serv. técnico', stCount, ()=>navigate('equipos',{estado:'en_servicio_tecnico'}), stCount>0?'warn':''),
    kpiCell('Alertas >30 d', alertaDias.length, ()=>navigate('equipos',{alerta30:'1'}), alertaDias.length>0?'alert':''),
    kpiCell('Pend. por resolver', pendAbiertos.length, ()=>navigate('pendientes',{}), pendAbiertos.length>0?'warn':''),
    kpiCell('Ciclos abiertos', ciclosAbiertos.length, ()=>navigate('ciclos',{estado:'abierto'})),
    kpiCell('Eventos borrador', eventosBorrador.length, ()=>navigate('eventos',{oficial:'No'}))
  );

  root.appendChild(el('div',{class:'view'},
    el('h2',{},'Resumen general'),
    el('div',{class:'subtitle'}, today.toLocaleDateString('es-CL',{weekday:'long',day:'2-digit',month:'long',year:'numeric'})),
    renderWelcomeBanner(),
    kpis,
    renderSumMPAnual(year),
    renderSumServicios(),
    renderSumMPDelMes(year, month),
    alertaDias.length > 0 ? renderSumAlertas(alertaDias) : null,
    pendAbiertos.length > 0 ? el('div',{class:'sum-section'},
      el('div',{class:'sum-section-hd'},
        el('h3',{}, `Pendientes próximos / vencidos`),
        el('span',{class:'hint'}, `${pendAbiertos.length} abiertos · click para ver`)
      ),
      renderPendientesTabla(pendAbiertos.sort((a,b)=>(a.fechaComp||'9999').localeCompare(b.fechaComp||'9999')).slice(0,10))
    ) : null
  ));
};

VIEWS.porResolver = function(root){
  state.equipos.forEach(recalcEstadoEquipo);
  const hoy = hoyLocal();
  const activos = state.pendientes.filter(p=>!p.anulado && p.estado!=='cerrado');
  const venc = activos.filter(p=>p.fechaComp && p.fechaComp < hoy);
  const noInic = activos.filter(p=>p.estado==='no_iniciado' && !(p.fechaComp && p.fechaComp < hoy));
  const enProc = activos.filter(p=>p.estado==='en_proceso' && !(p.fechaComp && p.fechaComp < hoy));
  const ciclos = state.ciclos.filter(c=>c.estado==='abierto');
  const borr = state.eventos.filter(e=>e.oficial!=='Sí' && !e.anulado);
  const confl = (state.conflictos||[]).filter(c=>c.estado==='pendiente'||c.estado==='pospuesto');
  const total = activos.length + ciclos.length + borr.length + confl.length;

  const v = el('div',{class:'view'},
    el('div',{class:'pr-hero'},
      el('h2',{}, 'Por resolver'),
      el('div',{class:'subtitle'},
        new Date().toLocaleDateString('es-CL',{weekday:'long',day:'2-digit',month:'long',year:'numeric'}) +
        (total>0 ? ` · te quedan ${total} cosa${total!==1?'s':''} por resolver` : ' · todo al día'))
    )
  );

  if(total === 0){
    v.appendChild(el('div',{class:'pr-allclear'},
      el('div',{style:{fontSize:'15px',fontWeight:'700',color:'var(--op)',marginBottom:'4px'}},'¡Todo al día!'),
      el('div',{},'No tienes pendientes, ciclos abiertos, borradores ni conflictos por resolver.')));
    root.appendChild(v); return;
  }

  const seccion = (titulo, count, urge) => el('div',{class:'pr-section'},
    el('div',{class:'pr-section-hd'}, el('h3',{style:urge?{color:'var(--noop)'}:null}, titulo), el('span',{class:'count'}, count)));
  const tarjetaPend = (p, color) => {
    const acts = el('div',{class:'pr-acts'});
    if(p.estado==='no_iniciado') acts.appendChild(el('button',{class:'small',onclick:()=>cambiarEstadoPend(p,'en_proceso')},'Empezar'));
    acts.appendChild(el('button',{class:'small primary',onclick:()=>cerrarPendiente(p)},'Resolver'));
    return el('div',{class:'pr-card '+color},
      el('div',{class:'pr-body'},
        el('div',{class:'pr-title'}, (p.inv||'')+' · '+(p.equipo||'')),
        el('div',{class:'pr-sub'}, (TIPO_PENDIENTE[p.tipo]||p.tipo) + (p.desc? ' — '+p.desc : '')),
        el('div',{style:{marginTop:'7px'}}, badgePend(p.estado),
          p.fechaComp ? el('span',{class:'badge',style:{marginLeft:'6px'}}, 'Compromiso '+fmtFecha(p.fechaComp)) : null)
      ), acts);
  };
  const tarjeta = (color, titulo, sub, btnLabel, onclick, btnPrimary) => el('div',{class:'pr-card '+color},
    el('div',{class:'pr-body'}, el('div',{class:'pr-title'}, titulo), el('div',{class:'pr-sub'}, sub)),
    el('div',{class:'pr-acts'}, el('button',{class:'small'+(btnPrimary?' primary':''),onclick}, btnLabel)));

  if(venc.length){ const s=seccion('Vencidos', venc.length+' atrasado(s)', true); venc.forEach(p=>s.appendChild(tarjetaPend(p,'red'))); v.appendChild(s); }
  if(noInic.length){ const s=seccion('No iniciados', noInic.length+' por empezar'); noInic.forEach(p=>s.appendChild(tarjetaPend(p,'gray'))); v.appendChild(s); }
  if(enProc.length){ const s=seccion('En proceso', enProc.length+' en curso'); enProc.forEach(p=>s.appendChild(tarjetaPend(p,'amber'))); v.appendChild(s); }
  if(ciclos.length){ const s=seccion('Ciclos correctivos abiertos', String(ciclos.length));
    ciclos.slice(0,15).forEach(c=>{ const eq=findEquipo(c.inv);
      s.appendChild(tarjeta('teal', c.folio||'(sin folio)', (c.inv||'')+' · '+(eq?eq.equipo:'')+' · abierto '+fmtFecha(c.fechaApertura), 'Ver equipo', ()=>navigate('equipo',{inv:c.inv}))); });
    v.appendChild(s); }
  if(borr.length){ const s=seccion('Borradores por archivar', borr.length+' documento(s)');
    borr.slice(0,15).forEach(e=>
      s.appendChild(tarjeta('gray', e.tipo+' · '+(e.equipo||''), (e.inv||'')+' · '+fmtFecha(e.fecha)+' · confirma el documento y oficialízalo', 'Ver ficha', ()=>navigate('equipo',{inv:e.inv}))));
    v.appendChild(s); }
  if(confl.length){ const s=seccion('Conflictos con el maestro', confl.length+' por revisar');
    s.appendChild(tarjeta('teal','Diferencias con la carta gantt', confl.length+' celda(s) por confirmar', 'Revisar', ()=>navigate('conciliacion'), true));
    v.appendChild(s); }
  root.appendChild(v);
};

function kpiCell(lbl, val, onclick, cls){
  return el('div',{class:'kpi '+(cls||''),onclick},
    el('div',{class:'lbl'}, lbl),
    el('div',{class:'val'}, String(val))
  );
}

function renderWelcomeBanner(){
  // Solo mostrar si no se descartó y el state está fresco.
  if(!stateEsFresh()) return null;
  if(localStorage.getItem('hhha_welcome_dismissed') === '1') return null;

  const fileInput = el('input',{type:'file',accept:'application/json',style:{display:'none'},onchange: async e=>{
    const f = e.target.files[0]; if(!f) return;
    try{
      const txt = await f.text();
      const data = JSON.parse(txt);
      if(!data.__v) throw new Error('No parece un backup válido (falta __v).');
      state = migrate(data);
      save();
      toast(`Backup importado · ${state.eventos.length} eventos, ${state.pendientes.length} pendientes`, 'success');
      navigate('dashboard');
    }catch(err){ toast('Error: '+err.message, 'error'); }
  }});
  const drop = el('div',{class:'mini-drop', onclick:()=>fileInput.click(),
    ondragover: e=>{e.preventDefault();},
    ondrop: e=>{e.preventDefault(); if(e.dataTransfer.files[0]) fileInput.onchange({target:{files:e.dataTransfer.files}});}
  },
    el('strong',{},'Importar backup JSON'),
    el('small',{},'Click o arrastra tu archivo hhha-data-AAAAMMDD.json')
  );

  return el('div',{class:'welcome-banner'},
    el('div',{class:'icon'}, '!'),
    el('div',{class:'content'},
      el('h3',{},'No detecto actividad del usuario en estos datos'),
      el('p',{},
        'El programa cargó el seed inicial (893 equipos, 55 eventos demo). Si ya habías registrado MPs antes y no las ves, ',
        el('strong',{},'es muy probable que abriste el archivo desde otra ubicación.'),
        ' Chrome guarda los datos por ruta de archivo, así que al moverlo a otra carpeta empieza vacío. Importa tu backup JSON para recuperar todo:'
      ),
      drop, fileInput,
      el('div',{style:{marginTop:'10px'}},
        el('button',{class:'dismiss',onclick:e=>{
          localStorage.setItem('hhha_welcome_dismissed','1');
          e.target.closest('.welcome-banner').remove();
        }},'Descartar este aviso (no volverá a aparecer)')
      )
    )
  );
}

// ====== Tabla resumen: MP del año por mes × resultado ======
function renderSumMPAnual(year){
  // Por cada mes: cuenta por código P programadas, y por código R: Si, C* (reprog), FS, NU, Baja, Sin registro
  const rows = MESES.map((mes, idx) => {
    const prog = state.equipos.filter(eq => eq.estado!=='baja' && mpProgramadaEnMes(eq, mes));
    const reg = (eq) => (eq.registro||{})[mes] || {};
    const si = prog.filter(eq => reg(eq).R === 'Si').length;
    const repro = prog.filter(eq => /^C[1-8]$/.test(reg(eq).R||'')).length;
    const fs = prog.filter(eq => reg(eq).R === 'FS').length;
    const nu = prog.filter(eq => reg(eq).R === 'NU').length;
    const baja = prog.filter(eq => reg(eq).R === 'Baja').length;
    const sinReg = prog.filter(eq => !reg(eq).R).length;
    return {mes, total: prog.length, si, repro, fs, nu, baja, sinReg};
  });
  const totals = rows.reduce((a,r)=>({
    total:a.total+r.total, si:a.si+r.si, repro:a.repro+r.repro,
    fs:a.fs+r.fs, nu:a.nu+r.nu, baja:a.baja+r.baja, sinReg:a.sinReg+r.sinReg
  }), {total:0,si:0,repro:0,fs:0,nu:0,baja:0,sinReg:0});

  function cell(val, mes, resultado){
    if(val === 0) return el('td',{class:'cell zero'}, '–');
    return el('td',{class:'cell', onclick:()=>navigate('equipos',{mes,mesYear:year,mpResultado:resultado||'todos'})},
      el('span',{class:'v'}, String(val))
    );
  }

  return el('div',{class:'sum-section'},
    el('div',{class:'sum-section-hd'},
      el('h3',{},'MP del año por mes y resultado'),
      el('span',{class:'hint'},`${year} · click en cualquier celda para ver los equipos`)
    ),
    el('table',{class:'sum-table'},
      el('thead',{},
        el('tr',{},
          el('th',{},'Mes'),
          el('th',{title:'Total programadas (X/R/RA/PM)'},'Programadas'),
          el('th',{},'Realizadas'),
          el('th',{title:'Causales C1–C8'},'Reprog.'),
          el('th',{title:'Fuera de servicio'},'FS'),
          el('th',{title:'No ubicable'},'NU'),
          el('th',{},'Baja'),
          el('th',{},'Sin registro')
        )
      ),
      el('tbody',{},
        ...rows.map(r => el('tr',{},
          el('td',{}, r.mes),
          cell(r.total, r.mes, 'todos'),
          cell(r.si, r.mes, 'Si'),
          cell(r.repro, r.mes, 'reprog'),
          cell(r.fs, r.mes, 'FS'),
          cell(r.nu, r.mes, 'NU'),
          cell(r.baja, r.mes, 'Baja'),
          cell(r.sinReg, r.mes, 'sinreg')
        )),
        el('tr',{class:'total-row'},
          el('td',{},'Total año'),
          el('td',{class:'cell',onclick:()=>navigate('equipos',{mpAnual:'1'})}, el('span',{class:'v'}, String(totals.total))),
          el('td',{class:'cell',onclick:()=>navigate('eventos',{tipo:'Mantención preventiva',resultado:'Si'})}, el('span',{class:'v'}, String(totals.si))),
          el('td',{class:'cell',onclick:()=>navigate('eventos',{tipo:'Mantención preventiva',resultado:'reprog'})}, el('span',{class:'v'}, String(totals.repro))),
          el('td',{}, String(totals.fs)),
          el('td',{}, String(totals.nu)),
          el('td',{}, String(totals.baja)),
          el('td',{}, String(totals.sinReg))
        )
      )
    )
  );
}

// ====== Tabla resumen: equipos por servicio × estado ======
function renderSumServicios(){
  const servicios = [...new Set(state.equipos.map(e=>e.servicio).filter(Boolean))].sort();
  const today = hoyLocal();
  const rows = servicios.map(s => {
    const eqs = state.equipos.filter(e => e.servicio === s);
    const op = eqs.filter(e => e.estado === 'operativo').length;
    const noop = eqs.filter(e => e.estado === 'no_operativo').length;
    const st = eqs.filter(e => e.estado === 'en_servicio_tecnico').length;
    const baja = eqs.filter(e => e.estado === 'baja').length;
    const pend = state.pendientes.filter(p => !p.anulado && p.servicio === s && p.estado !== 'cerrado').length;
    return {servicio:s, total:eqs.length, op, noop, st, baja, pend};
  }).sort((a,b)=>(b.noop+b.st+b.pend)-(a.noop+a.st+a.pend));

  const totals = rows.reduce((a,r)=>({total:a.total+r.total,op:a.op+r.op,noop:a.noop+r.noop,st:a.st+r.st,baja:a.baja+r.baja,pend:a.pend+r.pend}),{total:0,op:0,noop:0,st:0,baja:0,pend:0});

  function c(val, servicio, params){
    if(val === 0) return el('td',{class:'cell zero'}, '–');
    return el('td',{class:'cell', onclick:()=>navigate(params.__view||'equipos', {servicio, ...params})}, el('span',{class:'v'}, String(val)));
  }

  return el('div',{class:'sum-section'},
    el('div',{class:'sum-section-hd'},
      el('h3',{},'Equipos por servicio y estado'),
      el('span',{class:'hint'}, `${servicios.length} servicios · ordenados por carga abierta`)
    ),
    el('div',{style:{maxHeight:'400px',overflow:'auto',border:'1px solid var(--border)',borderRadius:'6px'}},
      el('table',{class:'sum-table',style:{marginBottom:'0',border:'none'}},
        el('thead',{},
          el('tr',{},
            el('th',{},'Servicio'),
            el('th',{},'Total'),
            el('th',{},'Operativos'),
            el('th',{},'No op.'),
            el('th',{},'Serv. téc.'),
            el('th',{},'Baja'),
            el('th',{},'Pendientes')
          )
        ),
        el('tbody',{},
          ...rows.map(r => el('tr',{},
            el('td',{}, r.servicio),
            c(r.total, r.servicio, {}),
            c(r.op, r.servicio, {estado:'operativo'}),
            c(r.noop, r.servicio, {estado:'no_operativo'}),
            c(r.st, r.servicio, {estado:'en_servicio_tecnico'}),
            c(r.baja, r.servicio, {estado:'baja'}),
            c(r.pend, r.servicio, {__view:'pendientes'})
          )),
          el('tr',{class:'total-row'},
            el('td',{},'Total'),
            el('td',{}, String(totals.total)),
            el('td',{}, String(totals.op)),
            el('td',{}, String(totals.noop)),
            el('td',{}, String(totals.st)),
            el('td',{}, String(totals.baja)),
            el('td',{}, String(totals.pend))
          )
        )
      )
    )
  );
}

// ====== Tabla resumen: MP del mes por ejecutor ======
// Wrapper con toggle Por ejecutor / Por mes
function renderSumMPDelMes(year, monthIdx){
  const wrap = el('div',{class:'sum-section'});
  const modo = {value: getPref('mpSumModo', 'ejecutor')};
  function render(){
    wrap.innerHTML = '';
    const content = modo.value === 'mes'
      ? renderSumMesesMP(year, true)
      : renderSumEjecutoresMP(year, monthIdx, true);
    // Header con toggle
    const hd = el('div',{class:'sum-section-hd'},
      el('h3',{}, content.title),
      el('div',{style:{display:'flex',gap:'8px',alignItems:'center'}},
        el('span',{class:'hint'}, content.hint),
        el('div',{class:'toggle-group'},
          el('button',{class:'small'+(modo.value==='ejecutor'?' primary':''),onclick:()=>{modo.value='ejecutor';setPref('mpSumModo','ejecutor');save({internal:true});render();}}, 'Por ejecutor'),
          el('button',{class:'small'+(modo.value==='mes'?' primary':''),onclick:()=>{modo.value='mes';setPref('mpSumModo','mes');save({internal:true});render();}}, 'Por mes')
        )
      )
    );
    wrap.appendChild(hd);
    wrap.appendChild(content.table);
  }
  render();
  return wrap;
}

function renderSumMesesMP(year, returnParts){
  // Por cada mes: asignadas, ejecutadas, pendientes, % cumplimiento
  const rows = MESES.map((mes, monthIdx) => {
    const keyMes = `${year}-${String(monthIdx+1).padStart(2,'0')}`;
    const asignaciones = (state.asignacionesMP[keyMes]) || {};
    const mpProgEquipos = state.equipos.filter(eq => eq.estado !== 'baja' && mpProgramadaEnMes(eq, mes));
    const conAsig = mpProgEquipos.filter(eq => asignaciones[eq.inv]);
    const ejecutadas = mpProgEquipos.filter(eq => mpDelMesEjecutada(eq, year, monthIdx)).length;
    const asignadas = conAsig.length;
    const sinAsignar = mpProgEquipos.length - asignadas;
    const pendientes = mpProgEquipos.filter(eq => mpEstadoMes(eq, year, monthIdx) === 'pendiente').length;
    const pct = mpProgEquipos.length === 0 ? null : Math.round(ejecutadas / mpProgEquipos.length * 100);
    return {mes, monthIdx, programadas: mpProgEquipos.length, asignadas, sinAsignar, ejecutadas, pendientes, pct};
  });
  const tot = rows.reduce((a,r)=>({programadas:a.programadas+r.programadas, asignadas:a.asignadas+r.asignadas, ejecutadas:a.ejecutadas+r.ejecutadas, pendientes:a.pendientes+r.pendientes}), {programadas:0,asignadas:0,ejecutadas:0,pendientes:0});
  const pctTot = tot.programadas === 0 ? null : Math.round(tot.ejecutadas/tot.programadas*100);
  function c(val, mIdx, params){
    if(val === 0) return el('td',{class:'cell zero'}, '–');
    return el('td',{class:'cell',onclick:()=>navigate('mp',{mes:MESES[mIdx], ...params})}, el('span',{class:'v'}, String(val)));
  }
  const table = el('table',{class:'sum-table'},
    el('thead',{}, el('tr',{},
      el('th',{},'Mes'),
      el('th',{},'Programadas'),
      el('th',{},'Asignadas'),
      el('th',{},'Sin asignar'),
      el('th',{},'Ejecutadas'),
      el('th',{},'Pendientes'),
      el('th',{},'Cumplimiento')
    )),
    el('tbody',{},
      ...rows.map(r => el('tr',{},
        el('td',{}, r.mes),
        c(r.programadas, r.monthIdx, {}),
        c(r.asignadas, r.monthIdx, {}),
        r.sinAsignar > 0 ? el('td',{class:'cell',onclick:()=>navigate('mp',{mes:r.mes, sinAsignar:'1'}),style:{color:r.sinAsignar>0?'var(--st)':null}}, el('span',{class:'v'}, String(r.sinAsignar))) : el('td',{class:'cell zero'},'–'),
        c(r.ejecutadas, r.monthIdx, {estadoMP:'ejec'}),
        c(r.pendientes, r.monthIdx, {estadoMP:'pend'}),
        el('td',{}, r.pct == null ? '–' : el('span',{},
          el('span',{class:'bar',style:{width: Math.max(4, r.pct*0.6)+'px',background: r.pct===100?'var(--op)':r.pct>=50?'var(--st)':'var(--noop)'}}),
          r.pct + '%'
        ))
      )),
      el('tr',{class:'total-row'},
        el('td',{},'Total año'),
        el('td',{}, String(tot.programadas)),
        el('td',{}, String(tot.asignadas)),
        el('td',{}, String(tot.programadas - tot.asignadas)),
        el('td',{}, String(tot.ejecutadas)),
        el('td',{}, String(tot.pendientes)),
        el('td',{}, pctTot == null ? '–' : pctTot+'%')
      )
    )
  );
  if(returnParts){
    return {title:`MP del año ${year} · por mes`, hint:'12 meses · click en celda para abrir vista filtrada', table};
  }
  return el('div',{class:'sum-section'},
    el('div',{class:'sum-section-hd'},
      el('h3',{},`MP del año ${year} · por mes`),
      el('span',{class:'hint'},'12 meses · click en celda para abrir vista filtrada')
    ),
    table
  );
}

function renderSumEjecutoresMP(year, monthIdx, returnParts){
  const mes = NUM_MES[monthIdx];
  const keyMes = `${year}-${String(monthIdx+1).padStart(2,'0')}`;
  state.asignacionesMP[keyMes] = state.asignacionesMP[keyMes] || {};
  const mpProgEquipos = state.equipos.filter(eq => eq.estado !== 'baja' && mpProgramadaEnMes(eq, mes));

  const rows = EJECUTORES.map(ej => {
    const asignados = mpProgEquipos.filter(eq => state.asignacionesMP[keyMes][eq.inv] === ej);
    const ejecutadas = asignados.filter(eq => mpDelMesEjecutada(eq, year, monthIdx)).length;
    const pendientes = asignados.filter(eq => mpEstadoMes(eq, year, monthIdx) === 'pendiente').length;
    const pct = asignados.length === 0 ? null : Math.round(ejecutadas / asignados.length * 100);
    return {ejecutor:ej, asignadas:asignados.length, ejecutadas, pendientes, pct};
  });
  const sinAsignar = mpProgEquipos.filter(eq => !state.asignacionesMP[keyMes][eq.inv]).length;

  const totalAsig = rows.reduce((a,r)=>a+r.asignadas,0);
  const totalEjec = rows.reduce((a,r)=>a+r.ejecutadas,0);
  const totalPend = rows.reduce((a,r)=>a+r.pendientes,0);

  function c(val, ejecutor, params){
    if(val === 0) return el('td',{class:'cell zero'}, '–');
    return el('td',{class:'cell', onclick:()=>navigate('mp', {ejecutor, ...params})}, el('span',{class:'v'}, String(val)));
  }

  const table = el('table',{class:'sum-table'},
    el('thead',{},
      el('tr',{},
        el('th',{},'Ejecutor'),
        el('th',{},'Asignadas'),
        el('th',{},'Ejecutadas'),
        el('th',{},'Pendientes'),
        el('th',{},'Cumplimiento')
      )
    ),
    el('tbody',{},
      ...rows.filter(r=>r.asignadas>0).map(r => el('tr',{},
        el('td',{}, r.ejecutor),
        c(r.asignadas, r.ejecutor, {}),
        c(r.ejecutadas, r.ejecutor, {estadoMP:'ejec'}),
        c(r.pendientes, r.ejecutor, {estadoMP:'pend'}),
        el('td',{},
          r.pct == null ? '–' : el('span',{},
            el('span',{class:'bar',style:{width: Math.max(4, r.pct*0.6)+'px',background: r.pct===100?'var(--op)':r.pct>=50?'var(--st)':'var(--noop)'}}),
            r.pct + '%'
          )
        )
      )),
      sinAsignar > 0 ? el('tr',{style:{background:'#fef9c3'}},
        el('td',{}, el('strong',{}, 'Sin asignar')),
        el('td',{class:'cell', onclick:()=>navigate('mp',{sinAsignar:'1'})}, el('span',{class:'v'}, String(sinAsignar))),
        el('td',{}, '–'), el('td',{}, '–'), el('td',{}, '–')
      ) : null,
      el('tr',{class:'total-row'},
        el('td',{},'Total'),
        el('td',{}, String(totalAsig+sinAsignar)),
        el('td',{}, String(totalEjec)),
        el('td',{}, String(totalPend+sinAsignar)),
        el('td',{}, totalAsig+sinAsignar === 0 ? '–' : Math.round(totalEjec/(totalAsig+sinAsignar)*100)+'%')
      )
    )
  );
  const title = `MP del mes · ${mes} ${year} · por ejecutor`;
  const hint = sinAsignar > 0
    ? el('span',{style:{color:'var(--noop)'}}, `${sinAsignar} sin asignar`)
    : `${totalAsig} asignadas`;
  if(returnParts) return {title, hint, table};
  return el('div',{class:'sum-section'},
    el('div',{class:'sum-section-hd'},
      el('h3',{}, title),
      el('span',{class:'hint'}, hint)
    ),
    table
  );
}

// ====== Tabla resumen de alertas >30 días ======
function renderSumAlertas(alertaDias){
  return el('div',{class:'sum-section'},
    el('div',{class:'sum-section-hd'},
      el('h3',{},`Equipos con >30 días sin avance`),
      el('span',{class:'hint'},`${alertaDias.length} casos · click para ver ficha`)
    ),
    el('table',{class:'data'},
      el('thead',{}, el('tr',{}, ['N° Inv.','Equipo','Servicio','Estado','Días'].map(h=>el('th',{},h)))),
      el('tbody',{}, ...alertaDias.sort((a,b)=>diasEnEstado(b)-diasEnEstado(a)).slice(0,15).map(e =>
        el('tr',{class:'clickable',onclick:()=>navigate('equipo',{inv:e.inv})},
          el('td',{}, e.inv),
          el('td',{}, e.equipo, el('br'), el('small',{class:'muted'}, (e.marca||'')+' '+(e.modelo||''))),
          el('td',{}, e.servicio||'—', el('br'), el('small',{class:'muted'}, e.unidad||'')),
          el('td',{}, badgeEstado(e.estado)),
          el('td',{class:'num',style:{color:'var(--noop)',fontWeight:'600'}}, diasEnEstado(e))
        )
      ))
    )
  );
}

//---------------- EQUIPOS ----------------
VIEWS.equipos = function(root, params){
  // Columnas según la especificación funcional (cap. 3): ID, N° Inventario, Serie, Equipo,
  // Marca, Modelo, Servicio, Unidad, Ubicación, Procedencia y, al final, Estado, Días y Pendientes.
  const COLS = [
    {k:'id',l:'ID',g:e=>e.id!=null?String(e.id):'',num:true, cell:e=>el('td',{class:'num'}, e.id!=null?String(e.id):'—')},
    {k:'inv',l:'N° Inventario',g:e=>e.inv||'', cell:e=>el('td',{}, el('strong',{}, e.inv||'—'))},
    {k:'serie',l:'Serie',g:e=>e.serie||''},
    {k:'equipo',l:'Equipo',g:e=>e.equipo||'',lista:true},
    {k:'marca',l:'Marca',g:e=>e.marca||'',lista:true},
    {k:'modelo',l:'Modelo',g:e=>e.modelo||'',lista:true},
    {k:'servicio',l:'Servicio',g:e=>e.servicio||'',lista:true},
    {k:'unidad',l:'Unidad',g:e=>e.unidad||'',lista:true},
    {k:'ubic',l:'Ubicación',g:e=>e.ubic||'',lista:true},
    {k:'proc',l:'Procedencia',g:e=>e.proc||'',lista:true},
    {k:'estado',l:'Estado',g:e=>ESTADO_LABEL[e.estado]||e.estado||'',lista:true, cell:e=>el('td',{}, badgeEstado(e.estado), (e.estado==='en_servicio_tecnico'||e.estado==='no_operativo') ? el('div',{style:{marginTop:'3px'}}, el('small',{class:'muted'}, 'Enc: '+(encargadoDe(e)||'—'))) : null)},
    {k:'dias',l:'Días en estado',g:e=>e.estadoDesde?String(diasEnEstado(e)):'0',num:true, cell:e=>el('td',{class:'num'}, e.estadoDesde ? diasEnEstado(e)+' d' : el('small',{class:'muted'},'—'))},
    {k:'pend',l:'Pendientes',g:e=>String(pendientesDe(e.inv).filter(p=>p.estado!=='cerrado').length),num:true, cell:e=>{const n=pendientesDe(e.inv).filter(p=>p.estado!=='cerrado').length; return el('td',{class:'num'}, n>0?el('span',{class:'badge abierto'},n):el('small',{class:'muted'},'—'));}}
  ];
  const filtros = {};
  if(params.estado) filtros.estado = ESTADO_LABEL[params.estado] || params.estado;
  if(params.servicio) filtros.servicio = params.servicio;
  let ordK = null, ordDir = 1;
  const search = el('input',{type:'search',placeholder:'Buscar en todo (N° Inv., serie, equipo, marca, modelo, servicio…)',value:params.q||''});
  const thead = el('thead',{});
  const tbody = el('tbody',{});
  const counter = el('div',{class:'muted',style:{fontSize:'12px',padding:'8px 0'}},'');
  const chipsBar = el('div',{class:'filters'});

  function applyParamsFilter(equipos){
    let res = equipos;
    // Filtro por mes/resultado MP (de la tabla resumen)
    if(params.mes && params.mpResultado){
      const mes = params.mes, r = params.mpResultado;
      res = res.filter(eq => {
        if(eq.estado==='baja') return false;
        if(!mpProgramadaEnMes(eq, mes)) return false;
        const reg = (eq.registro||{})[mes] || {};
        if(r === 'todos') return true;
        if(r === 'sinreg') return !reg.R;
        if(r === 'reprog') return /^C[1-8]$/.test(reg.R||'');
        return reg.R === r;
      });
    }
    if(params.alerta30){
      res = res.filter(e => ['no_operativo','en_servicio_tecnico'].includes(e.estado) && diasEnEstado(e) > 30);
    }
    if(params.mpAnual){
      res = res.filter(e => e.estado!=='baja' && Object.values(e.prog||{}).some(p=>['X','R','RA','PM'].includes(p)));
    }
    return res;
  }

  const norm = s => (s||'').toString().toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');
  const valoresUnicos = c => [...new Set(state.equipos.map(e=>{const v=c.g(e); return v==null?'':String(v);}))].filter(v=>v!=='').sort((a,b)=>a.localeCompare(b,'es',{numeric:true}));

  function buildHead(){
    thead.innerHTML = '';
    const trH = el('tr',{});
    COLS.forEach(c=>{
      const flecha = ordK===c.k ? (ordDir>0?' ▲':' ▼') : '';
      trH.appendChild(el('th',{class:'th-sort',title:'Ordenar por '+c.l, onclick:()=>{ if(ordK===c.k) ordDir=-ordDir; else { ordK=c.k; ordDir=1; } render(); }}, c.l+flecha));
    });
    thead.appendChild(trH);
    const trF = el('tr',{class:'filtros-col'});
    COLS.forEach(c=>{
      let ctrl;
      if(c.lista){
        ctrl = el('select',{onchange:e=>{ filtros[c.k]=e.target.value; render(); }},
          el('option',{value:''},'(todos)'),
          ...valoresUnicos(c).map(v=>el('option',{value:v}, v.length>24?v.slice(0,24)+'…':v)));
        ctrl.value = filtros[c.k]||'';
      } else {
        ctrl = el('input',{type:'text',placeholder:'filtrar…',value:filtros[c.k]||'',oninput:e=>{ filtros[c.k]=e.target.value; clearTimeout(window.__eqf); window.__eqf=setTimeout(render,200); }});
      }
      trF.appendChild(el('th',{}, ctrl));
    });
    thead.appendChild(trF);
  }

  function render(){
    state.equipos.forEach(recalcEstadoEquipo);
    const tokens = norm(search.value.trim()).split(/\s+/).filter(Boolean);
    let lista = state.equipos.filter(e => {
      if(tokens.length){
        const hay = [e.inv,e.serie,e.equipo,e.marca,e.modelo,e.servicio,e.unidad,e.ubic,e.fam,e.carpeta].map(norm).join(' ');
        if(!tokens.every(t => hay.includes(t))) return false;
      }
      for(const c of COLS){
        const fv = filtros[c.k]; if(!fv) continue;
        const val = c.g(e);
        if(c.lista){ if(String(val) !== fv) return false; }
        else { if(!norm(val).includes(norm(fv))) return false; }
      }
      if(filtros.__conPend && !pendientesDe(e.inv).some(p=>p.estado!=='cerrado')) return false;
      return true;
    });
    lista = applyParamsFilter(lista);
    if(ordK){ const c = COLS.find(x=>x.k===ordK);
      lista.sort((a,b)=> c.num ? ((+c.g(a)||0)-(+c.g(b)||0))*ordDir : String(c.g(a)).localeCompare(String(c.g(b)),'es')*ordDir);
    }
    buildHead();
    tbody.innerHTML = '';
    lista.slice(0,500).forEach(e => {
      const tr = el('tr',{class:'row-click', title:'Abrir ficha del equipo', onclick:()=>navigate('equipo',{inv:e.inv})});
      COLS.forEach(c => tr.appendChild(c.cell ? c.cell(e) : el('td',{}, c.g(e)||'—')));
      tbody.appendChild(tr);
    });
    counter.textContent = `${lista.length} equipos${lista.length>500?' (mostrando primeros 500)':''}`;
    renderChips();
  }

  function renderChips(){
    chipsBar.innerHTML = '';
    const chips = [];
    if(params.mes && params.mpResultado){
      const r = params.mpResultado === 'todos' ? 'Todas las MP' : params.mpResultado === 'reprog' ? 'Reprogramadas' : params.mpResultado === 'sinreg' ? 'Sin registro' : params.mpResultado;
      chips.push(['MP '+params.mes, r, ()=>{delete params.mes; delete params.mpResultado; render();}]);
    }
    if(params.alerta30) chips.push(['Alerta', '>30 días', ()=>{delete params.alerta30; render();}]);
    if(params.mpAnual) chips.push(['MP', 'Programadas en el año', ()=>{delete params.mpAnual; render();}]);
    chips.forEach(([k,v,onclr]) => chipsBar.appendChild(el('span',{class:'filter-chip'},
      el('span',{class:'k'}, k+':'), el('span',{}, v),
      el('span',{class:'x',onclick:onclr}, '×')
    )));
    const hayCol = Object.keys(filtros).some(k=>filtros[k]);
    if(chips.length > 0 || hayCol || search.value){
      chipsBar.appendChild(el('button',{class:'filter-clear',onclick:()=>{
        Object.keys(params).forEach(k=>delete params[k]);
        Object.keys(filtros).forEach(k=>delete filtros[k]);
        search.value='';
        render();
      }},'Limpiar todo'));
    }
  }

  search.addEventListener('input', ()=>{ clearTimeout(window.__eqs); window.__eqs=setTimeout(render,200); });

  state.equipos.forEach(recalcEstadoEquipo);
  const limpiarFiltros = ()=>{ Object.keys(filtros).forEach(k=>delete filtros[k]); };
  const _qa = (lbl, n, fn, cls) => el('button',{class:'qa-btn'+(cls?' '+cls:''), onclick:fn}, `${lbl} (${n})`);
  const barraQA = el('div',{class:'quick-access'},
    el('button',{class:'qa-btn',onclick:()=>{limpiarFiltros();render();}},'Todos'),
    _qa('En servicio técnico', state.equipos.filter(e=>e.estado==='en_servicio_tecnico').length, ()=>{limpiarFiltros();filtros.estado='En servicio técnico';render();}, 'st'),
    _qa('No operativos', state.equipos.filter(e=>e.estado==='no_operativo').length, ()=>{limpiarFiltros();filtros.estado='No operativo';render();}, 'noop'),
    _qa('Con pendientes', state.equipos.filter(e=>pendientesDe(e.inv).some(p=>p.estado!=='cerrado')).length, ()=>{limpiarFiltros();filtros.__conPend=true;render();})
  );
  root.appendChild(el('div',{class:'view'},
    el('h2',{},'Buscar equipos'),
    el('div',{class:'subtitle'},'Planilla de equipos: haz clic en una fila para abrir su ficha (ahí registras eventos y pendientes). Ordena por cualquier columna (clic en su título) y filtra en cada una.'),
    barraQA,
    el('div',{class:'toolbar'}, el('div',{class:'grow'},search)),
    chipsBar,
    counter,
    el('div',{style:{maxHeight:'calc(100vh - 300px)',overflow:'auto',border:'1px solid var(--border)',borderRadius:'10px'}},
      el('table',{class:'data eq-grid buscar-grid',style:{border:'none'}}, thead, tbody)
    )
  ));
  render();
  setTimeout(()=>search.focus(), 50);
};

//---------------- REGISTRO MP (carta gantt navegable) ----------------
VIEWS.registroMP = function(root){
  state.equipos.forEach(recalcEstadoEquipo);
  const year = new Date().getFullYear();
  let mostrarMeses = getPref('regmp_meses', true) !== false;
  const filtros = {};
  let ordK = null, ordDir = 1;
  const norm = s => (s||'').toString().toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');
  const IDENT = [
    {k:'id',l:'ID',g:e=>e.id!=null?String(e.id):'',num:true},
    {k:'carpeta',l:'N° Carpeta',g:e=>e.carpeta!=null?String(e.carpeta):'',num:true},
    {k:'inv',l:'N° Inventario',g:e=>e.inv||''},
    {k:'equipo',l:'Equipo',g:e=>e.equipo||'',lista:true},
    {k:'servicio',l:'Servicio',g:e=>e.servicio||'',lista:true},
    {k:'unidad',l:'Unidad',g:e=>e.unidad||'',lista:true},
    {k:'ubic',l:'Ubicación',g:e=>e.ubic||'',lista:true},
    {k:'proc',l:'Procedencia',g:e=>e.proc||'',lista:true},
    {k:'marca',l:'Marca',g:e=>e.marca||'',lista:true},
    {k:'modelo',l:'Modelo',g:e=>e.modelo||'',lista:true},
    {k:'serie',l:'Serie',g:e=>e.serie||''},
    {k:'ano',l:'Año',g:e=>e.ano!=null?String(e.ano):'',lista:true},
    {k:'vur',l:'VUR',g:e=>e.vur!=null?String(e.vur):'',lista:true},
    {k:'clasif',l:'Clasificación',g:e=>e.clasif||'',lista:true},
    {k:'freq',l:'Frecuencia MP',g:e=>e.freq||'',lista:true}
  ];
  const FINAL = [
    {k:'estado',l:'Estado',g:e=>ESTADO_LABEL[e.estado]||e.estado||'',lista:true},
    {k:'dias',l:'Días en estado',g:e=>e.estadoDesde?String(diasEnEstado(e)):'0',num:true},
    {k:'pendi',l:'Pendientes',g:e=>String(pendientesDe(e.inv).filter(p=>p.estado!=='cerrado').length),num:true}
  ];
  const mesCols = () => { const a=[]; MESES.forEach(m=>{ a.push({k:'P_'+m,l:m+'·P',g:e=>((e.registro||{})[m]||{}).P||(e.prog||{})[m]||'',lista:true,mes:true}); a.push({k:'R_'+m,l:m+'·R',g:e=>((e.registro||{})[m]||{}).R||'',lista:true,mes:true,esR:true}); }); return a; };
  const cols = () => mostrarMeses ? [...IDENT, ...mesCols(), ...FINAL] : [...IDENT, ...FINAL];
  const colByK = k => cols().find(x=>x.k===k);
  const valoresUnicos = c => [...new Set(state.equipos.map(e=>{const v=c.g(e); return v==null?'':String(v);}))].filter(v=>v!=='').sort((a,b)=>a.localeCompare(b,'es',{numeric:true}));

  const thead = el('thead',{}); const tbody = el('tbody',{});
  const counter = el('div',{class:'muted',style:{fontSize:'12px',padding:'8px 0'}},'');
  const search = el('input',{type:'search',placeholder:'Buscar equipo, marca, modelo, servicio…'});

  function buildHead(){
    const CS = cols();
    thead.innerHTML = '';
    const trH = el('tr',{});
    CS.forEach(c => trH.appendChild(el('th',{class:'th-sort'+(c.mes?' mp-col':''), onclick:()=>{ if(ordK===c.k) ordDir=-ordDir; else { ordK=c.k; ordDir=1; } render(); }}, c.l + (ordK===c.k?(ordDir>0?' ▲':' ▼'):''))));
    trH.appendChild(el('th',{},'Acción'));
    thead.appendChild(trH);
    const trF = el('tr',{class:'filtros-col'});
    CS.forEach(c=>{
      let ctrl;
      if(c.lista){ ctrl = el('select',{onchange:e=>{ filtros[c.k]=e.target.value; render(); }}, el('option',{value:''},'(todos)'), ...valoresUnicos(c).map(v=>el('option',{value:v}, v.length>16?v.slice(0,16)+'…':v))); ctrl.value = filtros[c.k]||''; }
      else { ctrl = el('input',{type:'text',placeholder:'…',value:filtros[c.k]||'',oninput:e=>{ filtros[c.k]=e.target.value; clearTimeout(window.__rmf); window.__rmf=setTimeout(render,200); }}); }
      trF.appendChild(el('th',{class:c.mes?'mp-col':''}, ctrl));
    });
    trF.appendChild(el('th',{}));
    thead.appendChild(trF);
  }
  function render(){
    state.equipos.forEach(recalcEstadoEquipo);
    const CS = cols();
    const tokens = norm(search.value.trim()).split(/\s+/).filter(Boolean);
    let lista = state.equipos.filter(e=>{
      if(tokens.length){ const hay=[e.inv,e.serie,e.equipo,e.marca,e.modelo,e.servicio,e.unidad,e.ubic].map(norm).join(' '); if(!tokens.every(t=>hay.includes(t))) return false; }
      for(const c of CS){ const fv=filtros[c.k]; if(!fv) continue; const val=c.g(e); if(c.lista){ if(String(val)!==fv) return false; } else if(!norm(val).includes(norm(fv))) return false; }
      return true;
    });
    if(ordK){ const c=colByK(ordK); if(c) lista.sort((a,b)=> c.num?((+c.g(a)||0)-(+c.g(b)||0))*ordDir : String(c.g(a)).localeCompare(String(c.g(b)),'es')*ordDir); }
    buildHead();
    tbody.innerHTML = '';
    lista.slice(0,500).forEach(e=>{
      const tr = el('tr',{});
      CS.forEach(c=>{
        if(c.k==='estado') tr.appendChild(el('td',{}, badgeEstado(e.estado)));
        else if(c.k==='pendi'){ const n=pendientesDe(e.inv).filter(p=>p.estado!=='cerrado').length; tr.appendChild(el('td',{class:'num'}, n>0?el('span',{class:'badge abierto'},n):el('small',{class:'muted'},'—'))); }
        else if(c.mes){ const v=c.g(e); tr.appendChild(el('td',{class:'mp-col'+(c.esR&&v==='Si'?' mp-ok':'')+(c.esR&&/^C[1-8]$/.test(v)?' mp-rep':'')}, v||'')); }
        else tr.appendChild(el('td',{}, c.g(e)||'—'));
      });
      tr.appendChild(el('td',{class:'actions'}, el('button',{class:'small',onclick:()=>navigate('equipo',{inv:e.inv})},'Abrir')));
      tbody.appendChild(tr);
    });
    counter.textContent = `${lista.length} equipos${lista.length>500?' (mostrando primeros 500)':''}`;
  }
  search.addEventListener('input', ()=>{ clearTimeout(window.__rms); window.__rms=setTimeout(render,200); });
  const btnMeses = el('button',{class:'qa-btn',onclick:()=>{ mostrarMeses=!mostrarMeses; setPref('regmp_meses',mostrarMeses); save({internal:true}); btnMeses.textContent = mostrarMeses?'➖ Ocultar meses':'➕ Mostrar meses'; render(); }}, mostrarMeses?'➖ Ocultar meses':'➕ Mostrar meses');
  root.appendChild(el('div',{class:'view'},
    el('h2',{},'Registro MP '+year),
    el('div',{class:'subtitle'},'Carta gantt navegable: programado (P) y realizado (R) por mes, más estado, días y pendientes. Ordena y filtra en cualquier columna; "Abrir" lleva a la ficha.'),
    el('div',{class:'toolbar'}, el('div',{class:'grow'},search), btnMeses, counter),
    el('div',{style:{overflow:'auto',maxHeight:'calc(100vh - 230px)',border:'1px solid var(--border)',borderRadius:'10px'}},
      el('table',{class:'data eq-grid',style:{border:'none',fontSize:'12px'}}, thead, tbody)
    )
  ));
  render();
};

//---------------- EQUIPO (ficha) ----------------
VIEWS.equipo = function(root, params){
  const eq = findEquipo(params.inv);
  if(!eq){
    root.appendChild(el('div',{class:'view'},
      el('div',{class:'empty'},'Equipo no encontrado: '+params.inv),
      el('button',{onclick:()=>navigate('equipos')},'← Volver')
    ));
    return;
  }
  recalcEstadoEquipo(eq);
  const evs = eventosDe(eq.inv);
  const evsAnulados = state.eventos.filter(e => e.inv === eq.inv && e.anulado);
  const ciclos = ciclosDe(eq.inv);
  const pends = pendientesDe(eq.inv);
  const conflicts = conflictosDe(eq.inv);

  const year = new Date().getFullYear();

  // --- 4.1 Datos del equipo ---
  const datosBlock = el('div',{class:'grid-2'},
    el('div',{class:'section'},
      el('h3',{},'Identificación'),
      el('dl',{class:'kv'},
        el('dt',{},'N° Inventario'), el('dd',{}, eq.inv||'—'),
        el('dt',{},'N° Carpeta'), el('dd',{}, fmt(eq.carpeta)),
        el('dt',{},'Serie'), el('dd',{}, fmt(eq.serie)),
        el('dt',{},'Familia'), el('dd',{}, fmt(eq.fam)),
        el('dt',{},'Equipo'), el('dd',{}, fmt(eq.equipo)),
        el('dt',{},'Marca / Modelo'), el('dd',{}, `${fmt(eq.marca)} ${fmt(eq.modelo)}`),
        el('dt',{},'Año instalación'), el('dd',{}, fmt(eq.ano)),
        el('dt',{},'Procedencia'), el('dd',{}, fmt(eq.proc))
      )
    ),
    el('div',{class:'section'},
      el('h3',{},'Ubicación y estado'),
      el('dl',{class:'kv'},
        el('dt',{},'Servicio'), el('dd',{}, fmt(eq.servicio)),
        el('dt',{},'Unidad'), el('dd',{}, fmt(eq.unidad)),
        el('dt',{},'Ubicación'), el('dd',{}, fmt(eq.ubic)),
        el('dt',{},'Clasificación'), el('dd',{}, fmt(eq.clasif)),
        el('dt',{},'Vida útil residual'), el('dd',{}, fmt(eq.vur)),
        el('dt',{},'Frecuencia MP'), el('dd',{}, fmt(eq.freq)),
        el('dt',{},'Estado actual'), el('dd',{}, badgeEstado(eq.estado), ' ', el('small',{class:'muted'}, diasEnEstado(eq)+' días')),
        el('dt',{},'Sub-estado'), el('dd',{}, fmt(eq.subestado))
      )
    )
  );

  // --- Secciones contraíbles, una bajo otra (cap. 4 de la especificación) ---
  const pendAbiertos = pends.filter(p=>p.estado!=='cerrado').length;
  const lblHist = evsAnulados.length > 0
    ? `Historial de eventos (${evs.length} activos · ${evsAnulados.length} anulado${evsAnulados.length>1?'s':''})`
    : `Historial de eventos (${evs.length})`;
  const secHistorial = seccionColapsable(lblHist, renderBitacora(eq), true);
  const secciones = el('div',{},
    seccionColapsable('Datos del equipo', datosBlock, true),
    seccionColapsable(`Programación PMP ${year}`, renderMatrizMP(eq), true),
    secHistorial,
    seccionColapsable(`Pendientes (${pendAbiertos} abierto${pendAbiertos!==1?'s':''} · ${pends.length} total)`, renderPendientesEquipo(eq), pendAbiertos>0),
    seccionColapsable(`Ciclos correctivos (${ciclos.length})`, renderCiclos(eq), ciclos.some(c=>c.estado==='abierto')),
    conflicts.length > 0 ? seccionColapsable(`⚠ Conflictos con el maestro (${conflicts.length})`, renderConflictosEquipo(eq, ()=>navigate('equipo',{inv:eq.inv})), true) : null
  );

  // Eventos creados hoy en este equipo (sin contar anulados)
  const evsHoy = state.eventos.filter(e => e.inv === eq.inv && !e.anulado &&
    e.ts && new Date(e.ts).toISOString().slice(0,10) === new Date().toISOString().slice(0,10));
  const evsHoyBanner = evsHoy.length > 0
    ? el('div',{class:'today-chip', title:'Eventos registrados hoy en este equipo. Click para ir al Historial.',
        onclick:()=>{ secHistorial.open=true; secHistorial.scrollIntoView({behavior:'smooth',block:'start'}); }},
        `${evsHoy.length} evento${evsHoy.length>1?'s':''} hoy`,
        el('span',{style:{marginLeft:'5px',opacity:.7}}, '→'))
    : null;

  root.appendChild(el('div',{class:'view'},
    el('div',{style:{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'10px',flexWrap:'wrap',gap:'8px'}},
      el('div',{style:{display:'flex',alignItems:'center',gap:'8px',flexWrap:'wrap'}},
        el('button',{class:'ghost',onclick:()=>navBack('equipos')},'← Volver'),
        el('h2',{style:{display:'inline-block',marginLeft:'4px'}},`${eq.equipo} · ${eq.inv}`),
        evsHoyBanner
      ),
      el('div',{style:{display:'flex',gap:'6px'}},
        el('button',{class:'primary',onclick:()=>mpRapida({invDefault:eq.inv}),title:'Registrar Mantención Preventiva rápida'},'➕ MP'),
        el('button',{onclick:()=>nuevoEvento({invDefault:eq.inv}),title:'Crear evento completo (7 tipos)'},'➕ Evento'),
        el('button',{onclick:()=>nuevoPendiente({invDefault:eq.inv}),title:'Crear pendiente / tarea'},'➕ Pendiente'),
        eq.estado !== 'baja' ? el('button',{class:'danger',onclick:()=>darDeBaja(eq),title:'Marcar equipo como baja'},'⊘ Dar de baja') : null
      )
    ),
    secciones
  ));
};

function renderMatrizMP(eq){
  const cellClass = (v) => {
    if(!v) return '';
    if(v==='X') return 'mp-cell-x';
    if(v==='R') return 'mp-cell-r';
    if(v==='RA') return 'mp-cell-ra';
    if(v==='PM') return 'mp-cell-pm';
    if(v==='Si') return 'mp-cell-si';
    if(/^C[1-8]$/.test(v)) return 'mp-cell-c';
    if(v==='FS') return 'mp-cell-fs';
    if(v==='Baja') return 'mp-cell-baja';
    if(v==='NU') return 'mp-cell-nu';
    return '';
  };
  const trP = el('tr',{}, el('td',{class:'lbl-row'},'P (Programación)'));
  const trR = el('tr',{}, el('td',{class:'lbl-row'},'R (Resultado)'));
  const trE = el('tr',{}, el('td',{class:'lbl-row'},'Ejecutor'));
  const year = new Date().getFullYear();
  // Mapa de eventos MP por mes de este equipo (para tooltip)
  const evsMPPorMes = {};
  state.eventos.filter(e => e.inv === eq.inv && e.tipo === 'Mantención preventiva' && !e.anulado).forEach(ev => {
    if(!ev.fecha) return;
    const mIdx = new Date(ev.fecha + 'T00:00:00').getMonth();
    const mes = MESES[mIdx];
    if(!evsMPPorMes[mes] || ev.fecha > evsMPPorMes[mes].fecha) evsMPPorMes[mes] = ev;
  });
  MESES.forEach((m, idx) => {
    const p = ((eq.registro||{})[m]||{}).P || (eq.prog||{})[m] || '';
    const r = ((eq.registro||{})[m]||{}).R || '';
    const conflP = celdaTieneConflicto(eq.inv, m, 'P');
    const conflR = celdaTieneConflicto(eq.inv, m, 'R');
    // Tooltip para celda R con resultado: muestra evento MP que la generó
    let tipR = '';
    if(conflR) tipR = 'Conflicto con maestro: '+(conflR.valorMaestro||'(vacío)');
    else if(r){
      const ev = evsMPPorMes[m];
      if(ev){
        tipR = `${m} · ${fmtFecha(ev.fecha)} · ${ev.ejecutor||'sin ejecutor'} · Resultado: ${r}` +
               (ev.obs ? `\n${ev.obs.slice(0,140)}` : '');
      } else {
        tipR = `${m} · Resultado registrado: ${r} (sin evento asociado)`;
      }
    }
    let tipP = '';
    if(conflP) tipP = 'Conflicto con maestro: '+(conflP.valorMaestro||'(vacío)');
    else if(p && !r) tipP = 'Click para registrar MP rápida en '+m;
    else if(p) tipP = `${m} · Programación: ${p}`;
    const tdP = el('td',{class:cellClass(p)+(conflP?' has-conflict':''), title: tipP}, p||'');
    const tdR = el('td',{class:cellClass(r)+(conflR?' has-conflict':''), title: tipR}, r||'');
    if(conflP){
      tdP.onclick = ()=>navigate('conciliacion');
      tdP.style.cursor = 'pointer';
    } else if(p && !r){
      const fechaSug = year+'-'+String(idx+1).padStart(2,'0')+'-15';
      tdP.onclick = ()=>mpRapida({invDefault:eq.inv, fechaDefault: fechaSug});
      tdP.style.cursor = 'pointer';
    }
    if(conflR) tdR.onclick = ()=>navigate('conciliacion');
    if(conflR) tdR.style.cursor = 'pointer';
    const ejec = (evsMPPorMes[m] && evsMPPorMes[m].ejecutor) || '';
    trP.appendChild(tdP);
    trR.appendChild(tdR);
    trE.appendChild(el('td',{class:'mp-ejec', title: ejec || ''}, ejec ? (ejec.length>10?ejec.slice(0,9)+'…':ejec) : ''));
  });
  return el('div',{class:'section'},
    el('h3',{},`Programación PMP ${year}`),
    el('div',{style:{overflowX:'auto'}},
      el('table',{class:'mp-matrix'},
        el('thead',{}, el('tr',{}, el('th',{},'Mes'), ...MESES.map(m=>el('th',{},m)))),
        el('tbody',{}, trP, trR, trE)
      )
    ),
    el('div',{style:{marginTop:'10px',fontSize:'12px'},class:'muted'},
      'Códigos P: X=Programado · R=Reprogramado · RA=Reprog. año ant. · PM=Puesta en marcha. ',
      'Códigos R: Si=Realizado · C1–C8=Causal · FS=Fuera servicio · Baja · NU=No ubicable.'
    )
  );
}

// Imprime el historial de eventos del equipo: abre una ventana limpia y lanza el diálogo
// de impresión del navegador (también permite "Guardar como PDF"). 100% offline.
function imprimirHistorial(eq){
  const esc = s => (s==null?'':String(s)).replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
  const evs = eventosDeTodos(eq.inv).slice().reverse();
  const filas = evs.map(ev => {
    const pendAsoc = state.pendientes.filter(p => p.eventoOrigen === ev.id && !p.anulado).length;
    const desc = esc(ev.tipo)
      + (ev.folio ? ' · Folio '+esc(ev.folio) : '')
      + (ev.resultado ? ' · R: '+esc(ev.resultado) : '')
      + (ev.oficial==='Sí' ? ' · OFICIAL' : '')
      + (ev.anulado ? ' · ANULADO' : '');
    return `<tr class="${ev.anulado?'anu':''}"><td>${esc(fmtFecha(ev.fecha))}</td><td>${desc}</td>`
      + `<td>${esc(ev.estado||'')}</td><td>${esc(ev.ejecutor||'')}</td>`
      + `<td>${esc(ev.obs||'')}</td><td>${pendAsoc>0?pendAsoc:''}</td></tr>`;
  }).join('');
  const html = '<!doctype html><html lang="es"><head><meta charset="utf-8">'
    + '<title>Historial '+esc(eq.inv)+'</title><style>'
    + 'body{font-family:Arial,Helvetica,sans-serif;font-size:12px;color:#111;padding:24px}'
    + 'h1{font-size:16px;margin:0 0 4px} h2{font-size:12px;font-weight:400;color:#555;margin:0 0 14px}'
    + 'table{border-collapse:collapse;width:100%} th,td{border:1px solid #999;padding:5px 7px;text-align:left;vertical-align:top}'
    + 'th{background:#eee} tr.anu td{color:#999;text-decoration:line-through}'
    + '.tb{margin:10px 0 16px} @media print{.noprint{display:none}}'
    + '</style></head><body>'
    + '<h1>Historial de eventos — '+esc(eq.equipo||'')+' · '+esc(eq.inv)+'</h1>'
    + '<h2>'+esc(fmt(eq.marca))+' '+esc(fmt(eq.modelo))+' · Serie '+esc(fmt(eq.serie))
    +   ' · '+esc(fmt(eq.servicio))+' · Estado: '+esc(ESTADO_LABEL[eq.estado]||eq.estado||'—')
    +   ' · Impreso '+esc(new Date().toLocaleString('es-CL'))+'</h2>'
    + '<div class="tb noprint"><button onclick="window.print()">🖨 Imprimir</button></div>'
    + '<table><thead><tr><th>Fecha</th><th>Descripción</th><th>Estado</th><th>Ejecutor</th><th>Observación</th><th>Pend.</th></tr></thead>'
    + '<tbody>'+(filas||'<tr><td colspan="6">Sin eventos registrados.</td></tr>')+'</tbody></table>'
    + '</body></html>';
  const w = window.open('', '_blank');
  if(!w){ toast('Permite las ventanas emergentes del navegador para imprimir.', 'error'); return; }
  w.document.open(); w.document.write(html); w.document.close(); w.focus();
  setTimeout(()=>{ try{ w.print(); }catch(e){} }, 350);
}

function renderBitacora(eq){
  const todos = eventosDeTodos(eq.inv).slice().reverse();
  const activos = todos.filter(e => !e.anulado);
  const anulados = todos.filter(e => e.anulado);
  // Una fila por evento, en columnas: Fecha · Descripción · Estado · Ejecutor · Pendientes · Acciones.
  const fila = (ev) => {
    const pendsEv = state.pendientes.filter(p => p.eventoOrigen === ev.id && !p.anulado);
    // Descripción: tipo + sellos (oficial/borrador/auto/lote) + folio + resultado + observación.
    const desc = el('td',{},
      el('div',{},
        el('strong',{}, ev.tipo), ' ',
        ev.anulado ? el('span',{class:'badge anulado-badge'},'Anulado') :
          (ev.oficial==='Sí' ? el('span',{class:'badge ofic-si'},'Oficial') : el('span',{class:'badge ofic-no'},'Borrador')),
        ev.origen === 'conciliacion_auto' ? el('span',{class:'badge auto-badge',title:'Creado automáticamente al subir el maestro. Fecha = día 15 del mes.'},'🔗 Auto-maestro') : null,
        ev.origen === 'conciliacion' ? el('span',{class:'badge auto-badge',title:'Creado al aceptar un conflicto del maestro en Conciliación.'},'🔗 Conciliación') : null,
        ev.origen === 'masivo' ? el('span',{class:'badge ofic-no',title:'Registrado en lote desde MP del mes'},'⚡ Lote') : null,
        ev.folio ? el('span',{class:'pill'}, 'Folio: '+ev.folio) : null,
        ev.resultado ? el('span',{class:'pill'}, 'R: '+ev.resultado) : null
      ),
      ev.empresa ? el('div',{class:'muted',style:{fontSize:'12px',marginTop:'3px'}}, 'Empresa: '+ev.empresa) : null,
      ev.obs ? el('div',{class:'muted',style:{fontSize:'12px',marginTop:'4px',whiteSpace:'pre-wrap'}}, ev.obs) : null,
      ev.anulado ? el('div',{class:'muted',style:{fontSize:'12px',marginTop:'4px',color:'var(--noop)'}},
        '⊘ Anulado'+(ev.fechaAnulacion ? ' · '+new Date(ev.fechaAnulacion).toLocaleString('es-CL') : '')+(ev.motivoAnulacion ? ' · Motivo: '+ev.motivoAnulacion : '')
      ) : null
    );
    return el('tr',{class: ev.anulado?'ev-anulado':''},
      el('td',{style:{whiteSpace:'nowrap'}}, fmtFecha(ev.fecha),
        ev.ts ? el('small',{class:'muted',style:{display:'block',fontSize:'10px',marginTop:'2px'}}, 'creado '+new Date(ev.ts).toLocaleString('es-CL',{day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'})) : null),
      desc,
      el('td',{}, (ev.tipo==='Mantención preventiva' && ev.resultado ? estadoMPDesdeResultado(ev.resultado) : ev.estado) || el('small',{class:'muted'},'—')),
      el('td',{}, ev.ejecutor || el('small',{class:'muted'},'—')),
      el('td',{}, pendsEv.length === 0
        ? el('small',{class:'muted'},'—')
        : el('div',{}, ...pendsEv.map(p => el('span',{class:'tag',title:'Abrir pendiente',style:{cursor:'pointer',display:'inline-block',margin:'2px 3px 0 0'},onclick:()=>abrirPendiente(p)},
            (TIPO_PENDIENTE[p.tipo]||p.tipo)+' · '+(ESTADO_PEND_LABEL[p.estado]||p.estado))))),
      el('td',{class:'actions',style:{whiteSpace:'nowrap'}},
        !ev.anulado ? el('div',{style:{display:'flex',gap:'4px',flexWrap:'wrap'}},
          el('button',{class:'small',onclick:()=>nuevoPendiente({invDefault:ev.inv, eventoOrigen:ev.id}),title:'Agregar un pendiente ligado a este evento'},'➕ Pend.'),
          ev.oficial !== 'Sí' ? el('button',{class:'small primary',onclick:()=>oficializarEvento(ev),title:'Marcar como oficial'},'✓ Oficializar') : null,
          el('button',{class:'small',onclick:()=>editarEvento(ev),title:'Editar campos básicos'},'✎ Editar'),
          el('button',{class:'small danger',onclick:()=>anularEvento(ev),title:'Anular evento (revierte efectos)'},'⊘ Anular')
        ) : el('small',{class:'muted'},'—')
      )
    );
  };
  return el('div',{class:'section'},
    el('div',{style:{display:'flex',justifyContent:'space-between',alignItems:'center',gap:'8px',flexWrap:'wrap'}},
      el('h3',{style:{margin:'0'}},
        'Historial de eventos',
        anulados.length > 0
          ? el('small',{style:{fontWeight:'400',color:'var(--muted)',marginLeft:'8px',textTransform:'none',letterSpacing:'0'}},
              `${activos.length} activo${activos.length!==1?'s':''} · ${anulados.length} anulado${anulados.length!==1?'s':''}`)
          : null
      ),
      el('button',{class:'small',title:'Imprimir el registro de eventos (o guardarlo como PDF)',onclick:()=>imprimirHistorial(eq)},'🖨 Imprimir')
    ),
    el('div',{style:{overflow:'auto'}},
      el('table',{class:'data bitacora-grid'},
        el('thead',{}, el('tr',{}, ['Fecha','Descripción','Estado','Ejecutor','Pendientes','Acciones'].map(h=>el('th',{},h)))),
        el('tbody',{}, todos.length===0
          ? el('tr',{}, el('td',{colspan:'6',class:'empty small'},'Sin eventos registrados.'))
          : null, ...todos.map(fila))
      )
    )
  );
}

function renderCiclos(eq){
  const ciclos = ciclosDe(eq.inv);
  if(ciclos.length===0) return el('div',{class:'empty'},'Sin ciclos correctivos.');
  return el('div',{class:'section'},
    el('h3',{},'Ciclos correctivos'),
    el('div',{}, ...ciclos.map(c => el('div',{class:'ciclo-card '+(c.estado==='cerrado'?'cerrado':'')},
      el('div',{style:{display:'flex',justifyContent:'space-between',alignItems:'center'}},
        el('div',{},
          el('strong',{},'Folio '+c.folio), ' ',
          el('span',{class:'badge '+(c.estado==='abierto'?'abierto':'cerrado')}, c.estado)
        ),
        el('div',{class:'muted',style:{fontSize:'12px'}},
          'Apertura: '+fmtFecha(c.fechaApertura),
          c.fechaCierre ? ' · Cierre: '+fmtFecha(c.fechaCierre) : ''
        )
      ),
      c.ingenieroAsignado ? el('div',{style:{fontSize:'12px',marginTop:'4px'}},'Ingeniero: '+c.ingenieroAsignado) : null,
      c.descripcionInicial ? el('div',{style:{fontSize:'13px',marginTop:'5px'}}, c.descripcionInicial) : null,
      c.estado==='abierto' ? el('div',{style:{marginTop:'5px'}}, el('button',{class:'small',onclick:()=>cerrarCicloManual(c)},'Cerrar manualmente')) : null
    )))
  );
}

function renderResumenEquipo(eq, refresh, setTab){
  const evs = eventosDe(eq.inv).slice().reverse();
  const ultimos = evs.slice(0,3);
  const pends = pendientesDe(eq.inv).filter(p => p.estado !== 'cerrado');
  const ciclos = ciclosAbiertosDe(eq.inv);
  const confl = conflictosDe(eq.inv);
  const year = new Date().getFullYear();
  // Mini matriz MP
  const cellClass = (v) => {
    if(!v) return '';
    if(v==='X') return 'mp-cell-x';
    if(v==='R') return 'mp-cell-r';
    if(v==='RA') return 'mp-cell-ra';
    if(v==='PM') return 'mp-cell-pm';
    if(v==='Si') return 'mp-cell-si';
    if(/^C[1-8]$/.test(v)) return 'mp-cell-c';
    if(v==='FS') return 'mp-cell-fs';
    if(v==='Baja') return 'mp-cell-baja';
    if(v==='NU') return 'mp-cell-nu';
    return '';
  };
  const matrizMini = el('table',{class:'mp-matrix',style:{fontSize:'11px'}},
    el('thead',{}, el('tr',{}, el('th',{},''), ...MESES.map(m=>el('th',{},m)))),
    el('tbody',{},
      el('tr',{}, el('td',{class:'lbl-row'},'P'), ...MESES.map(m => {
        const p = (eq.prog||{})[m] || '';
        return el('td',{class:cellClass(p)}, p||'');
      })),
      el('tr',{}, el('td',{class:'lbl-row'},'R'), ...MESES.map(m => {
        const r = ((eq.registro||{})[m]||{}).R || '';
        return el('td',{class:cellClass(r)}, r||'');
      }))
    )
  );

  return el('div',{class:'resumen-grid'},
    // Bloque MP
    el('div',{class:'section resumen-block'},
      el('div',{class:'resumen-block-hd'},
        el('h3',{},`Programación MP ${year}`),
        el('button',{class:'small primary',onclick:()=>mpRapida({invDefault:eq.inv})}, '➕ Registrar MP')
      ),
      el('div',{style:{overflowX:'auto'}}, matrizMini),
      el('div',{style:{fontSize:'11px',color:'var(--muted)',marginTop:'8px'}},
        `Frecuencia: ${fmt(eq.freq)} · Estado: ${ESTADO_LABEL[eq.estado]||eq.estado||'—'} · Desde: ${fmtFecha(eq.estadoDesde)}`
      )
    ),
    // Bloque últimos eventos
    el('div',{class:'section resumen-block'},
      el('div',{class:'resumen-block-hd'},
        el('h3',{}, `Últimos eventos (${evs.length} total)`),
        el('button',{class:'small ghost',onclick:()=>setTab('bitacora')}, 'Ver bitácora completa →')
      ),
      ultimos.length === 0
        ? el('div',{class:'empty small'},'Sin eventos registrados.')
        : el('div',{class:'resumen-events'}, ...ultimos.map(ev => el('div',{class:'resumen-event-row'},
            el('div',{class:'rev-fecha'}, fmtFecha(ev.fecha)),
            el('div',{class:'rev-tipo'},
              el('strong',{}, ev.tipo),
              ev.resultado ? el('span',{class:'pill'}, ev.resultado) : null,
              ev.oficial==='Sí' ? el('span',{class:'badge ofic-si',style:{marginLeft:'4px'}},'Oficial') : null
            ),
            el('div',{class:'rev-ejec'}, ev.ejecutor||'—'),
            ev.obs ? el('div',{class:'rev-obs'}, ev.obs.slice(0,160)+(ev.obs.length>160?'…':'')) : null
          )))
    ),
    // Bloque pendientes
    el('div',{class:'section resumen-block'},
      el('div',{class:'resumen-block-hd'},
        el('h3',{}, `Pendientes abiertos (${pends.length})`),
        el('button',{class:'small ghost',onclick:()=>setTab('pendientes')}, pends.length>0?'Ver todos →':null)
      ),
      pends.length === 0
        ? el('div',{class:'empty small'},'Sin pendientes abiertos.')
        : el('div',{}, ...pends.slice(0,4).map(p => el('div',{class:'resumen-pend-row',onclick:()=>abrirPendiente(p)},
            el('span',{class:'tag'}, TIPO_PENDIENTE[p.tipo]||p.tipo),
            el('span',{class:'rev-pend-desc'}, p.desc||'—'),
            p.fechaComp ? el('span',{class:'rev-pend-comp'}, fmtFecha(p.fechaComp)) : null
          )))
    ),
    // Bloque conflictos (solo si hay)
    confl.length > 0 ? el('div',{class:'section resumen-block resumen-block-warn'},
      el('div',{class:'resumen-block-hd'},
        el('h3',{style:{color:'var(--noop)'}}, `⚠ ${confl.length} conflicto${confl.length>1?'s':''} con maestro`),
        el('button',{class:'small primary',onclick:()=>setTab('conflictos')},'Resolver →')
      ),
      el('div',{style:{fontSize:'13px',color:'var(--muted)'}},
        confl.slice(0,3).map(c => el('div',{}, '· '+nombreCampoConflicto(c)+' → maestro: '+(c.valorMaestro||'(vacío)')))
      )
    ) : null,
    // Bloque ciclos (solo si hay)
    ciclos.length > 0 ? el('div',{class:'section resumen-block resumen-block-warn'},
      el('div',{class:'resumen-block-hd'},
        el('h3',{}, `Ciclos correctivos abiertos (${ciclos.length})`),
        el('button',{class:'small ghost',onclick:()=>setTab('ciclos')}, 'Ver →')
      ),
      el('div',{}, ...ciclos.map(c => el('div',{style:{fontSize:'13px',marginBottom:'4px'}},
        el('strong',{}, c.folio), ' · apertura: ', fmtFecha(c.fechaApertura),
        c.ingenieroAsignado ? ' · '+c.ingenieroAsignado : ''
      )))
    ) : null
  );
}

function renderConflictosEquipo(eq, refresh){
  const lista = conflictosDe(eq.inv);
  if(lista.length === 0) return el('div',{class:'empty'},'Sin conflictos pendientes con el maestro.');
  function aplicarTodos(accion){
    if(lista.length > 5 && !confirm(`Aplicar "${accion}" a ${lista.length} conflictos de este equipo?`)) return;
    let n = 0, evsSint = 0;
    lista.forEach(c => {
      const r = resolverConflicto(c, accion, null, {skipSave:true});
      n++;
      if(r && r.eventoCreado) evsSint++;
    });
    save();
    refreshNav();
    toast(`${n} resueltos${evsSint>0?' · '+evsSint+' eventos creados':''}`, 'success');
    refresh();
  }
  const acciones = el('div',{style:{display:'flex',gap:'6px',marginBottom:'12px',flexWrap:'wrap'}},
    el('span',{style:{flex:'1',fontSize:'13px',color:'var(--muted)'}}, `${lista.length} conflicto${lista.length>1?'s':''} pendiente${lista.length>1?'s':''}`),
    el('button',{class:'small primary',onclick:()=>aplicarTodos('aceptar_maestro')}, '✓ Aceptar maestro a todos'),
    el('button',{class:'small',onclick:()=>aplicarTodos('mantener_programa')}, '✗ Mantener programa en todos')
  );
  const cards = lista.map(c => {
    const card = el('div',{class:'conf-card '+(c.tipo==='equipo_nuevo'?'altas':c.tipo==='equipo_faltante'?'faltante':'urgent')});
    card.appendChild(el('div',{class:'hd'},
      el('div',{},
        el('div',{class:'title'}, nombreCampoConflicto(c)),
        el('div',{class:'meta'}, 'Detectado: '+new Date(c.fechaDeteccion).toLocaleString('es-CL'))
      ),
      el('span',{class:'badge '+(c.estado==='pendiente'?'noop':'st')}, c.estado)
    ));
    if(c.tipo === 'mp_diferencia'){
      card.appendChild(el('div',{class:'conf-diff'},
        el('div',{class:'prog'},
          el('div',{class:'lbl'},'En el programa'),
          el('div',{class:c.valorPrograma?'val':'val empty'}, c.valorPrograma || 'sin valor')
        ),
        el('div',{class:'mast'},
          el('div',{class:'lbl'},'En el maestro (Excel)'),
          el('div',{class:c.valorMaestro?'val':'val empty'}, c.valorMaestro || 'sin valor')
        )
      ));
    }
    card.appendChild(el('div',{class:'conf-actions'},
      el('button',{class:'primary small',onclick:()=>{const r=resolverConflicto(c,'aceptar_maestro');refresh();}},'✓ Aceptar maestro'),
      el('button',{class:'small',onclick:()=>{resolverConflicto(c,'mantener_programa');refresh();}},'✗ Mantener programa'),
      el('button',{class:'small ghost',onclick:()=>{resolverConflicto(c,'posponer');refresh();}},'⏸ Posponer')
    ));
    return card;
  });
  return el('div',{class:'section'}, acciones, el('div',{}, ...cards));
}

function renderPendientesEquipo(eq){
  const pends = pendientesDe(eq.inv).slice().sort((a,b)=> (a.fechaCrea||'').localeCompare(b.fechaCrea||''));
  if(pends.length===0) return el('div',{class:'empty'},'Sin pendientes.');
  return el('div',{},
    el('div',{style:{textAlign:'right',marginBottom:'8px'}}, el('button',{class:'primary small',onclick:()=>nuevoPendiente({invDefault:eq.inv})},'➕ Pendiente')),
    el('div',{}, ...pends.map(p => el('div',{class:'section',style:{padding:'10px 14px',marginBottom:'8px'}},
      el('div',{style:{display:'flex',justifyContent:'space-between',alignItems:'start',gap:'10px'}},
        el('div',{style:{flex:'1'}},
          el('strong',{}, TIPO_PENDIENTE[p.tipo]||p.tipo), ' ',
          el('span',{class:'badge '+p.estado}, p.estado),
          el('div',{style:{marginTop:'4px'}}, p.desc),
          el('small',{class:'muted'},
            `Creado ${fmtFecha(p.fechaCrea)}`,
            p.fechaComp ? ` · Compromiso ${fmtFecha(p.fechaComp)}` : '',
            p.ejecutor ? ' · '+p.ejecutor : '',
            p.origen ? ' · '+p.origen : ''
          )
        ),
        el('div',{style:{display:'flex',gap:'4px',flexShrink:'0'}},
          el('button',{class:'small',onclick:()=>abrirPendiente(p)},'Ver / editar'),
          p.estado!=='cerrado' ? el('button',{class:'small primary',onclick:()=>cerrarPendiente(p)},'Cerrar') : null
        )
      )
    )))
  );
}

//---------------- MP DEL MES ----------------
VIEWS.mp = function(root, params){
  const today = new Date();
  let year = today.getFullYear(), monthIdx = today.getMonth();
  const mesActual = ()=> NUM_MES[monthIdx];
  const keyMes = ()=> `${year}-${String(monthIdx+1).padStart(2,'0')}`;
  state.asignacionesMP[keyMes()] = state.asignacionesMP[keyMes()] || {};

  const ANIOS = [year-1, year, year+1];
  const selMes = el('select',{}, ...NUM_MES.map((m,i)=>el('option',{value:i}, m)));
  selMes.value = monthIdx;
  const selAnio = el('select',{}, ...ANIOS.map(a=>el('option',{value:a}, String(a))));
  selAnio.value = year;
  function irAMes(d){
    monthIdx += d;
    if(monthIdx > 11){ monthIdx = 0; year++; }
    if(monthIdx < 0){ monthIdx = 11; year--; }
    if(year < ANIOS[0]) year = ANIOS[0];
    if(year > ANIOS[ANIOS.length-1]) year = ANIOS[ANIOS.length-1];
    selMes.value = monthIdx; selAnio.value = year; render();
  }
  selMes.onchange = ()=>{ monthIdx = +selMes.value; render(); };
  selAnio.onchange = ()=>{ year = +selAnio.value; render(); };
  const btnPrevMes = el('button',{class:'small',title:'Mes anterior',onclick:()=>irAMes(-1)},'‹');
  const btnNextMes = el('button',{class:'small',title:'Mes siguiente',onclick:()=>irAMes(1)},'›');

  const selExec = el('select',{},
    el('option',{value:''},'Todos los ejecutores'),
    ...EJECUTORES.map(x=>el('option',{value:x,selected:x===params.ejecutor?'selected':false},x))
  );
  if(params.ejecutor) selExec.value = params.ejecutor;
  const selEst = el('select',{},
    el('option',{value:''},'Todos'),
    el('option',{value:'ejec',selected:params.estadoMP==='ejec'?'selected':false},'Ejecutadas'),
    el('option',{value:'pend',selected:params.estadoMP==='pend'?'selected':false},'Pendientes'),
    el('option',{value:'reprog'},'Reprogramadas (C1–C8)'),
    el('option',{value:'sinAsignar',selected:params.sinAsignar?'selected':false},'Sin asignar')
  );
  if(params.estadoMP) selEst.value = params.estadoMP;
  if(params.sinAsignar) selEst.value = 'sinAsignar';

  const tbody = el('tbody',{});
  const counter = el('div',{class:'muted',style:{fontSize:'12px'}},'');
  const seleccion = new Set();
  const bulkBar = el('div',{class:'bulk-bar',style:{display:'none'}});

  function asignar(inv, ejec){
    state.asignacionesMP[keyMes()][inv] = ejec || null;
    save();
  }

  function renderBulkBar(){
    bulkBar.innerHTML = '';
    if(seleccion.size === 0){ bulkBar.style.display = 'none'; return; }
    bulkBar.style.display = 'flex';
    bulkBar.appendChild(el('span',{class:'bulk-count'}, `${seleccion.size} seleccionado${seleccion.size>1?'s':''}`));
    bulkBar.appendChild(el('button',{class:'small',onclick:()=>{seleccion.clear();render();}},'Limpiar selección'));
    bulkBar.appendChild(el('div',{style:{flex:'1'}}));
    bulkBar.appendChild(el('button',{class:'small primary',onclick:()=>mpMasiva([...seleccion], year, monthIdx, ()=>{seleccion.clear();render();})}, '➕ Registrar MP a todos'));
    bulkBar.appendChild(el('button',{class:'small',onclick:()=>{
      const ej = prompt('Asignar a:\n'+EJECUTORES.map((e,i)=>(i+1)+'. '+e).join('\n')+'\n\nNúmero (1-11):');
      const idx = parseInt(ej) - 1;
      if(idx >= 0 && idx < EJECUTORES.length){
        seleccion.forEach(inv => { state.asignacionesMP[keyMes()][inv] = EJECUTORES[idx]; });
        save();
        toast(`${seleccion.size} equipos asignados a ${EJECUTORES[idx]}`,'success');
        seleccion.clear();
        render();
      }
    }}, '👤 Asignar a ejecutor'));
  }

  function render(){
    state.equipos.forEach(recalcEstadoEquipo);
    const m = mesActual();
    let lista = state.equipos.filter(eq => {
      if(eq.estado === 'baja') return false;
      if(!mpProgramadaEnMes(eq, m)) return false;
      const prevR = Object.entries(eq.registro||{}).some(([mes,obj]) => {
        const idx = MES_NUM[mes];
        return idx < monthIdx && ['FS','Baja','NU'].includes(obj.R);
      });
      if(prevR) return false;
      return true;
    });

    const fExec = selExec.value, fEst = selEst.value;
    lista = lista.filter(eq => {
      const ej = ((state.asignacionesMP[keyMes()]||{})[eq.inv])||null;
      if(fExec && ej !== fExec) return false;
      const est = mpEstadoMes(eq, year, monthIdx);
      if(fEst === 'ejec' && est !== 'ejecutada') return false;
      if(fEst === 'pend' && est !== 'pendiente') return false;
      if(fEst === 'reprog' && est !== 'reprogramada') return false;
      if(fEst === 'sinAsignar' && ej) return false;
      return true;
    });

    tbody.innerHTML = '';
    lista.forEach(eq => {
      const est = mpEstadoMes(eq, year, monthIdx);
      state.asignacionesMP[keyMes()] = state.asignacionesMP[keyMes()] || {};
      const asign = state.asignacionesMP[keyMes()][eq.inv] || '';
      const selA = el('select',{onchange:e=>asignar(eq.inv,e.target.value)},
        el('option',{value:''},'— sin asignar —'),
        ...EJECUTORES.map(x=>el('option',{value:x,selected:x===asign?'selected':false},x))
      );
      selA.value = asign;
      const cb = el('input',{type:'checkbox',checked:seleccion.has(eq.inv)?'checked':false,onclick:e=>{e.stopPropagation();if(e.target.checked) seleccion.add(eq.inv); else seleccion.delete(eq.inv); renderBulkBar();}});
      cb.checked = seleccion.has(eq.inv);
      tbody.appendChild(el('tr',{},
        el('td',{style:{width:'30px'}}, cb),
        el('td',{}, el('strong',{},eq.inv)),
        el('td',{}, eq.equipo),
        el('td',{}, eq.servicio, el('br'), el('small',{class:'muted'}, eq.unidad||'')),
        el('td',{}, eq.marca+' '+eq.modelo),
        el('td',{}, el('span',{class:'badge mp-cause'}, (eq.prog||{})[m])),
        el('td',{}, eq.freq||'—'),
        el('td',{}, selA),
        el('td',{}, est==='ejecutada' ? el('span',{class:'badge mp-si'},'Ejecutada')
                  : est==='reprogramada' ? el('span',{class:'badge st'},'Reprogramada')
                  : est==='otro' ? el('span',{class:'badge'}, resultadoMPMes(eq, year, monthIdx)||'—')
                  : el('span',{class:'badge mp-no'},'Pendiente')),
        el('td',{class:'actions'},
          el('button',{class:'small primary',onclick:()=>mpRapida({invDefault:eq.inv, fechaDefault:fechaSugeridaMP(year, monthIdx)})}, est==='ejecutada'?'➕ MP':'➕ Registrar MP'),
          el('button',{class:'small ghost',onclick:()=>navigate('equipo',{inv:eq.inv})},'Ficha')
        )
      ));
    });
    counter.textContent = `${lista.length} equipos`;
    renderBulkBar();
  }
  [selExec,selEst].forEach(s => s.addEventListener('change',render));
  // Botón seleccionar todos visibles
  const btnSelTodos = el('button',{class:'small ghost',onclick:()=>{
    const m = mesActual();
    const visibles = state.equipos.filter(eq => eq.estado!=='baja' && mpProgramadaEnMes(eq, m));
    visibles.forEach(eq => seleccion.add(eq.inv));
    render();
  }},'☐ Seleccionar todos los visibles');

  // Botones plantilla
  const btnDescargarPlantilla = el('button',{onclick:()=>descargarPlantillaMP(year, monthIdx), title:'Descargar plantilla Excel del mes'}, '📥 Descargar plantilla');
  const fileInputPlantilla = el('input',{type:'file',accept:'.xlsx',style:{display:'none'},onchange:async e=>{
    const f = e.target.files[0]; if(!f) return;
    await subirPlantillaMP(f, year, monthIdx);
    e.target.value = '';
    render();
  }});
  const btnSubirPlantilla = el('button',{class:'primary',onclick:()=>fileInputPlantilla.click(), title:'Subir plantilla con asignaciones llenadas'}, '📤 Subir plantilla');

  root.appendChild(el('div',{class:'view'},
    el('div',{style:{display:'flex',justifyContent:'space-between',alignItems:'center',flexWrap:'wrap',gap:'8px'}},
      el('h2',{},'MP del mes'),
      el('div',{style:{display:'flex',gap:'6px'}},
        btnDescargarPlantilla, btnSubirPlantilla, fileInputPlantilla
      )
    ),
    el('div',{class:'subtitle'},'Selecciona mes, asigna ejecutor y registra el evento al recibir la documentación. Marca varios y usa "Registrar MP a todos" para batch. Se excluyen equipos con FS/Baja/NU en meses previos.'),
    el('div',{class:'toolbar'}, btnPrevMes, selMes, selAnio, btnNextMes, selExec, selEst, btnSelTodos, counter),
    bulkBar,
    el('div',{style:{maxHeight:'calc(100vh - 280px)',overflow:'auto',border:'1px solid var(--border)',borderRadius:'6px'}},
      el('table',{class:'data',style:{border:'none'}},
        el('thead',{}, el('tr',{},
          ['','N° Inv.','Equipo','Servicio/Unidad','Marca-Modelo','Cód. P','Freq.','Ejecutor asignado','Estado MP','Acciones'].map(h=>el('th',{},h))
        )),
        tbody
      )
    )
  ));
  render();
};

//---------------- CICLOS ----------------
VIEWS.ciclos = function(root, params){
  const tab = el('div',{class:'tabs'});
  const body = el('div',{});
  let modo = params.estado || 'abierto';

  function render(){
    tab.innerHTML = '';
    [['abierto',`Abiertos (${state.ciclos.filter(c=>c.estado==='abierto').length})`],['cerrado',`Cerrados (${state.ciclos.filter(c=>c.estado==='cerrado').length})`]].forEach(([k,l])=>{
      tab.appendChild(el('button',{class:modo===k?'active':'',onclick:()=>{modo=k;render();}},l));
    });
    body.innerHTML = '';
    const lista = state.ciclos.filter(c=>c.estado===modo).sort((a,b)=>(b.fechaApertura||'').localeCompare(a.fechaApertura||''));
    if(lista.length===0){
      body.appendChild(el('div',{class:'empty'},'Sin ciclos '+modo+'s.'));
      return;
    }
    const tbl = el('table',{class:'data'},
      el('thead',{}, el('tr',{}, ['Folio SIGEM','Equipo','Servicio','Apertura','Cierre','Ingeniero','Acciones'].map(h=>el('th',{},h)))),
      el('tbody',{}, ...lista.map(c=>{
        const eq = findEquipo(c.inv);
        return el('tr',{},
          el('td',{}, el('strong',{}, c.folio)),
          el('td',{}, eq ? `${eq.equipo} · ${c.inv}` : c.inv),
          el('td',{}, eq?eq.servicio:'—'),
          el('td',{}, fmtFecha(c.fechaApertura)),
          el('td',{}, fmtFecha(c.fechaCierre)),
          el('td',{}, c.ingenieroAsignado||'—'),
          el('td',{class:'actions'},
            el('button',{class:'small',onclick:()=>navigate('equipo',{inv:c.inv})},'Ficha'),
            c.estado==='abierto' ? el('button',{class:'small primary',onclick:()=>cerrarCicloManual(c)},'Cerrar'): null
          )
        );
      }))
    );
    body.appendChild(tbl);
  }

  root.appendChild(el('div',{class:'view'},
    el('h2',{},'Ciclos correctivos'),
    tab, body
  ));
  render();
};

//---------------- PENDIENTES ----------------
VIEWS.pendientes = function(root, params){
  const search = el('input',{type:'search',placeholder:'Buscar pendiente…'});
  const selTipo = el('select',{},
    el('option',{value:''},'Todos los tipos'),
    ...Object.entries(TIPO_PENDIENTE).map(([k,v])=>el('option',{value:k,selected:k===params.tipo?'selected':false},v))
  );
  if(params.tipo) selTipo.value = params.tipo;
  const selEst = el('select',{},
    el('option',{value:''},'Todos los estados'),
    el('option',{value:'no_iniciado',selected:params.estado==='no_iniciado'?'selected':false},'No iniciado'),
    el('option',{value:'en_proceso',selected:params.estado==='en_proceso'?'selected':false},'En proceso'),
    el('option',{value:'cerrado',selected:params.estado==='cerrado'?'selected':false},'Resuelto')
  );
  if(params.estado) selEst.value = params.estado;
  const selExec = el('select',{},
    el('option',{value:''},'Todos los ejecutores'),
    ...EJECUTORES.map(x=>el('option',{value:x,selected:x===params.ejecutor?'selected':false},x))
  );
  if(params.ejecutor) selExec.value = params.ejecutor;
  const selServ = el('select',{},
    el('option',{value:''},'Todos los servicios'),
    ...[...new Set(state.pendientes.map(p=>p.servicio).filter(Boolean))].sort().map(s=>el('option',{value:s,selected:s===params.servicio?'selected':false},s))
  );
  if(params.servicio) selServ.value = params.servicio;
  const container = el('div',{});
  const chipsBar = el('div',{class:'filters'});
  function render(){
    const q = search.value.trim().toLowerCase();
    const t = selTipo.value, e = selEst.value, ex = selExec.value, srv = selServ.value;
    const list = state.pendientes.filter(p => !p.anulado)
      .filter(p => !t || p.tipo === t)
      .filter(p => !e || p.estado === e)
      .filter(p => !ex || p.ejecutor === ex)
      .filter(p => !srv || p.servicio === srv)
      .filter(p => !q || ((p.desc||'')+(p.inv||'')+(p.equipo||'')+(p.servicio||'')).toLowerCase().includes(q))
      .sort((a,b)=>(a.fechaComp||'9999').localeCompare(b.fechaComp||'9999'));
    container.innerHTML = '';
    container.appendChild(el('div',{class:'muted',style:{fontSize:'12px',padding:'8px 0'}}, `${list.length} pendientes`));
    container.appendChild(renderPendientesTabla(list));
    renderChips();
  }
  function renderChips(){
    chipsBar.innerHTML = '';
    const chips = [];
    if(params.tipo) chips.push(['Tipo', TIPO_PENDIENTE[params.tipo], ()=>{delete params.tipo; selTipo.value=''; render();}]);
    if(params.estado) chips.push(['Estado', params.estado, ()=>{delete params.estado; selEst.value=''; render();}]);
    if(params.ejecutor) chips.push(['Ejecutor', params.ejecutor, ()=>{delete params.ejecutor; selExec.value=''; render();}]);
    if(params.servicio) chips.push(['Servicio', params.servicio, ()=>{delete params.servicio; selServ.value=''; render();}]);
    chips.forEach(([k,v,onclr]) => chipsBar.appendChild(el('span',{class:'filter-chip'},
      el('span',{class:'k'}, k+':'), el('span',{}, v), el('span',{class:'x',onclick:onclr}, '×')
    )));
    if(chips.length>0) chipsBar.appendChild(el('button',{class:'filter-clear',onclick:()=>{
      Object.keys(params).forEach(k=>delete params[k]);
      selTipo.value=''; selEst.value=''; selExec.value=''; selServ.value=''; search.value='';
      render();
    }},'Limpiar todo'));
  }
  [search,selTipo,selEst,selExec,selServ].forEach(i => i.addEventListener('input',render));
  root.appendChild(el('div',{class:'view'},
    el('div',{style:{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'6px',flexWrap:'wrap',gap:'10px'}},
      el('h2',{},'Pendientes'),
      el('button',{class:'primary',onclick:()=>nuevoPendiente({})},'➕ Nuevo pendiente')
    ),
    el('div',{class:'subtitle'},'Gestiones, reprogramaciones de MP, documentos faltantes y recomendaciones.'),
    el('div',{class:'toolbar'}, el('div',{class:'grow'},search), selTipo, selEst, selExec, selServ),
    chipsBar,
    container
  ));
  render();
};

function renderPendientesTabla(list){
  if(list.length === 0) return el('div',{class:'empty small'},'Sin pendientes.');
  const today = hoyLocal();
  return el('div',{style:{overflow:'auto'}},
    el('table',{class:'data'},
      el('thead',{}, el('tr',{}, ['Equipo','Tipo','Descripción','Ejecutor','Compromiso','Estado','Acciones'].map(h=>el('th',{},h)))),
      el('tbody',{}, ...list.map(p => {
        const vencido = p.fechaComp && p.fechaComp < today && p.estado !== 'cerrado';
        return el('tr',{},
          el('td',{}, el('strong',{}, p.inv||'—'), el('br'), el('small',{class:'muted'}, p.equipo||'')),
          el('td',{}, el('span',{class:'tag'}, TIPO_PENDIENTE[p.tipo]||p.tipo)),
          el('td',{style:{maxWidth:'400px'}}, p.desc),
          el('td',{}, p.ejecutor||'—'),
          el('td',{style:vencido?{color:'var(--danger)',fontWeight:'600'}:null}, fmtFecha(p.fechaComp)),
          el('td',{}, badgePend(p.estado)),
          el('td',{class:'actions'},
            el('button',{class:'small',onclick:()=>abrirPendiente(p)},'Ver'),
            p.estado==='no_iniciado' ? el('button',{class:'small',onclick:()=>cambiarEstadoPend(p,'en_proceso')},'Empezar') : null,
            p.estado !== 'cerrado' ? el('button',{class:'small primary',onclick:()=>cerrarPendiente(p)},'Resolver') : null,
            el('button',{class:'small ghost',onclick:()=>navigate('equipo',{inv:p.inv})},'Ficha')
          )
        );
      }))
    )
  );
}

//---------------- EVENTOS (bitácora global) ----------------
VIEWS.eventos = function(root, params){
  const search = el('input',{type:'search',placeholder:'Buscar por inv, equipo, folio, ejecutor, empresa, observación…'});
  const selTipo = el('select',{},
    el('option',{value:''},'Todos los tipos'),
    ...TIPOS_EVENTO.map(t=>el('option',{value:t.label,selected:t.label===params.tipo?'selected':false},t.label))
  );
  if(params.tipo) selTipo.value = params.tipo;
  const selOficial = el('select',{},
    el('option',{value:''},'Todos'),
    el('option',{value:'Sí'},'Oficiales'),
    el('option',{value:'No',selected:params.oficial==='No'?'selected':false},'Borradores')
  );
  if(params.oficial) selOficial.value = params.oficial;
  const selRes = el('select',{},
    el('option',{value:''},'Cualquier resultado'),
    el('option',{value:'Si',selected:params.resultado==='Si'?'selected':false},'Si'),
    el('option',{value:'reprog',selected:params.resultado==='reprog'?'selected':false},'C1–C8 (reprog.)'),
    el('option',{value:'FS'},'FS'),
    el('option',{value:'NU'},'NU'),
    el('option',{value:'Baja'},'Baja')
  );
  if(params.resultado) selRes.value = params.resultado;
  const container = el('div',{});
  const chipsBar = el('div',{class:'filters'});
  function render(){
    const q = search.value.trim().toLowerCase();
    const t = selTipo.value, o = selOficial.value, r = selRes.value;
    const list = state.eventos.filter(e => !e.anulado)
      .filter(e => !t || e.tipo === t)
      .filter(e => !o || (e.oficial||'No') === o)
      .filter(e => {
        if(!r) return true;
        if(r === 'reprog') return /^C[1-8]$/.test(e.resultado||'');
        return e.resultado === r;
      })
      .filter(e => {
        if(!q) return true;
        // Enriquecemos con datos del equipo: serie, marca, modelo, ubicación, unidad
        const eq = findEquipo(e.inv);
        const eqBlob = eq ? [eq.serie, eq.marca, eq.modelo, eq.ubic, eq.unidad, eq.fam].filter(Boolean).join(' ') : '';
        return (JSON.stringify(e) + ' ' + eqBlob).toLowerCase().includes(q);
      })
      .sort((a,b)=>(b.fecha||'').localeCompare(a.fecha||''));
    container.innerHTML = '';
    container.appendChild(el('div',{class:'muted',style:{fontSize:'12px',padding:'8px 0'}}, list.length+' eventos'));
    container.appendChild(el('div',{style:{maxHeight:'calc(100vh - 280px)',overflow:'auto',border:'1px solid var(--border)',borderRadius:'6px'}},
      el('table',{class:'data',style:{border:'none'}},
        el('thead',{}, el('tr',{}, ['Fecha','Tipo','Equipo','Servicio','Ejecutor','Folio','Resultado','Estado','Ofic.','Acciones'].map(h=>el('th',{},h)))),
        el('tbody',{}, ...list.map(ev => el('tr',{class:'clickable',onclick:()=>navigate('equipo',{inv:ev.inv})},
          el('td',{}, fmtFecha(ev.fecha)),
          el('td',{}, el('strong',{}, ev.tipo)),
          el('td',{}, ev.equipo||'—', el('br'), el('small',{class:'muted'}, ev.inv||'')),
          el('td',{}, ev.servicio||'—'),
          el('td',{}, ev.ejecutor||'—'),
          el('td',{}, ev.folio||'—'),
          el('td',{}, ev.resultado||'—'),
          el('td',{}, ev.estado||'—'),
          el('td',{}, el('span',{class:'badge '+(ev.oficial==='Sí'?'ofic-si':'ofic-no')}, ev.oficial||'No')),
          el('td',{class:'actions',onclick:e=>e.stopPropagation()},
            el('button',{class:'small',onclick:()=>editarEvento(ev)},'Editar')
          )
        )))
      )
    ));
  }
  function renderChips(){
    chipsBar.innerHTML = '';
    const chips = [];
    if(params.tipo) chips.push(['Tipo', params.tipo, ()=>{delete params.tipo; selTipo.value=''; render();}]);
    if(params.resultado){
      const v = params.resultado === 'reprog' ? 'C1–C8' : params.resultado;
      chips.push(['Resultado', v, ()=>{delete params.resultado; selRes.value=''; render();}]);
    }
    if(params.oficial) chips.push(['Oficial', params.oficial, ()=>{delete params.oficial; selOficial.value=''; render();}]);
    chips.forEach(([k,v,onclr]) => chipsBar.appendChild(el('span',{class:'filter-chip'},
      el('span',{class:'k'}, k+':'), el('span',{}, v), el('span',{class:'x',onclick:onclr}, '×')
    )));
    if(chips.length>0) chipsBar.appendChild(el('button',{class:'filter-clear',onclick:()=>{
      Object.keys(params).forEach(k=>delete params[k]);
      selTipo.value=''; selOficial.value=''; selRes.value=''; search.value='';
      render();
    }},'Limpiar todo'));
  }
  const origRender = render;
  render = function(){ origRender(); renderChips(); };
  [search,selTipo,selOficial,selRes].forEach(i => i.addEventListener('input', render));
  root.appendChild(el('div',{class:'view'},
    el('div',{style:{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'6px',flexWrap:'wrap',gap:'10px'}},
      el('h2',{},'Bitácora de eventos'),
      el('button',{class:'primary',onclick:()=>nuevoEvento({})},'➕ Nuevo evento')
    ),
    el('div',{class:'subtitle'},'Todos los eventos registrados sobre los equipos (los 7 tipos). Click en una fila para abrir la ficha.'),
    el('div',{class:'toolbar'}, el('div',{class:'grow'},search), selTipo, selRes, selOficial),
    chipsBar,
    container
  ));
  render();
};

//==============================================================
// CONCILIACIÓN — Importación y comparación con archivo maestro
//==============================================================
const CONF_KEY = (inv, hoja, mes, campo) => `${inv}|${hoja}|${mes}|${campo||''}`;

function valNorm(v){
  if(v == null) return '';
  return String(v).trim();
}

function conflictoPendiente(inv, hoja, mes, campo){
  return (state.conflictos||[]).find(c =>
    c.tipo === 'mp_diferencia' &&
    c.inv === inv && c.hoja === hoja && c.mes === mes && c.campo === campo &&
    (c.estado === 'pendiente' || c.estado === 'pospuesto')
  );
}

function celdaTieneConflicto(inv, mes, campo){
  // Devuelve el primer conflicto pendiente para esa celda, o null.
  return (state.conflictos||[]).find(c =>
    c.tipo === 'mp_diferencia' && c.inv === inv && c.mes === mes && c.campo === campo &&
    (c.estado === 'pendiente' || c.estado === 'pospuesto')
  ) || null;
}

async function parsearMaestro(file){
  if(typeof XLSX === 'undefined'){
    throw new Error('Parser XLSX no disponible (HTML corrupto). Recarga la página.');
  }
  const buf = await file.arrayBuffer();
  const wb = XLSX.read(buf, {type:'array'});

  // Hoja PMP — buscar por nombre con o sin año
  const sheetPMP = wb.SheetNames.find(n => /^PMP[_\s-]?\d{4}$/i.test(n));
  const sheetReg = wb.SheetNames.find(n => /^Registro[_\s-]?MP[_\s-]?\d{4}$/i.test(n));
  if(!sheetPMP) throw new Error('No se encontró hoja PMP_AAAA en el archivo.');
  if(!sheetReg) throw new Error('No se encontró hoja Registro_MP-AAAA en el archivo.');

  const pmp = parsearHojaPMP(wb.Sheets[sheetPMP]);
  const reg = parsearHojaRegistro(wb.Sheets[sheetReg]);

  return {sheetPMP, sheetReg, pmp, reg};
}

function parsearHojaPMP(ws){
  // Convertimos a matriz de filas
  const rows = XLSX.utils.sheet_to_json(ws, {header:1, defval:null, blankrows:false});
  // Buscar fila de encabezados (contiene 'N° Inventario' o 'N° Inv')
  const headerIdx = rows.findIndex(r => r && r.some(c => /N° Inventario/i.test(String(c||''))));
  if(headerIdx < 0) throw new Error('Hoja PMP sin encabezados reconocibles.');
  const header = rows[headerIdx];
  const invIdx = header.findIndex(c => /N° Inventario/i.test(String(c||'')));
  // Columnas de meses
  const mesIdx = {};
  MESES.forEach(m => {
    const i = header.findIndex(c => String(c||'').trim() === m);
    if(i >= 0) mesIdx[m] = i;
  });
  // Frecuencia y otros campos opcionales
  const equipos = {};
  for(let r = headerIdx + 1; r < rows.length; r++){
    const row = rows[r];
    if(!row) continue;
    const inv = valNorm(row[invIdx]);
    if(!inv || inv === 'N/A') continue;
    const prog = {};
    MESES.forEach(m => {
      const i = mesIdx[m];
      if(i != null){
        const v = valNorm(row[i]);
        if(v) prog[m] = v;
      }
    });
    equipos[inv] = {inv, prog};
  }
  return equipos;
}

function parsearHojaRegistro(ws){
  const rows = XLSX.utils.sheet_to_json(ws, {header:1, defval:null, blankrows:false});
  const headerIdx = rows.findIndex(r => r && r.some(c => /N° Inventario/i.test(String(c||''))));
  if(headerIdx < 0) throw new Error('Hoja Registro sin encabezados reconocibles.');
  const header = rows[headerIdx];
  const invIdx = header.findIndex(c => /N° Inventario/i.test(String(c||'')));
  // Después del header de campos, hay 12 pares P/R consecutivos
  // Buscamos la primera columna con encabezado 'P' después del N° Inventario y a partir de ahí cada 2 cols = mes
  // Estrategia: encontrar el primer 'P' y luego asignar P,R,P,R,P,R... a los 12 meses
  let firstP = -1;
  for(let i = invIdx + 1; i < header.length - 1; i++){
    if(String(header[i]||'').trim() === 'P' && String(header[i+1]||'').trim() === 'R'){
      firstP = i;
      break;
    }
  }
  if(firstP < 0) throw new Error('Hoja Registro: no encontré sub-encabezados P/R.');
  const equipos = {};
  for(let r = headerIdx + 1; r < rows.length; r++){
    const row = rows[r];
    if(!row) continue;
    const inv = valNorm(row[invIdx]);
    if(!inv || inv === 'N/A') continue;
    const reg = {};
    for(let m = 0; m < 12; m++){
      const pv = valNorm(row[firstP + m*2]);
      const rv = valNorm(row[firstP + m*2 + 1]);
      if(pv || rv) reg[MESES[m]] = {P: pv || null, R: rv || null};
    }
    equipos[inv] = {inv, reg};
  }
  return equipos;
}

function compararMaestro(parsed, importacionId){
  const conflictosNuevos = [];
  const todos = new Set([...Object.keys(parsed.pmp), ...Object.keys(parsed.reg)]);
  const invsProg = new Set(state.equipos.map(e => e.inv));
  // Año del archivo extraído del nombre de la hoja (PMP_2026 / Registro_MP-2026)
  const yearMatch = (parsed.sheetPMP||parsed.sheetReg||'').match(/(\d{4})/);
  const year = yearMatch ? parseInt(yearMatch[1]) : new Date().getFullYear();
  let autoCompletados = 0;
  let eventosSinteticos = 0;

  // 1. Equipos nuevos: en maestro pero no en programa
  todos.forEach(inv => {
    if(!invsProg.has(inv)){
      // Verifica que no exista ya un conflicto equipo_nuevo abierto
      const existente = state.conflictos.find(c => c.tipo === 'equipo_nuevo' && c.inv === inv && c.estado === 'pendiente');
      if(existente){
        existente.importacionId = importacionId;
        existente.datosMaestro = {pmp: parsed.pmp[inv], reg: parsed.reg[inv]};
        return;
      }
      conflictosNuevos.push({
        id: state.counters.conflicto++,
        tipo: 'equipo_nuevo',
        inv,
        equipo: null,
        datosMaestro: {pmp: parsed.pmp[inv], reg: parsed.reg[inv]},
        estado: 'pendiente',
        fechaDeteccion: new Date().toISOString(),
        importacionId
      });
    }
  });

  // 2. Equipos faltantes en maestro
  invsProg.forEach(inv => {
    if(!todos.has(inv)){
      const eq = findEquipo(inv);
      if(eq && eq.estado === 'baja') return; // los dados de baja se sacan del maestro
      const existente = state.conflictos.find(c => c.tipo === 'equipo_faltante' && c.inv === inv && c.estado === 'pendiente');
      if(existente){ existente.importacionId = importacionId; return; }
      conflictosNuevos.push({
        id: state.counters.conflicto++,
        tipo: 'equipo_faltante',
        inv,
        equipo: eq ? eq.equipo : null,
        estado: 'pendiente',
        fechaDeteccion: new Date().toISOString(),
        importacionId
      });
    }
  });

  // 3. Diferencias por celda
  state.equipos.forEach(eq => {
    if(eq.estado === 'baja') return;
    const inv = eq.inv;
    const fromPMP = parsed.pmp[inv];
    const fromReg = parsed.reg[inv];

    // PMP: solo P (programación) en una hoja
    MESES.forEach(mes => {
      const valProg = valNorm(((eq.prog||{})[mes]) || '');
      const valMast = fromPMP ? valNorm(fromPMP.prog[mes] || '') : '';
      if(valProg === valMast) return;
      if(!fromPMP) return; // equipo no en hoja PMP del archivo
      // Auto-completar: vacío en programa + valor en maestro → escribir sin conflicto
      if(!valProg && valMast){
        eq.prog = eq.prog || {};
        eq.prog[mes] = valMast;
        autoCompletados++;
        return;
      }
      // Conflicto: valor diferente o el programa tiene dato y maestro vacío
      registrarOActualizarConflicto({
        tipo:'mp_diferencia', inv, equipo: eq.equipo,
        hoja:'PMP', mes, campo:'P', year,
        valorPrograma: valProg, valorMaestro: valMast,
        importacionId
      }, conflictosNuevos);
    });

    // Registro_MP: P y R
    MESES.forEach(mes => {
      const regProg = (eq.registro||{})[mes] || {};
      const regMast = (fromReg && fromReg.reg[mes]) || {};
      ['P','R'].forEach(campo => {
        const vp = valNorm(regProg[campo] || '');
        const vm = valNorm(regMast[campo] || '');
        if(vp === vm) return;
        if(!fromReg) return; // equipo no está en hoja Registro, ya se manejó como faltante
        // Auto-completar: vacío en programa + valor en maestro
        if(!vp && vm){
          eq.registro = eq.registro || {};
          eq.registro[mes] = eq.registro[mes] || {};
          eq.registro[mes][campo] = vm;
          autoCompletados++;
          // Si es R con valor MP del catálogo y no hay evento MP en ese mes, crear sintético
          if(campo === 'R' && RESULTADOS_MP.has(vm)){
            const mIdx = MES_NUM[mes];
            const yaExiste = state.eventos.some(ev =>
              ev.inv === eq.inv && !ev.anulado && ev.tipo === 'Mantención preventiva' &&
              ev.fecha && new Date(ev.fecha+'T00:00:00').getMonth() === mIdx &&
              ev.fecha.startsWith(String(year)));
            if(!yaExiste){
              const fecha = `${year}-${String(mIdx+1).padStart(2,'0')}-15`;
              const ev = {
                id: state.counters.evento++,
                inv: eq.inv, equipo: eq.equipo, servicio: eq.servicio, fam: eq.fam,
                tipo: 'Mantención preventiva',
                fecha, fechaReg: hoyLocal(),
                resultado: vm,
                ejecutor: getPref('ultimoEjecutor', null) || 'Personal externo',
                estado: estadoMPDesdeResultado(vm),
                obs: `[Conciliación auto] Importado desde maestro · Importación #${importacionId}`,
                oficial: 'No', anulado: false,
                origen: 'conciliacion_auto',
                creadoPor: 'Cristian',
                ts: new Date().toISOString()
              };
              state.eventos.push(ev);
              audit('evento', ev.id, 'creado_autocompletado', null, 'conciliacion');
              eventosSinteticos++;
            }
          }
          return;
        }
        // Conflicto: valores diferentes ambos con dato, o programa con dato y maestro vacío
        registrarOActualizarConflicto({
          tipo:'mp_diferencia', inv, equipo: eq.equipo,
          hoja:'Registro', mes, campo, year,
          valorPrograma: vp, valorMaestro: vm,
          importacionId
        }, conflictosNuevos);
      });
    });
  });

  state.conflictos.push(...conflictosNuevos);
  return {conflictos: conflictosNuevos.length, autoCompletados, eventosSinteticos};
}

function registrarOActualizarConflicto(data, buffer){
  // Si ya existe un conflicto pendiente para la misma celda, actualizamos.
  const existente = state.conflictos.find(c =>
    c.tipo==='mp_diferencia' && c.inv===data.inv && c.hoja===data.hoja &&
    c.mes===data.mes && c.campo===data.campo &&
    (c.estado === 'pendiente' || c.estado === 'pospuesto')
  );
  if(existente){
    existente.valorMaestro = data.valorMaestro;
    existente.valorPrograma = data.valorPrograma;
    existente.importacionId = data.importacionId;
    return;
  }
  buffer.push({
    id: state.counters.conflicto++,
    ...data,
    estado: 'pendiente',
    fechaDeteccion: new Date().toISOString()
  });
}

// Catálogo de resultados válidos para crear evento MP sintético desde Conciliación.
const RESULTADOS_MP = new Set(['Si','C1','C2','C3','C4','C5','C6','C7','C8','FS','NU','Baja','No']);

function resolverConflicto(c, accion, valorManual, opts){
  const skipSave = opts && opts.skipSave;
  const eq = findEquipo(c.inv);
  let eventoCreado = null;
  if(c.tipo === 'mp_diferencia'){
    if(accion === 'aceptar_maestro' || accion === 'manual'){
      const v = accion === 'manual' ? valorManual : c.valorMaestro;
      if(c.hoja === 'PMP'){
        eq.prog = eq.prog || {};
        if(v) eq.prog[c.mes] = v; else delete eq.prog[c.mes];
      } else {
        eq.registro = eq.registro || {};
        eq.registro[c.mes] = eq.registro[c.mes] || {};
        eq.registro[c.mes][c.campo] = v || null;
        if(!eq.registro[c.mes].P && !eq.registro[c.mes].R) delete eq.registro[c.mes];
      }
      c.resolucionValor = v;
      // Si aceptamos un resultado R con valor válido del catálogo MP → crear evento sintético
      if(c.hoja === 'Registro' && c.campo === 'R' && v && RESULTADOS_MP.has(v)){
        // Buscar si ya existe un evento MP no anulado en ese mes para no duplicar
        const mIdx = MES_NUM[c.mes];
        const yearStr = (c.year || new Date().getFullYear()).toString();
        const yaExiste = state.eventos.some(ev =>
          ev.inv === eq.inv && !ev.anulado && ev.tipo === 'Mantención preventiva' &&
          ev.fecha && new Date(ev.fecha+'T00:00:00').getMonth() === mIdx &&
          ev.fecha.startsWith(yearStr)
        );
        if(!yaExiste){
          const fecha = `${yearStr}-${String(mIdx+1).padStart(2,'0')}-15`;
          const ev = {
            id: state.counters.evento++,
            inv: eq.inv, equipo: eq.equipo, servicio: eq.servicio, fam: eq.fam,
            tipo: 'Mantención preventiva',
            fecha, fechaReg: hoyLocal(),
            resultado: v,
            ejecutor: getPref('ultimoEjecutor', null) || 'Personal externo',
            estado: estadoMPDesdeResultado(v),
            obs: `[Conciliación] Importado desde maestro · Importación #${c.importacionId||'-'}`,
            oficial: 'No',
            anulado: false,
            origen: 'conciliacion',
            creadoPor: 'Cristian',
            ts: new Date().toISOString(),
            conflictoOrigen: c.id
          };
          state.eventos.push(ev);
          aplicarEfectosEvento(ev);
          audit('evento', ev.id, 'creado_sintetico', null, 'conciliacion');
          eventoCreado = ev;
        }
      }
    }
    if(accion === 'mantener_programa'){
      c.resolucionValor = c.valorPrograma;
    }
    c.estado = accion === 'posponer' ? 'pospuesto' :
               accion === 'aceptar_maestro' ? 'resuelto_maestro' :
               accion === 'manual' ? 'resuelto_manual' :
               'resuelto_programa';
  } else if(c.tipo === 'equipo_nuevo'){
    if(accion === 'aceptar_maestro'){
      // Importar el equipo al programa
      const datos = c.datosMaestro || {};
      const nuevoEq = {
        inv: c.inv,
        equipo: '', // sin datos en maestro de identificación, el usuario completa después
        servicio:null, unidad:null, ubic:null, fam:null,
        marca:null, modelo:null, serie:null, ano:null, vur:null, clasif:null, freq:null,
        estado:'operativo', subestado:null,
        estadoDesde: hoyLocal(),
        prog: (datos.pmp && datos.pmp.prog) || {},
        registro: (datos.reg && datos.reg.reg) || {}
      };
      state.equipos.push(nuevoEq);
      audit('equipo', c.inv, 'alta_por_conciliacion', null, 'creado');
      c.estado = 'resuelto_maestro';
    } else if(accion === 'mantener_programa'){
      // Ignorar el equipo nuevo
      c.estado = 'resuelto_programa';
    } else if(accion === 'posponer'){
      c.estado = 'pospuesto';
    }
  } else if(c.tipo === 'equipo_faltante'){
    if(accion === 'aceptar_maestro'){
      // El maestro no lo tiene → dar de baja en el programa
      if(eq){
        eq.estado = 'baja';
        eq.estadoDesde = hoyLocal();
        audit('equipo', c.inv, 'baja_por_conciliacion', null, 'baja');
      }
      c.estado = 'resuelto_maestro';
    } else if(accion === 'mantener_programa'){
      c.estado = 'resuelto_programa';
    } else if(accion === 'posponer'){
      c.estado = 'pospuesto';
    }
  }
  c.fechaResolucion = new Date().toISOString();
  c.accionAplicada = accion;
  audit('conflicto', c.id, 'resolucion', 'pendiente', accion);

  // Actualizar contadores de la importación
  const imp = state.importaciones.find(i => i.id === c.importacionId);
  if(imp){
    imp.resueltos = (imp.resueltos || 0) + 1;
  }
  if(!skipSave){
    save();
    refreshNav();
  }
  return {eventoCreado};
}

function nombreCampoConflicto(c){
  if(c.tipo === 'mp_diferencia') return `${c.hoja} · ${c.mes} · columna ${c.campo}`;
  if(c.tipo === 'equipo_nuevo') return 'Equipo nuevo en maestro';
  if(c.tipo === 'equipo_faltante') return 'Equipo no aparece en maestro';
  return c.tipo;
}

//============== VISTA CONCILIACIÓN ==============
VIEWS.conciliacion = function(root, params){
  const drop = el('div',{class:'drop-zone',tabindex:'0'},
    el('strong',{},'Subir archivo maestro (.xlsm / .xlsx)'),
    el('small',{},'Click o arrastra el archivo aquí · No sobreescribe nada — genera la lista de diferencias por resolver.')
  );
  const fileInput = el('input',{type:'file',accept:'.xlsm,.xlsx',style:{display:'none'}});
  drop.onclick = ()=>fileInput.click();
  drop.ondragover = e => { e.preventDefault(); drop.classList.add('dragging'); };
  drop.ondragleave = ()=>drop.classList.remove('dragging');
  drop.ondrop = e => {
    e.preventDefault(); drop.classList.remove('dragging');
    if(e.dataTransfer.files[0]) procesar(e.dataTransfer.files[0]);
  };
  fileInput.onchange = e => { if(e.target.files[0]) procesar(e.target.files[0]); };

  const progressBox = el('div',{});
  const filtersBox = el('div',{class:'toolbar'});
  const histBox = el('div',{});
  const listBox = el('div',{});

  async function procesar(file){
    progressBox.innerHTML = '';
    const box = el('div',{class:'imp-progress'});
    progressBox.appendChild(box);
    box.appendChild(el('div',{class:'step'}, `Archivo: ${file.name} (${(file.size/1024).toFixed(1)} KB)`));
    // Hash SHA-256 para detectar duplicados
    const s0 = el('div',{class:'step'}, 'Calculando hash del archivo…'); box.appendChild(s0);
    let fileHash = null;
    try{
      const buf = await file.arrayBuffer();
      const hashBuf = await crypto.subtle.digest('SHA-256', buf);
      fileHash = Array.from(new Uint8Array(hashBuf)).map(b => b.toString(16).padStart(2,'0')).join('');
      s0.textContent = `✓ Hash: ${fileHash.slice(0,16)}…`;
      s0.classList.add('done');
      const dup = state.importaciones.find(i => i.hash === fileHash);
      if(dup){
        const fechaDup = new Date(dup.fecha).toLocaleString('es-CL');
        const msg = `Este archivo ya fue importado el ${fechaDup}.\n\n` +
                    `Generó ${dup.generados||0} conflictos · ${dup.resueltos||0} resueltos.\n\n` +
                    `¿Re-importar de todas formas? (Se recomienda cancelar si el contenido no cambió.)`;
        if(!confirm(msg)){
          box.appendChild(el('div',{class:'step error'}, '✗ Importación cancelada — archivo duplicado.'));
          return;
        }
      }
    } catch(e){
      s0.textContent = '⚠ Hash no calculado (continuando)';
      console.warn('hash failed', e);
    }
    const s1 = el('div',{class:'step'}, 'Parseando hojas…'); box.appendChild(s1);
    try{
      const parsed = await parsearMaestro(file);
      s1.textContent = `✓ Hojas: ${parsed.sheetPMP}, ${parsed.sheetReg}. ${Object.keys(parsed.pmp).length} eq. en PMP, ${Object.keys(parsed.reg).length} en Registro.`;
      s1.classList.add('done');
      const s2 = el('div',{class:'step'}, 'Comparando con el estado del programa…'); box.appendChild(s2);
      const importacion = {
        id: state.counters.importacion++,
        nombre: file.name,
        fecha: new Date().toISOString(),
        hash: fileHash,
        totalMaestro: new Set([...Object.keys(parsed.pmp),...Object.keys(parsed.reg)]).size,
        totalPrograma: state.equipos.length,
        generados: 0, resueltos: 0
      };
      const result = compararMaestro(parsed, importacion.id);
      importacion.generados = result.conflictos;
      importacion.autoCompletados = result.autoCompletados;
      importacion.eventosSinteticos = result.eventosSinteticos;
      state.importaciones.unshift(importacion);
      save();
      refreshNav();
      s2.textContent = `✓ Comparación completada.`;
      s2.classList.add('done');
      // Reporte de autocompletado
      if(result.autoCompletados > 0){
        const sAuto = el('div',{class:'step done'},
          `✓ Auto-completados: ${result.autoCompletados} celdas vacías del programa con datos del maestro` +
          (result.eventosSinteticos > 0 ? ` (${result.eventosSinteticos} eventos sintéticos en bitácora)` : '')
        );
        box.appendChild(sAuto);
      }
      const s3 = el('div',{class:'step done'}, result.conflictos === 0
        ? '✓ Sin conflictos — celdas con valores diferentes no se encontraron.'
        : `→ ${result.conflictos} conflictos pendientes (valores diferentes) en la lista de abajo.`);
      box.appendChild(s3);
      render();
    } catch(err){
      box.appendChild(el('div',{class:'step error'}, '✗ Error: '+err.message));
      console.error(err);
    }
  }

  const selTipo = el('select',{},
    el('option',{value:''},'Todos los tipos'),
    el('option',{value:'mp_diferencia'},'Diferencia MP'),
    el('option',{value:'equipo_nuevo'},'Equipo nuevo'),
    el('option',{value:'equipo_faltante'},'Equipo faltante')
  );
  const selEstado = el('select',{},
    el('option',{value:''},'Pendientes y pospuestos'),
    el('option',{value:'pendiente'},'Solo pendientes'),
    el('option',{value:'pospuesto'},'Solo pospuestos'),
    el('option',{value:'resuelto'},'Resueltos (historial)'),
    el('option',{value:'todos'},'Todos')
  );
  const searchConf = el('input',{type:'search',placeholder:'Buscar por inv, mes, valor…'});
  const selAgrupar = el('select',{},
    el('option',{value:''},'Sin agrupar'),
    el('option',{value:'tipo'},'Agrupar por: Tipo + hoja + campo'),
    el('option',{value:'servicio'},'Agrupar por: Servicio'),
    el('option',{value:'equipo'},'Agrupar por: Equipo')
  );

  // Selección masiva
  const seleccion = new Set();
  const bulkBar = el('div',{class:'bulk-bar', style:{display:'none'}});
  let listaVisible = []; // referencia a la última lista filtrada para "seleccionar todos"

  function renderBulkBar(){
    bulkBar.innerHTML = '';
    if(seleccion.size === 0){
      bulkBar.style.display = 'none';
      return;
    }
    bulkBar.style.display = 'flex';
    bulkBar.appendChild(el('span',{class:'bulk-count'},
      `${seleccion.size} seleccionado${seleccion.size>1?'s':''}`));
    bulkBar.appendChild(el('button',{class:'small',onclick:()=>{seleccion.clear();render();}},'Limpiar selección'));
    bulkBar.appendChild(el('div',{style:{flex:'1'}}));
    bulkBar.appendChild(el('button',{class:'small primary',onclick:()=>aplicarBulk('aceptar_maestro')},'✓ Aceptar maestro a todos'));
    bulkBar.appendChild(el('button',{class:'small',onclick:()=>aplicarBulk('mantener_programa')},'✗ Mantener programa en todos'));
    bulkBar.appendChild(el('button',{class:'small ghost',onclick:()=>aplicarBulk('posponer')},'⏸ Posponer todos'));
  }

  function aplicarBulk(accion){
    if(seleccion.size > 50){
      if(!confirm(`Vas a aplicar "${accion}" a ${seleccion.size} conflictos. Esta acción NO se puede deshacer en lote. ¿Continuar?`)) return;
    }
    const ids = [...seleccion];
    let aplicados = 0, eventosSinteticos = 0;
    ids.forEach(id => {
      const c = state.conflictos.find(x => x.id === id);
      if(!c) return;
      if(c.estado !== 'pendiente' && c.estado !== 'pospuesto') return;
      const r = resolverConflicto(c, accion, null, {skipSave:true});
      aplicados++;
      if(r && r.eventoCreado) eventosSinteticos++;
    });
    seleccion.clear();
    save();
    refreshNav();
    const detalle = eventosSinteticos > 0
      ? `${aplicados} resueltos · ${eventosSinteticos} evento${eventosSinteticos>1?'s':''} sintético${eventosSinteticos>1?'s':''} creado${eventosSinteticos>1?'s':''} en bitácora`
      : `${aplicados} resueltos`;
    toast(detalle, 'success');
    render();
  }

  function render(){
    // Historial
    histBox.innerHTML = '';
    if(state.importaciones.length === 0){
      histBox.appendChild(el('div',{class:'empty small',style:{marginBottom:'18px'}},'Aún no has subido ningún archivo maestro.'));
    } else {
      histBox.appendChild(el('h3',{},'Historial de importaciones'));
      const grid = el('div',{class:'imp-history'});
      state.importaciones.slice(0,4).forEach(imp => {
        const pend = (imp.generados||0) - (imp.resueltos||0);
        grid.appendChild(el('div',{class:'imp-card'},
          el('div',{class:'name'}, imp.nombre),
          el('div',{class:'date'}, new Date(imp.fecha).toLocaleString('es-CL')),
          el('div',{class:'nums'},
            el('span',{},el('span',{class:'n'},String(imp.generados||0)),el('small',{},' Conflictos')),
            el('span',{},el('span',{class:'n',style:imp.autoCompletados>0?{color:'var(--op)'}:{}},String(imp.autoCompletados||0)),el('small',{},' Auto-completados')),
            el('span',{},el('span',{class:'n'},String(imp.resueltos||0)),el('small',{},' Resueltos')),
            el('span',{},el('span',{class:'n',style:pend>0?{color:'var(--noop)'}:{}},String(pend)),el('small',{},' Pendientes'))
          )
        ));
      });
      histBox.appendChild(grid);
    }

    // Lista de conflictos
    const t = selTipo.value, e = selEstado.value, q = searchConf.value.trim().toLowerCase();
    let lista = state.conflictos.slice();
    if(t) lista = lista.filter(c => c.tipo === t);
    if(!e || e === '' ){
      lista = lista.filter(c => c.estado === 'pendiente' || c.estado === 'pospuesto');
    } else if(e === 'pendiente' || e === 'pospuesto'){
      lista = lista.filter(c => c.estado === e);
    } else if(e === 'resuelto'){
      lista = lista.filter(c => c.estado && c.estado.startsWith('resuelto'));
    }
    if(q){
      lista = lista.filter(c => JSON.stringify(c).toLowerCase().includes(q));
    }
    // Ordenar: pendientes primero, luego pospuestos, luego resueltos. Dentro: por fecha desc.
    lista.sort((a,b) => {
      const order = {pendiente:0, pospuesto:1, resuelto_maestro:2, resuelto_programa:2, resuelto_manual:2};
      const oa = order[a.estado] != null ? order[a.estado] : 3;
      const ob = order[b.estado] != null ? order[b.estado] : 3;
      if(oa !== ob) return oa - ob;
      return (b.fechaDeteccion||'').localeCompare(a.fechaDeteccion||'');
    });

    listBox.innerHTML = '';
    listaVisible = lista;
    const head = el('div',{style:{display:'flex',justifyContent:'space-between',alignItems:'center',gap:'12px',flexWrap:'wrap'}},
      el('h3',{style:{margin:0}}, `Por resolver ${lista.length>0 ? '· '+lista.length+' conflictos' : ''}`),
      lista.length > 0 ? el('div',{style:{display:'flex',gap:'6px',alignItems:'center'}},
        el('button',{class:'small',onclick:()=>{
          lista.filter(c => c.estado === 'pendiente' || c.estado === 'pospuesto').forEach(c => seleccion.add(c.id));
          render();
        }},'Seleccionar todos los visibles'),
        el('small',{class:'muted'}, lista.filter(c => c.estado === 'pendiente' || c.estado === 'pospuesto').length+' resolubles')
      ) : null
    );
    listBox.appendChild(head);
    renderBulkBar();
    if(lista.length === 0){
      listBox.appendChild(el('div',{class:'empty small'}, state.conflictos.length === 0 ? 'No hay conflictos.' : 'Sin conflictos con los filtros actuales.'));
      return;
    }

    const modoAgrup = selAgrupar.value;
    if(!modoAgrup){
      lista.forEach(c => listBox.appendChild(renderConflictoConCheckbox(c, render, seleccion)));
      return;
    }

    // Agrupar
    const claveDe = (c) => {
      if(modoAgrup === 'tipo'){
        if(c.tipo === 'mp_diferencia') return `${c.tipo} · ${c.hoja||'-'} · ${c.campo||'-'}`;
        return c.tipo;
      }
      if(modoAgrup === 'servicio'){
        const eq = findEquipo(c.inv);
        return eq && eq.servicio ? eq.servicio : '(sin servicio)';
      }
      if(modoAgrup === 'equipo'){
        const eq = findEquipo(c.inv);
        return `${c.inv} · ${eq?eq.equipo:'?'}`;
      }
      return 'Otros';
    };
    const grupos = new Map();
    lista.forEach(c => {
      const k = claveDe(c);
      if(!grupos.has(k)) grupos.set(k, []);
      grupos.get(k).push(c);
    });
    // Ordenar grupos por cantidad descendente
    const gruposOrd = [...grupos.entries()].sort((a,b)=>b[1].length - a[1].length);
    gruposOrd.forEach(([clave, items]) => {
      const resolubles = items.filter(c => c.estado === 'pendiente' || c.estado === 'pospuesto');
      const groupBox = el('div',{class:'conf-group'});
      const expanded = {value: items.length <= 10}; // los grupos chicos parten expandidos
      const header = el('div',{class:'conf-group-hd'});
      const renderGroup = ()=>{
        header.innerHTML = '';
        header.appendChild(el('span',{class:'tw',onclick:()=>{expanded.value=!expanded.value;renderGroup();}}, expanded.value?'▼':'▶'));
        header.appendChild(el('span',{class:'lbl',onclick:()=>{expanded.value=!expanded.value;renderGroup();}}, clave));
        header.appendChild(el('span',{class:'cnt'}, `${items.length} · ${resolubles.length} resolubles`));
        const acts = el('span',{class:'acts'});
        if(resolubles.length > 0){
          acts.appendChild(el('button',{class:'small primary',onclick:e=>{e.stopPropagation();aplicarGrupo(resolubles, 'aceptar_maestro', clave);}}, '✓ Aceptar maestro al grupo'));
          acts.appendChild(el('button',{class:'small',onclick:e=>{e.stopPropagation();aplicarGrupo(resolubles, 'mantener_programa', clave);}}, '✗ Mantener programa al grupo'));
          acts.appendChild(el('button',{class:'small',onclick:e=>{e.stopPropagation();resolubles.forEach(c => seleccion.add(c.id));render();}}, '+ Sel. grupo'));
        }
        header.appendChild(acts);
        // body
        if(groupBox.querySelector('.conf-group-bd')) groupBox.querySelector('.conf-group-bd').remove();
        if(expanded.value){
          const body = el('div',{class:'conf-group-bd'});
          items.forEach(c => body.appendChild(renderConflictoConCheckbox(c, render, seleccion)));
          groupBox.appendChild(body);
        }
      };
      groupBox.appendChild(header);
      renderGroup();
      listBox.appendChild(groupBox);
    });
  }

  function aplicarGrupo(items, accion, claveGrupo){
    if(items.length > 20){
      if(!confirm(`Vas a aplicar "${accion}" a ${items.length} conflictos del grupo "${claveGrupo}". ¿Continuar?`)) return;
    }
    let aplicados = 0, eventosSint = 0;
    items.forEach(c => {
      const r = resolverConflicto(c, accion, null, {skipSave:true});
      aplicados++;
      if(r && r.eventoCreado) eventosSint++;
    });
    save();
    refreshNav();
    const det = eventosSint > 0 ? `${aplicados} resueltos · ${eventosSint} eventos sintéticos creados` : `${aplicados} resueltos`;
    toast(`Grupo "${claveGrupo}": ${det}`, 'success');
    render();
  }

  filtersBox.appendChild(el('div',{class:'grow'}, searchConf));
  filtersBox.appendChild(selTipo);
  filtersBox.appendChild(selEstado);
  filtersBox.appendChild(selAgrupar);
  [selTipo, selEstado, selAgrupar, searchConf].forEach(x => x.addEventListener('input', render));

  root.appendChild(el('div',{class:'view'},
    el('h2',{},'Conciliación'),
    el('div',{class:'subtitle'},'Sube el archivo maestro y revisa diferencias contra lo que tiene el programa. Tú decides cuál fuente es la correcta — nada se sobreescribe sin tu confirmación.'),
    drop, fileInput,
    progressBox,
    histBox,
    el('h3',{},'Filtros'),
    filtersBox,
    bulkBar,
    listBox
  ));
  render();
};

function renderConflictoConCheckbox(c, onChange, seleccion){
  const wrapper = el('div',{class:'conf-row'});
  const resoluble = c.estado === 'pendiente' || c.estado === 'pospuesto';
  if(resoluble){
    const cb = el('input',{type:'checkbox', checked: seleccion.has(c.id) ? 'checked' : false, onchange:e=>{
      if(e.target.checked) seleccion.add(c.id);
      else seleccion.delete(c.id);
      onChange();
    }});
    cb.checked = seleccion.has(c.id);
    const cbWrap = el('div',{class:'conf-checkbox'}, cb);
    wrapper.appendChild(cbWrap);
  } else {
    wrapper.appendChild(el('div',{class:'conf-checkbox'}, el('span',{class:'muted',style:{fontSize:'11px'}},'✓')));
  }
  wrapper.appendChild(renderConflicto(c, onChange));
  return wrapper;
}

function renderConflicto(c, onChange){
  const eq = findEquipo(c.inv);
  const cls = c.tipo === 'equipo_nuevo' ? 'altas' :
              c.tipo === 'equipo_faltante' ? 'faltante' :
              c.estado === 'pospuesto' ? '' : 'urgent';
  const card = el('div',{class:'conf-card '+cls});

  card.appendChild(el('div',{class:'hd'},
    el('div',{},
      el('div',{class:'title'},
        c.inv,
        eq ? ' · '+eq.equipo : '',
        ' · ', nombreCampoConflicto(c)
      ),
      el('div',{class:'meta'},
        eq ? (eq.servicio||'')+' · '+(eq.ubic||'') : '',
        ' · Detectado: ', new Date(c.fechaDeteccion).toLocaleString('es-CL')
      )
    ),
    el('div',{},
      el('span',{class:'badge '+(c.estado==='pendiente'?'noop':c.estado==='pospuesto'?'st':'op')}, estadoConflictoLabel(c.estado))
    )
  ));

  if(c.tipo === 'mp_diferencia'){
    card.appendChild(el('div',{class:'conf-diff'},
      el('div',{class:'prog'},
        el('div',{class:'lbl'},'En el programa'),
        el('div',{class:c.valorPrograma?'val':'val empty'}, c.valorPrograma || 'sin valor')
      ),
      el('div',{class:'mast'},
        el('div',{class:'lbl'},'En el maestro (Excel)'),
        el('div',{class:c.valorMaestro?'val':'val empty'}, c.valorMaestro || 'sin valor')
      )
    ));
  } else if(c.tipo === 'equipo_nuevo'){
    const ms = c.datosMaestro || {};
    const progStr = ms.pmp && ms.pmp.prog ? Object.entries(ms.pmp.prog).map(([m,v])=>`${m}=${v}`).join(' · ') : 'sin programación';
    const regStr = ms.reg && ms.reg.reg ? Object.entries(ms.reg.reg).map(([m,o])=>`${m}=${o.P||''}/${o.R||''}`).join(' · ') : 'sin registro';
    card.appendChild(el('div',{style:{fontSize:'12px',color:'var(--muted)',padding:'6px 0'}},
      el('div',{},el('strong',{},'Programación maestro: '), progStr),
      el('div',{},el('strong',{},'Registro maestro: '), regStr)
    ));
  } else if(c.tipo === 'equipo_faltante'){
    card.appendChild(el('div',{style:{fontSize:'13px',padding:'6px 0'}}, 'El programa tiene este equipo pero ya no aparece en el maestro. ¿Lo damos de baja?'));
  }

  if(c.estado === 'pendiente' || c.estado === 'pospuesto'){
    const actions = el('div',{class:'conf-actions'});
    if(c.tipo === 'mp_diferencia'){
      actions.appendChild(el('button',{class:'primary small',onclick:()=>{resolverConflicto(c,'aceptar_maestro');onChange();}},'✓ Aceptar maestro'));
      actions.appendChild(el('button',{class:'small',onclick:()=>{resolverConflicto(c,'mantener_programa');onChange();}},'✗ Mantener programa'));
      actions.appendChild(el('button',{class:'small',onclick:()=>{
        const v = prompt('Valor manual a guardar (ej. Si, C1, FS, dejar vacío para borrar):', c.valorMaestro || c.valorPrograma || '');
        if(v === null) return;
        resolverConflicto(c,'manual',v.trim());
        onChange();
      }},'✏ Editar manualmente'));
    } else if(c.tipo === 'equipo_nuevo'){
      actions.appendChild(el('button',{class:'primary small',onclick:()=>{resolverConflicto(c,'aceptar_maestro');onChange();}},'+ Agregar al programa'));
      actions.appendChild(el('button',{class:'small',onclick:()=>{resolverConflicto(c,'mantener_programa');onChange();}},'Ignorar'));
    } else if(c.tipo === 'equipo_faltante'){
      actions.appendChild(el('button',{class:'danger small',onclick:()=>{resolverConflicto(c,'aceptar_maestro');onChange();}},'Dar de baja'));
      actions.appendChild(el('button',{class:'small',onclick:()=>{resolverConflicto(c,'mantener_programa');onChange();}},'Mantener en programa'));
    }
    if(c.estado !== 'pospuesto'){
      actions.appendChild(el('button',{class:'small ghost',onclick:()=>{resolverConflicto(c,'posponer');onChange();}},'⏸ Posponer'));
    }
    if(eq){
      actions.appendChild(el('button',{class:'small ghost',onclick:()=>navigate('equipo',{inv:c.inv})},'Ver ficha →'));
    }
    card.appendChild(actions);
  } else {
    card.appendChild(el('div',{class:'ctx'},
      'Resuelto: ', estadoConflictoLabel(c.estado),
      c.resolucionValor != null ? ' → valor final: '+(c.resolucionValor || '(vacío)') : '',
      c.fechaResolucion ? ' · '+new Date(c.fechaResolucion).toLocaleString('es-CL') : ''
    ));
  }
  return card;
}

function estadoConflictoLabel(e){
  return {pendiente:'Pendiente', pospuesto:'Pospuesto', resuelto_maestro:'Aceptado maestro', resuelto_programa:'Mantenido programa', resuelto_manual:'Resuelto manual'}[e] || e;
}

//==============================================================
// MP RÁPIDA — modal mínimo (4 campos), recuerda último ejecutor y resultado
//==============================================================
// Sugiere día 5 del mes seleccionado (patrón observado: registras MPs del mes anterior).
function fechaSugeridaMP(year, monthIdx){
  return `${year}-${String(monthIdx+1).padStart(2,'0')}-05`;
}

// Registro masivo de MPs sobre varios equipos.
function mpMasiva(invs, year, monthIdx, refresh){
  if(!invs || invs.length === 0) return;
  const fecha = el('input',{type:'date', value: fechaSugeridaMP(year, monthIdx)});
  const resultado = el('select',{}, ...['Si','C1','C2','C3','C4','C5','C6','C7','C8','FS','Baja','NU','No'].map(x=>el('option',{value:x},x)));
  resultado.value = getPref('ultimoResultadoMP','Si');
  const ejecutor = el('select',{}, el('option',{value:''},'—'), ...EJECUTORES.map(x=>el('option',{value:x},x)));
  ejecutor.value = getPref('ultimoEjecutor','');
  const obs = el('textarea',{placeholder:'Observación común a todos los registros (opcional)'});
  const omitirDup = el('input',{type:'checkbox',checked:'checked'});
  function guardar(){
    if(!fecha.value){ toast('Fecha requerida','error'); return; }
    if(!ejecutor.value){ toast('Selecciona ejecutor','error'); return; }
    let creados = 0, omitidos = 0, errores = [];
    const yy = parseInt(fecha.value.slice(0,4));
    const mm = parseInt(fecha.value.slice(5,7))-1;
    invs.forEach(inv => {
      const eq = findEquipo(inv);
      if(!eq){ errores.push(inv+': no encontrado'); return; }
      // Omitir si ya tiene MP no anulada en ese mes
      if(omitirDup.checked && state.eventos.some(e =>
        e.inv === inv && !e.anulado && e.tipo === 'Mantención preventiva' && e.fecha &&
        e.fecha.startsWith(`${yy}-${String(mm+1).padStart(2,'0')}`))){
        omitidos++;
        return;
      }
      const ev = {
        id: state.counters.evento++,
        inv, equipo: eq.equipo, servicio: eq.servicio, fam: eq.fam,
        tipo: 'Mantención preventiva',
        fecha: fecha.value, fechaReg: hoyLocal(),
        resultado: resultado.value,
        ejecutor: ejecutor.value,
        estado: estadoMPDesdeResultado(resultado.value),
        obs: obs.value || null,
        oficial: 'No',
        anulado: false,
        creadoPor: 'Cristian',
        origen: 'masivo',
        ts: new Date().toISOString()
      };
      state.eventos.push(ev);
      aplicarEfectosEvento(ev);
      audit('evento', ev.id, 'creado', null, 'MP masiva');
      creados++;
    });
    setPref('ultimoEjecutor', ejecutor.value);
    setPref('ultimoResultadoMP', resultado.value);
    save();
    closeModal();
    let msg = `${creados} MP registradas`;
    if(omitidos > 0) msg += ` · ${omitidos} omitidas (ya tenían MP en el mes)`;
    if(errores.length > 0) msg += ` · ${errores.length} errores`;
    toast(msg, 'success');
    if(refresh) refresh();
  }
  modal({title:`Registrar MP a ${invs.length} equipos`, wide:true,
    hasUnsavedData: ()=> obs.value.trim() !== '',
    body: el('div',{},
      el('div',{class:'notice info'},
        `Se registrará una Mantención Preventiva con los mismos datos a los ${invs.length} equipos seleccionados.`
      ),
      el('div',{class:'grid-2'},
        formField('Fecha de la MP', fecha),
        formField('Resultado', resultado)
      ),
      formField('Ejecutor', ejecutor),
      formField('Observación común (opcional)', obs),
      el('label',{style:{display:'flex',alignItems:'center',gap:'8px',marginTop:'10px',fontSize:'13px',textTransform:'none',letterSpacing:'0'}},
        omitirDup, 'Omitir equipos que ya tienen MP registrada en el mes (evita duplicados)'
      ),
      el('div',{class:'eq-info-card',style:{marginTop:'14px'}},
        el('div',{class:'eq-info-lbl'}, 'Equipos seleccionados ('+invs.length+')'),
        el('div',{style:{fontSize:'12px',color:'var(--muted)',maxHeight:'120px',overflow:'auto',marginTop:'6px'}},
          invs.slice(0,30).map(i => {
            const e = findEquipo(i);
            return el('div',{}, `${i} · ${e?e.equipo:'?'} · ${e?e.servicio:'?'}`);
          }),
          invs.length > 30 ? el('div',{style:{fontStyle:'italic'}}, `… y ${invs.length-30} más`) : null
        )
      )
    ),
    footer: [
      el('button',{onclick:closeModal},'Cancelar'),
      el('button',{class:'primary',onclick:guardar}, `✓ Registrar MP a ${invs.length} equipos`)
    ]
  });
  setTimeout(()=>ejecutor.value ? resultado.focus() : ejecutor.focus(), 80);
}

function mpRapida(opts){
  const eq = findEquipo(opts.invDefault);
  if(!eq){ toast('Equipo no encontrado','error'); return; }

  const fecha = el('input',{type:'date', value: opts.fechaDefault || hoyLocal()});
  const resultado = el('select',{},
    ...['Si','C1','C2','C3','C4','C5','C6','C7','C8','FS','Baja','NU','No'].map(x =>
      el('option',{value:x, selected: x === getPref('ultimoResultadoMP','Si') ? 'selected' : false}, x))
  );
  resultado.value = getPref('ultimoResultadoMP','Si');
  const ejecutor = el('select',{},
    el('option',{value:''},'—'),
    ...EJECUTORES.map(x => el('option',{value:x, selected: x === getPref('ultimoEjecutor','') ? 'selected' : false}, x))
  );
  ejecutor.value = getPref('ultimoEjecutor','');
  const obs = el('textarea',{placeholder:'Observación (opcional)'});

  function guardar(continuar){
    if(!fecha.value){ toast('Fecha requerida','error'); return; }
    if(!ejecutor.value){ toast('Selecciona ejecutor','error'); return; }
    // Alerta si la fecha cae en un mes sin programación MP
    const [yy, mm] = fecha.value.split('-').map(Number);
    const mesActual = MESES[mm-1];
    const codigoP = (eq.prog || {})[mesActual];
    if(!codigoP || !['X','R','RA','PM'].includes(codigoP)){
      const mesesProg = MESES.filter(m => ['X','R','RA','PM'].includes((eq.prog||{})[m]));
      const aviso = `Este equipo NO tiene MP programada en ${mesActual} ${yy}.\n\n` +
        (mesesProg.length > 0
          ? `Meses programados (${eq.freq||'sin frecuencia'}): ${mesesProg.join(', ')}.\n\n`
          : 'No tiene programación MP definida en la matriz.\n\n') +
        '¿Registrar igual?';
      if(!confirm(aviso)) return;
    }
    const ev = {
      id: state.counters.evento++,
      inv: eq.inv, equipo: eq.equipo, servicio: eq.servicio, fam: eq.fam,
      tipo: 'Mantención preventiva',
      fecha: fecha.value, fechaReg: hoyLocal(),
      resultado: resultado.value,
      ejecutor: ejecutor.value,
      estado: estadoMPDesdeResultado(resultado.value),
      obs: obs.value || null,
      oficial: 'No',
      anulado: false,
      creadoPor: 'Cristian',
      ts: new Date().toISOString()
    };
    state.eventos.push(ev);
    aplicarEfectosEvento(ev);
    audit('evento', ev.id, 'creado', null, 'MP rápida');
    setPref('ultimoEjecutor', ejecutor.value);
    setPref('ultimoResultadoMP', resultado.value);
    save();
    closeModal();
    toast(`MP registrada · ${eq.inv} · ${fmtFecha(ev.fecha)} · ${ev.resultado}`, 'success',
      {label:'Ver', fn:()=>navigate('equipo',{inv:eq.inv})});
    if(continuar){
      // Mantiene el flujo: vuelve a Equipos para registrar la siguiente
      navigate('equipos');
    } else if(currentView === 'equipo'){
      navigate('equipo',{inv:eq.inv});
    } else {
      navigate(currentView, viewParams);
    }
  }

  const valoresIniciales = {
    fecha: fecha.value, resultado: resultado.value,
    ejecutor: ejecutor.value, obs: ''
  };
  function hasUnsavedData(){
    return obs.value.trim() !== '' ||
           fecha.value !== valoresIniciales.fecha ||
           ejecutor.value !== valoresIniciales.ejecutor ||
           resultado.value !== valoresIniciales.resultado;
  }
  modal({title:`MP rápida · ${eq.inv} · ${eq.equipo}`, hasUnsavedData, body: el('div',{},
    el('div',{class:'eq-info-card'},
      el('div',{class:'eq-info-hd'},
        el('strong',{}, eq.equipo||'—'),
        el('span',{class:'eq-info-inv'}, ' · '+eq.inv),
        badgeEstado(eq.estado),
        conflictosDe(eq.inv).length > 0 ? el('span',{class:'badge noop conflict-badge', title:'Conflictos pendientes con maestro', onclick:()=>{closeModal();navigate('equipo',{inv:eq.inv, openTab:'conflictos'});}}, conflictosDe(eq.inv).length+' conflicto'+(conflictosDe(eq.inv).length>1?'s':'')) : null
      ),
      el('div',{class:'eq-info-grid'},
        eqInfoCell('N° Carpeta', eq.carpeta),
        eqInfoCell('Serie', eq.serie),
        eqInfoCell('Marca', eq.marca),
        eqInfoCell('Modelo', eq.modelo),
        eqInfoCell('Servicio', eq.servicio),
        eqInfoCell('Unidad', eq.unidad),
        eqInfoCell('Ubicación', eq.ubic),
        eqInfoCell('Frecuencia MP', eq.freq)
      )
    ),
    el('div',{class:'grid-2'},
      formField('Fecha de la MP', fecha),
      formField('Resultado', resultado)
    ),
    formField('Ejecutor', ejecutor),
    formField('Observación', obs),
    el('div',{class:'notice info',style:{marginTop:'14px'}},
      'Se guardará como borrador. Recuerda el último ejecutor y resultado para los siguientes registros.')
  ), footer:[
    el('button',{onclick:closeModal},'Cancelar'),
    el('button',{onclick:()=>guardar(true), class:'primary'},'Guardar y siguiente'),
    el('button',{class:'primary',onclick:()=>guardar(false)},'Guardar')
  ]});
  // Autofocus reforzado: prioriza el primer campo vacío en este orden
  setTimeout(()=>{
    if(!fecha.value) fecha.focus();
    else if(!ejecutor.value) ejecutor.focus();
    else obs.focus();
  }, 80);
}

//==============================================================
// FORMULARIO EVENTO
//==============================================================
// Campo "Folio SIGEM" del ciclo correctivo. Con ciclos abiertos: lista preseleccionada
// en el ciclo abierto (para que el folio "se cargue" solo); sin ciclos: casilla manual.
function folioCicloControl(ciclosAb){
  if(!ciclosAb.length) return el('input',{type:'text',placeholder:'Folio SIGEM (sin ciclo abierto)'});
  const sel = el('select',{},
    ...ciclosAb.map(c=>el('option',{value:c.folio}, c.folio)),
    el('option',{value:''},'— sin vincular —')
  );
  sel.value = ciclosAb[0].folio;
  return sel;
}
// Aviso para eventos de cierre (Reparación / Recepción) cuando no hay ciclo abierto.
function avisoSinCicloAbierto(){
  return el('div',{class:'notice warn'},
    'Este equipo no tiene un ciclo correctivo abierto. Normalmente esto se vincula a una ' +
    'Solicitud de trabajo abierta: revisa si fue anulada o ya cerrada. Si igual necesitas ' +
    'registrarlo, escribe el folio a mano.');
}
function nuevoEvento(opts){
  let tipo = opts.tipoDefault || null;
  let invSel = opts.invDefault || '';
  const eqList = state.equipos.slice().sort((a,b)=>a.inv.localeCompare(b.inv));

  function build(){
    const eq = invSel ? findEquipo(invSel) : null;
    const ciclosAb = invSel ? ciclosAbiertosDe(invSel) : [];

    // Selector de equipo
    const invInput = el('input',{type:'text',list:'eq-list',value:invSel,placeholder:'N° Inventario',oninput:e=>{invSel=e.target.value;if(findEquipo(invSel)){rebuild();}}});
    const dataList = el('datalist',{id:'eq-list'}, ...eqList.slice(0,200).map(e=>el('option',{value:e.inv}, `${e.inv} — ${e.equipo} (${e.servicio||''})`)));

    // Selector de tipo (tarjetas)
    const tipoGrid = el('div',{class:'event-type-grid'}, ...TIPOS_EVENTO.map(t =>
      el('button',{class:'',onclick:()=>{tipo=t.label;rebuild();}},
        el('strong',{},t.label), el('small',{},t.desc)
      )
    ));
    if(tipo){
      tipoGrid.querySelectorAll('button').forEach((b,i)=>{
        if(TIPOS_EVENTO[i].label === tipo) b.classList.add('selected');
      });
    }

    // Campos según tipo
    const campos = el('div',{});
    if(tipo){
      const today = hoyLocal();
      const fecha = el('input',{type:'date',value:opts.fechaDefault||today});
      const obs = el('textarea',{placeholder:'Observación / descripción / informe…'});
      const ejecutor = el('select',{}, el('option',{value:''},'—'), ...EJECUTORES.map(x=>el('option',{value:x},x)));
      const oficial = el('select',{}, el('option',{value:'No'},'Borrador (No oficial)'), el('option',{value:'Sí'},'Oficial'));

      let extra = {};
      if(tipo === 'Solicitud de trabajo'){
        const folio = el('input',{type:'text',placeholder:'2025-NNNNNN-NN-NNNNN (déjalo vacío para auto)'});
        extra = {folio};
        campos.appendChild(el('div',{class:'grid-2'},
          formField('Fecha de solicitud',fecha), formField('Ejecutor asignado',ejecutor),
          formField('Folio SIGEM',folio), formField('Oficial',oficial)
        ));
        campos.appendChild(formField('Descripción de la falla',obs));
        campos.appendChild(el('div',{class:'notice info'},'Al guardar se abrirá automáticamente un Ciclo correctivo y el equipo pasará a "no operativo".'));
      } else if(tipo === 'Visita técnica'){
        const empresa = el('input',{type:'text'});
        const tecnico = el('input',{type:'text'});
        const tipoVisita = el('select',{}, el('option',{value:'diagnóstica'},'Diagnóstica'),el('option',{value:'correctiva'},'Correctiva'));
        const folio = folioCicloControl(ciclosAb);
        const estado = el('select',{}, ...['no operativo','operativo','en servicio técnico'].map(s=>el('option',{value:s},s)));
        extra = {empresa,tecnico,tipoVisita,folio,estado};
        campos.appendChild(el('div',{class:'grid-3'},
          formField('Fecha',fecha), formField('Empresa',empresa), formField('Técnico',tecnico)
        ));
        campos.appendChild(el('div',{class:'grid-3'},
          formField('Tipo de visita',tipoVisita), formField('Vincular a Folio SIGEM',folio), formField('Estado resultante',estado)
        ));
        campos.appendChild(formField('Informe / Observación',obs));
        campos.appendChild(formField('Oficial',oficial));
      } else if(tipo === 'Orden de Compra'){
        const nCotiz = el('input',{type:'text'});
        const nOC = el('input',{type:'text'});
        const empresa = el('input',{type:'text'});
        const via = el('select',{},el('option',{value:'trato_directo'},'Trato directo'),el('option',{value:'compra_agil'},'Compra ágil'));
        const folioInf = el('input',{type:'text',placeholder:'Solo si trato directo'});
        const folio = folioCicloControl(ciclosAb);
        extra = {nCotiz,nOC,empresa,via,folioInf,folio};
        campos.appendChild(el('div',{class:'grid-3'},
          formField('Fecha',fecha), formField('N° Cotización',nCotiz), formField('N° OC',nOC)
        ));
        campos.appendChild(el('div',{class:'grid-3'},
          formField('Empresa',empresa), formField('Vía',via), formField('Folio informe (TD)',folioInf)
        ));
        campos.appendChild(el('div',{class:'grid-2'},
          formField('Vincular a Folio SIGEM',folio), formField('Oficial',oficial)
        ));
        campos.appendChild(formField('Observación',obs));
      } else if(tipo === 'Envío a servicio técnico'){
        const nEnvio = el('input',{type:'text',placeholder:'Correlativo'});
        const empresa = el('input',{type:'text'});
        const folio = folioCicloControl(ciclosAb);
        extra = {nEnvio,empresa,folio};
        const estadoFixed = el('input',{value:'en servicio técnico',readonly:true});
        campos.appendChild(el('div',{class:'grid-3'},
          formField('Fecha de envío',fecha), formField('N° de envío',nEnvio), formField('Empresa',empresa)
        ));
        campos.appendChild(el('div',{class:'grid-3'},
          formField('Ejecutor',ejecutor), formField('Folio SIGEM',folio), formField('Estado resultante',estadoFixed)
        ));
        campos.appendChild(formField('Observación',obs));
        campos.appendChild(formField('Oficial',oficial));
        extra.estado = estadoFixed;
      } else if(tipo === 'Recepción'){
        const nEnvio = el('input',{type:'text',placeholder:'N° envío original'});
        const folioGuia = el('input',{type:'text'});
        const folio = folioCicloControl(ciclosAb);
        const estado = el('select',{}, el('option',{value:'no operativo'},'No operativo'), el('option',{value:'operativo'},'Operativo'));
        extra = {nEnvio,folioGuia,folio,estado};
        campos.appendChild(el('div',{class:'grid-3'},
          formField('Fecha de recepción',fecha), formField('N° envío original',nEnvio), formField('Folio guía despacho',folioGuia)
        ));
        campos.appendChild(el('div',{class:'grid-3'},
          formField('Folio SIGEM',folio), formField('Estado resultante',estado), formField('Oficial',oficial)
        ));
        if(!ciclosAb.length) campos.appendChild(avisoSinCicloAbierto());
        campos.appendChild(formField('Informe técnico / Observación',obs));
      } else if(tipo === 'Reparación'){
        const folio = folioCicloControl(ciclosAb);
        const estado = el('select',{}, el('option',{value:'operativo'},'Operativo (cierra ciclo)'), el('option',{value:'no operativo'},'No operativo'), el('option',{value:'en servicio técnico'},'En servicio técnico (no cierra)'));
        const repuestos = el('input',{type:'text',placeholder:'Repuestos utilizados'});
        extra = {folio,estado,repuestos};
        campos.appendChild(el('div',{class:'grid-3'},
          formField('Fecha de reparación',fecha), formField('Ejecutor',ejecutor), formField('Repuestos',repuestos)
        ));
        campos.appendChild(el('div',{class:'grid-3'},
          formField('Folio SIGEM',folio), formField('Estado resultante',estado), formField('Oficial',oficial)
        ));
        if(!ciclosAb.length) campos.appendChild(avisoSinCicloAbierto());
        campos.appendChild(formField('Descripción de la tarea',obs));
      } else if(tipo === 'Mantención preventiva'){
        const ejec2 = el('select',{}, el('option',{value:''},'—'), ...EJECUTORES.map(x=>el('option',{value:x},x)));
        const resultado = el('select',{},
          ...['Si','C1','C2','C3','C4','C5','C6','C7','C8','FS','Baja','NU','No'].map(x=>el('option',{value:x},x))
        );
        // El estado resultante de una MP NO se elige a mano: se deriva del resultado/causal
        // (C2→en servicio técnico, C3/FS/NU→no operativo, Baja→baja, Si→operativo; C1/C4–C8 no
        // cambian el estado). Así no se puede guardar un C2 como "operativo" por descuido.
        const estado = el('input',{type:'text',readonly:true});
        const syncEstadoMP = ()=>{ estado.value = estadoMPDesdeResultado(resultado.value) || '(sin cambio de estado)'; };
        syncEstadoMP(); resultado.addEventListener('change', syncEstadoMP);
        extra = {ejec2,resultado};
        campos.appendChild(el('div',{class:'grid-3'},
          formField('Fecha MP',fecha), formField('Ejecutor',ejecutor), formField('Ejecutor 2',ejec2)
        ));
        campos.appendChild(el('div',{class:'grid-3'},
          formField('Resultado',resultado), formField('Estado resultante (automático)',estado), formField('Oficial',oficial)
        ));
        campos.appendChild(formField('Observación',obs));
        const noticeBox = el('div',{class:'notice info'},'Si resultado es C1–C8 se creará automáticamente un pendiente de reprogramación. Si es NU → pendiente "Localizar equipo". Si es Baja → equipo pasa a baja.');
        campos.appendChild(noticeBox);
      }

      // Botón guardar
      const btnGuardar = el('button',{class:'primary',onclick:()=>{
        if(!invSel){toast('Selecciona un equipo','error');return;}
        if(!findEquipo(invSel)){toast('Equipo no encontrado','error');return;}
        if(!fecha.value){toast('Fecha requerida','error');return;}
        const eq = findEquipo(invSel);
        // Alerta MP en mes sin programación
        if(tipo === 'Mantención preventiva'){
          const [yy, mm] = fecha.value.split('-').map(Number);
          const mesActual = MESES[mm-1];
          const codigoP = (eq.prog || {})[mesActual];
          if(!codigoP || !['X','R','RA','PM'].includes(codigoP)){
            const mesesProg = MESES.filter(m => ['X','R','RA','PM'].includes((eq.prog||{})[m]));
            const aviso = `Este equipo NO tiene MP programada en ${mesActual} ${yy}.\n\n` +
              (mesesProg.length > 0
                ? `Meses programados (${eq.freq||'sin frecuencia'}): ${mesesProg.join(', ')}.\n\n`
                : 'No tiene programación MP definida en la matriz.\n\n') +
              '¿Registrar igual?';
            if(!confirm(aviso)) return;
          }
        }
        const ev = {
          id: state.counters.evento++,
          inv: invSel, equipo: eq.equipo, servicio: eq.servicio, fam: eq.fam,
          tipo, fecha: fecha.value, fechaReg: hoyLocal(),
          ejecutor: ejecutor.value || null,
          obs: obs.value || null,
          oficial: oficial.value,
          anulado:false,
          creadoPor:'Cristian',
          ts: new Date().toISOString()
        };
        Object.keys(extra).forEach(k => { ev[k] = extra[k].value || null; });
        // Persistir estado y resultado en campos top-level
        if(extra.estado) ev.estado = extra.estado.value;
        if(extra.resultado) ev.resultado = extra.resultado.value;
        // MP: el estado resultante se deriva del resultado/causal (no de un menú manual).
        if(tipo === 'Mantención preventiva') ev.estado = estadoMPDesdeResultado(ev.resultado);
        if(extra.folio) ev.folio = extra.folio.value || null;
        if(extra.nEnvio) ev.nEnvio = extra.nEnvio.value || null;
        if(extra.nOC) ev.nOC = extra.nOC.value || null;
        if(extra.nCotiz) ev.nCotiz = extra.nCotiz.value || null;
        if(extra.empresa) ev.empresa = extra.empresa.value || null;
        if(extra.tecnico) ev.tecnico = extra.tecnico.value || null;
        if(extra.tipoVisita) ev.tipoVisita = extra.tipoVisita.value;
        if(extra.folioGuia) ev.folioGuia = extra.folioGuia.value || null;
        if(extra.ejec2) ev.ejecutor2 = extra.ejec2.value || null;
        if(extra.via) ev.via = extra.via.value;
        if(extra.folioInf) ev.folioInformeTD = extra.folioInf.value || null;
        if(extra.repuestos) ev.repuestos = extra.repuestos.value || null;

        state.eventos.push(ev);
        aplicarEfectosEvento(ev);
        audit('evento', ev.id, 'creado', null, tipo);
        save();
        closeModal();
        toast('Evento "'+tipo+'" registrado','success');
        if(currentView === 'equipo') navigate('equipo',{inv: invSel});
        else navigate(currentView, viewParams);
      }},'Guardar evento');

      campos.appendChild(el('div',{style:{marginTop:'14px',display:'flex',justifyContent:'flex-end',gap:'8px'}},
        el('button',{onclick:closeModal},'Cancelar'),
        btnGuardar
      ));
    } else {
      campos.appendChild(el('div',{class:'empty small'},'Selecciona el tipo de evento arriba para continuar.'));
    }

    return el('div',{},
      formField('N° Inventario del equipo', el('div',{},invInput,dataList)),
      eq ? el('div',{class:'eq-info-card',style:{marginTop:'14px'}},
        el('div',{class:'eq-info-hd'},
          el('strong',{}, eq.equipo||'—'),
          el('span',{class:'eq-info-inv'}, ' · '+eq.inv),
          badgeEstado(eq.estado),
          conflictosDe(eq.inv).length > 0 ? el('span',{class:'badge noop conflict-badge', title:'Conflictos pendientes con maestro', onclick:()=>{closeModal();navigate('equipo',{inv:eq.inv, openTab:'conflictos'});}}, conflictosDe(eq.inv).length+' conflicto'+(conflictosDe(eq.inv).length>1?'s':'')) : null
        ),
        el('div',{class:'eq-info-grid'},
          eqInfoCell('N° Carpeta', eq.carpeta),
          eqInfoCell('Serie', eq.serie),
          eqInfoCell('Marca', eq.marca),
          eqInfoCell('Modelo', eq.modelo),
          eqInfoCell('Servicio', eq.servicio),
          eqInfoCell('Unidad', eq.unidad),
          eqInfoCell('Ubicación', eq.ubic),
          eqInfoCell('Frecuencia MP', eq.freq)
        )
      ) : null,
      el('h3',{style:{marginTop:'18px'}},'Tipo de evento'),
      tipoGrid,
      tipo ? el('h3',{},'Datos del evento') : null,
      campos
    );
  }

  function rebuild(){
    const m = modal({title:'Nuevo evento', wide:true, body: build(),
      hasUnsavedData: ()=>{
        // Hay cambios si el usuario seleccionó tipo o llenó algún input visible
        if(tipo) return true;
        if(invSel && invSel !== (opts.invDefault||'')) return true;
        return false;
      }
    });
  }
  rebuild();
}
function formField(label, ctrl){
  return el('div',{}, el('label',{}, label), ctrl);
}
function eqInfoCell(lbl, val){
  const v = (val==null||val==='') ? '—' : String(val);
  return el('div',{class:'eq-info-cell'},
    el('div',{class:'eq-info-lbl'}, lbl),
    el('div',{class:'eq-info-val'+(v==='—'?' empty':'')}, v)
  );
}

//==============================================================
// EDITAR / OFICIALIZAR / ANULAR EVENTO
//==============================================================
function oficializarEvento(ev){
  // Documentos esperados según tipo
  const docsEsperados = ev.tipo === 'Mantención preventiva' ? DOCS_PREVENTIVO :
    (['Solicitud de trabajo','Visita técnica','Orden de Compra','Envío a servicio técnico','Recepción','Reparación'].includes(ev.tipo) ? DOCS_CORRECTIVO : []);
  const body = el('div',{},
    el('div',{class:'notice warn',style:{marginBottom:'14px'}},
      el('strong',{},'Al oficializar:'),
      el('ul',{style:{margin:'6px 0 0 18px',padding:0,fontSize:'13px'}},
        el('li',{},'El registro queda congelado (no editable libremente).'),
        el('li',{},'Se marca como "Oficial" para auditoría.'),
        el('li',{},'Se incluye en reportes oficiales y exports.')
      )
    ),
    el('div',{},
      el('strong',{style:{fontSize:'13px'}}, 'Evento: '), el('span',{}, ev.tipo+' · '+fmtFecha(ev.fecha)+' · '+(ev.ejecutor||'sin ejecutor')),
      ev.resultado ? el('div',{style:{marginTop:'4px',fontSize:'13px'}}, el('strong',{},'Resultado: '), ev.resultado) : null
    ),
    docsEsperados.length > 0 ? el('div',{style:{marginTop:'14px'}},
      el('div',{class:'eq-info-lbl'}, 'Documentos esperados (revisa que estén archivados)'),
      el('ul',{style:{margin:'4px 0 0 18px',padding:0,fontSize:'12px',color:'var(--muted)'}},
        ...docsEsperados.map(d => el('li',{},d))
      )
    ) : null
  );
  modal({title:'Oficializar evento', body, footer:[
    el('button',{onclick:closeModal},'Cancelar'),
    el('button',{class:'primary',onclick:()=>{
      ev.oficial = 'Sí';
      ev.ts = new Date().toISOString();
      audit('evento',ev.id,'oficial','No','Sí');
      save();
      closeModal();
      toast('Evento oficializado','success');
      navigate(currentView, viewParams);
    }},'✓ Oficializar')
  ]});
}
function editarEvento(ev){
  // Mini-form de edición (campos básicos)
  const fecha = el('input',{type:'date',value:ev.fecha||''});
  const obs = el('textarea',{}, ev.obs||'');
  const ejecutor = el('select',{}, el('option',{value:''},'—'), ...EJECUTORES.map(x=>el('option',{value:x,selected:x===ev.ejecutor?'selected':false},x)));
  const oficial = el('select',{}, el('option',{value:'No',selected:ev.oficial!=='Sí'?'selected':false},'Borrador'), el('option',{value:'Sí',selected:ev.oficial==='Sí'?'selected':false},'Oficial'));
  ejecutor.value = ev.ejecutor||''; oficial.value = ev.oficial||'No';
  modal({title:'Editar evento — '+ev.tipo, body: el('div',{},
    el('div',{class:'kv'},
      el('dt',{},'Tipo'), el('dd',{}, ev.tipo),
      el('dt',{},'Equipo'), el('dd',{}, ev.inv+' · '+(ev.equipo||''))
    ),
    el('div',{style:{marginTop:'10px'},class:'grid-2'},
      formField('Fecha',fecha), formField('Ejecutor',ejecutor),
      formField('Oficial',oficial)
    ),
    formField('Observación',obs)
  ), footer:[
    el('button',{onclick:closeModal},'Cancelar'),
    el('button',{class:'primary',onclick:()=>{
      audit('evento',ev.id,'fecha',ev.fecha,fecha.value);
      ev.fecha = fecha.value; ev.obs = obs.value; ev.ejecutor = ejecutor.value; ev.oficial = oficial.value;
      ev.ts = new Date().toISOString();
      save(); closeModal();
      navigate(currentView,viewParams);
      toast('Evento actualizado','success');
    }},'Guardar cambios')
  ]});
}
const MOTIVOS_ANULACION = [
  'Mal ingresado',
  'Equipo equivocado',
  'Fecha errónea',
  'Resultado equivocado',
  'Duplicado',
  'Ejecutor equivocado',
  'Documentación faltante'
];

function anularEvento(ev){
  // Modal con motivos predefinidos + textarea opcional
  const motivoSel = el('select',{}, el('option',{value:''},'— Selecciona motivo —'), ...MOTIVOS_ANULACION.map(m=>el('option',{value:m},m)), el('option',{value:'__otro'},'Otro (especificar)'));
  const otro = el('textarea',{placeholder:'Detalle adicional (opcional si seleccionaste un motivo de la lista)'});
  const minsCreado = ev.ts ? Math.floor((Date.now() - new Date(ev.ts).getTime()) / 60000) : -1;
  const advRecien = minsCreado >= 0 && minsCreado < 60
    ? el('div',{class:'notice warn',style:{marginBottom:'14px'}},
        `⚠ Este evento se registró hace ${minsCreado} minuto${minsCreado!==1?'s':''}. Si fue por error reciente, anula y vuelve a registrar correctamente.`)
    : null;
  function ejecutar(){
    const sel = motivoSel.value;
    const extra = otro.value.trim();
    let motivo = '';
    if(sel === '__otro'){ if(!extra){ toast('Especifica el motivo','error'); return; } motivo = extra; }
    else if(!sel){ toast('Selecciona un motivo','error'); return; }
    else { motivo = sel + (extra ? ' — '+extra : ''); }
    closeModal();
    anularEventoAplicar(ev, motivo);
  }
  modal({title:'Anular evento — '+ev.tipo, body: el('div',{},
    advRecien,
    el('div',{style:{fontSize:'13px',marginBottom:'12px',color:'var(--muted)'}},
      `Equipo ${ev.inv} · Fecha ${fmtFecha(ev.fecha)}${ev.resultado?' · Resultado '+ev.resultado:''}${ev.ejecutor?' · '+ev.ejecutor:''}`
    ),
    formField('Motivo de anulación', motivoSel),
    formField('Detalle (opcional)', otro),
    el('div',{class:'notice info',style:{marginTop:'12px',fontSize:'12px'}},
      'Anular revierte efectos: limpia R del mes en matriz, recalcula estado, anula ciclos/pendientes asociados.')
  ),
  footer:[
    el('button',{onclick:closeModal},'Cancelar'),
    el('button',{class:'danger',onclick:ejecutar},'⊘ Anular evento')
  ],
  hasUnsavedData: ()=> motivoSel.value !== '' || otro.value.trim() !== ''
  });
  setTimeout(()=>motivoSel.focus(), 80);
}

function anularEventoAplicar(ev, motivo){
  ev.anulado = true;
  ev.motivoAnulacion = motivo;
  ev.fechaAnulacion = new Date().toISOString();

  // === Revertir efectos ===
  const eq = findEquipo(ev.inv);
  let revertidos = [];

  if(eq){
    // 1. Si era MP con resultado, limpiar el R del mes (o usar la siguiente MP no anulada del mismo mes)
    if(ev.tipo === 'Mantención preventiva' && ev.fecha && ev.resultado){
      const [y,m] = ev.fecha.split('-').map(Number);
      const mes = MESES[m-1];
      if(eq.registro && eq.registro[mes]){
        const otrasMP = state.eventos.filter(x =>
          x.id !== ev.id && !x.anulado && x.inv === ev.inv &&
          x.tipo === 'Mantención preventiva' && x.fecha && x.resultado &&
          x.fecha.startsWith(`${y}-${String(m).padStart(2,'0')}`)
        ).sort((a,b)=>(b.fecha||'').localeCompare(a.fecha||''));
        if(otrasMP.length === 0){
          delete eq.registro[mes].R;
          if(Object.keys(eq.registro[mes]).length === 0) delete eq.registro[mes];
          revertidos.push(`R de ${mes} eliminado`);
        } else {
          eq.registro[mes].R = otrasMP[0].resultado;
          revertidos.push(`R de ${mes} cambiado a ${otrasMP[0].resultado} (de otra MP)`);
        }
      }
    }
    // 2. Recalcular estado del equipo desde los eventos no anulados restantes
    const estadoAntes = eq.estado;
    recalcEstadoEquipo(eq);
    if(eq.estado !== estadoAntes) revertidos.push(`estado: ${ESTADO_LABEL[estadoAntes]} → ${ESTADO_LABEL[eq.estado]}`);
  }

  // 3. Solicitud que abrió ciclo: marcar ciclo como anulado si no quedan más eventos
  if(ev.tipo === 'Solicitud de trabajo' && ev.folio){
    const ciclo = state.ciclos.find(c => c.folio === ev.folio);
    if(ciclo){
      const otros = state.eventos.filter(x => x.id !== ev.id && !x.anulado && x.folio === ev.folio);
      if(otros.length === 0){
        ciclo.estado = 'anulado';
        ciclo.anulado = true;
        ciclo.fechaCierre = ev.fecha;
        revertidos.push(`ciclo ${ev.folio} anulado`);
      }
    }
  }
  // 4. Reparación que cerró ciclo: reabrir si no hay otra reparación operativa posterior
  if((ev.tipo === 'Reparación' || ev.tipo === 'Recepción' || (ev.tipo === 'Visita técnica' && ev.tipoVisita === 'correctiva'))
     && ev.estado === 'operativo' && ev.folio){
    const ciclo = state.ciclos.find(c => c.folio === ev.folio);
    if(ciclo && ciclo.estado === 'cerrado'){
      const otraOp = state.eventos.find(x => x.id !== ev.id && !x.anulado && x.folio === ev.folio &&
        (x.tipo === 'Reparación' || x.tipo === 'Recepción' || (x.tipo === 'Visita técnica' && x.tipoVisita === 'correctiva')) &&
        x.estado === 'operativo');
      if(!otraOp){
        ciclo.estado = 'abierto';
        ciclo.fechaCierre = null;
        revertidos.push(`ciclo ${ev.folio} reabierto`);
      }
    }
  }
  // 5. MP con causal C1-C8: anular pendientes auto generados
  if(ev.tipo === 'Mantención preventiva' && ev.resultado && /^C[1-8]$/.test(ev.resultado)){
    const pendsAuto = state.pendientes.filter(p => p.eventoOrigen === ev.id && !p.anulado && p.estado !== 'cerrado');
    pendsAuto.forEach(p => {
      p.anulado = true;
      p.motivoAnulacion = 'Evento MP origen anulado';
    });
    if(pendsAuto.length > 0) revertidos.push(`${pendsAuto.length} pendiente(s) automático(s) anulado(s)`);
  }

  audit('evento', ev.id, 'anulado', false, true);
  save();
  const detalle = revertidos.length > 0 ? ' (' + revertidos.join('; ') + ')' : '';
  toast('Evento anulado' + detalle, 'success');
  navigate(currentView, viewParams);
}

//==============================================================
// PENDIENTES — abrir, cerrar, crear, tareas
//==============================================================
function nuevoPendiente(opts){
  opts = opts || {};
  const eqList = state.equipos.slice().sort((a,b)=>a.inv.localeCompare(b.inv));
  const invInput = el('input',{type:'text',list:'eq-list-p',value:opts.invDefault||'',placeholder:'N° Inventario'});
  const dataList = el('datalist',{id:'eq-list-p'}, ...eqList.slice(0,200).map(e=>el('option',{value:e.inv}, `${e.inv} — ${e.equipo}`)));
  const tipo = el('select',{}, ...Object.entries(TIPO_PENDIENTE).map(([k,v])=>el('option',{value:k},v)));
  const desc = el('textarea',{placeholder:'Descripción del pendiente'});
  const ejec = el('select',{}, el('option',{value:''},'—'), ...EJECUTORES.map(x=>el('option',{value:x},x)));
  const fComp = el('input',{type:'date'});
  const fRec = el('input',{type:'date'});
  // Si se crea desde un evento del historial, queda LIGADO a ese evento (eventoOrigen).
  const evLigado = opts.eventoOrigen != null ? state.eventos.find(e=>e.id===opts.eventoOrigen) : null;

  modal({title: evLigado ? 'Nuevo pendiente (ligado a un evento)' : 'Nuevo pendiente',
    hasUnsavedData: ()=> desc.value.trim() !== '' || ejec.value !== '' || fComp.value !== '' || fRec.value !== '',
    body: el('div',{},
    evLigado ? el('div',{class:'notice'}, '🔗 Quedará ligado al evento: '+evLigado.tipo+' · '+fmtFecha(evLigado.fecha)+(evLigado.folio?(' · Folio '+evLigado.folio):'')) : null,
    el('div',{class:'grid-2'},
      formField('N° Inventario', el('div',{},invInput,dataList)),
      formField('Tipo', tipo)
    ),
    formField('Descripción', desc),
    el('div',{class:'grid-3'},
      formField('Ejecutor', ejec),
      formField('Fecha compromiso', fComp),
      formField('Próximo recordatorio', fRec)
    )
  ), footer:[
    el('button',{onclick:closeModal},'Cancelar'),
    el('button',{class:'primary',onclick:()=>{
      const inv = invInput.value.trim();
      if(!inv || !findEquipo(inv)){toast('Equipo inválido','error');return;}
      if(!desc.value.trim()){toast('Descripción requerida','error');return;}
      const eq = findEquipo(inv);
      const p = {
        id: state.counters.pend++,
        inv, equipo: eq.equipo, servicio: eq.servicio,
        tipo: tipo.value, desc: desc.value.trim(),
        ejecutor: ejec.value||null,
        fechaCrea: hoyLocal(),
        fechaComp: fComp.value||null, proxRecord: fRec.value||null,
        fechaCierre:null, estado:'no_iniciado', origen:'manual',
        eventoOrigen: opts.eventoOrigen != null ? opts.eventoOrigen : null,
        seguimientos:[], tareas:[], anulado:false
      };
      state.pendientes.push(p);
      audit('pendiente',p.id,'creado_manual',null,tipo.value);
      save(); closeModal();
      toast('Pendiente creado','success');
      navigate(currentView,viewParams);
    }},'Crear pendiente')
  ]});
}

function abrirPendiente(p){
  const eq = findEquipo(p.inv) || {};
  const desc = el('textarea',{},p.desc||'');
  const tipo = el('select',{}, ...Object.entries(TIPO_PENDIENTE).map(([k,v])=>el('option',{value:k,selected:k===p.tipo?'selected':false},v)));
  const ejec = el('select',{}, el('option',{value:''},'—'), ...EJECUTORES.map(x=>el('option',{value:x,selected:x===p.ejecutor?'selected':false},x)));
  const estado = el('select',{}, ...['no_iniciado','en_proceso','cerrado'].map(s=>el('option',{value:s,selected:s===p.estado?'selected':false},ESTADO_PEND_LABEL[s])));
  const fComp = el('input',{type:'date',value:p.fechaComp||''});
  const fRec = el('input',{type:'date',value:p.proxRecord||''});
  tipo.value = p.tipo; ejec.value = p.ejecutor||''; estado.value = p.estado;

  // Tareas
  const tareasBox = el('div',{});
  const renderTareas = ()=>{
    tareasBox.innerHTML = '';
    const ts = state.tareas.filter(t => t.pendId === p.id || (p.tareas||[]).includes(t.id));
    if(ts.length === 0) tareasBox.appendChild(el('div',{class:'empty small'},'Sin tareas.'));
    else tareasBox.appendChild(el('div',{}, ...ts.map(t => el('div',{style:{display:'flex',alignItems:'center',gap:'8px',padding:'5px 0'}},
      el('input',{type:'checkbox',checked:t.estado==='cerrado'?'checked':false, style:{width:'auto'},onchange:e=>{
        t.estado = e.target.checked ? 'cerrado' : 'abierto';
        if(e.target.checked) t.fechaCierre = hoyLocal();
        audit('tarea',t.id,'estado',t.estado==='cerrado'?'abierto':'cerrado',t.estado);
        save();
        // Si todas cerradas → sugerir cerrar pendiente
        const todasCerradas = state.tareas.filter(x=>x.pendId===p.id).every(x=>x.estado==='cerrado');
        if(todasCerradas && state.tareas.filter(x=>x.pendId===p.id).length>0 && p.estado!=='cerrado'){
          if(confirm('Todas las tareas están cerradas. ¿Cerrar el pendiente?')){
            p.estado = 'cerrado'; p.fechaCierre = hoyLocal();
            save(); closeModal(); navigate(currentView,viewParams);
          }
        }
      }}),
      el('span',{style:t.estado==='cerrado'?{textDecoration:'line-through',color:'var(--muted)'}:null}, t.desc)
    ))));
  };
  renderTareas();

  const nuevaTareaInput = el('input',{type:'text',placeholder:'Nueva tarea…',onkeydown:e=>{
    if(e.key==='Enter' && e.target.value.trim()){
      const t = {id:state.counters.tarea++, pendId:p.id, inv:p.inv, equipo:p.equipo, desc:e.target.value.trim(), estado:'abierto'};
      state.tareas.push(t);
      p.tareas = (p.tareas||[]).concat(t.id);
      save();
      e.target.value='';
      renderTareas();
    }
  }});

  // Seguimientos
  const seguimientosBox = el('div',{});
  const renderSeg = ()=>{
    seguimientosBox.innerHTML = '';
    (p.seguimientos||[]).forEach(s => seguimientosBox.appendChild(el('div',{style:{padding:'6px 8px',background:'#fafbfd',borderRadius:'4px',marginBottom:'4px',fontSize:'12px'}},
      el('div',{},el('strong',{},s.autor),' · ',el('small',{class:'muted'},fmtFecha(s.fecha))),
      el('div',{}, s.texto)
    )));
    if(!p.seguimientos || p.seguimientos.length===0) seguimientosBox.appendChild(el('div',{class:'empty small'},'Sin seguimientos.'));
  };
  renderSeg();
  const nuevoSegTxt = el('input',{type:'text',placeholder:'Agregar seguimiento (Enter para guardar)…',onkeydown:e=>{
    if(e.key==='Enter' && e.target.value.trim()){
      p.seguimientos = p.seguimientos||[];
      p.seguimientos.push({autor:'Cristian',fecha:hoyLocal(),texto:e.target.value.trim()});
      save();
      e.target.value='';
      renderSeg();
    }
  }});

  modal({title:'Pendiente · '+p.inv, wide:true, body: el('div',{},
    el('div',{class:'eq-info-card'},
      el('div',{class:'eq-info-hd'},
        el('strong',{}, eq.equipo||p.equipo||'—'),
        el('span',{class:'eq-info-inv'}, ' · '+p.inv),
        eq.estado ? badgeEstado(eq.estado) : null,
        conflictosDe(p.inv).length > 0 ? el('span',{class:'badge noop conflict-badge', title:'Click para ir a la pestaña Conflictos del equipo', onclick:()=>{closeModal();navigate('equipo',{inv:p.inv, openTab:'conflictos'});}}, conflictosDe(p.inv).length+' conflicto'+(conflictosDe(p.inv).length>1?'s':'')) : null,
        el('button',{class:'small ghost eq-info-link',onclick:()=>{closeModal();navigate('equipo',{inv:p.inv});}}, 'Ver ficha →')
      ),
      el('div',{class:'eq-info-grid'},
        eqInfoCell('N° Carpeta', eq.carpeta),
        eqInfoCell('Serie', eq.serie),
        eqInfoCell('Marca', eq.marca),
        eqInfoCell('Modelo', eq.modelo),
        eqInfoCell('Servicio', eq.servicio),
        eqInfoCell('Unidad', eq.unidad),
        eqInfoCell('Ubicación', eq.ubic),
        eqInfoCell('Frecuencia MP', eq.freq)
      )
    ),
    el('div',{class:'grid-2'},
      formField('Tipo', tipo), formField('Estado', estado),
      formField('Ejecutor', ejec),
      formField('Equipo (resumen)', el('div',{style:{padding:'8px 0',color:'var(--muted)',fontSize:'13px'}}, `${p.inv} · ${eq.equipo||'—'}`))
    ),
    el('div',{class:'pend-section'},
      el('label',{class:'pend-section-lbl'},'Descripción del pendiente'),
      desc
    ),
    el('div',{class:'grid-2'}, formField('Fecha compromiso', fComp), formField('Próximo recordatorio', fRec)),
    el('div',{class:'pend-section'},
      el('label',{class:'pend-section-lbl'}, 'Tareas atómicas (sub-pasos)'),
      el('div',{class:'pend-section-hint'}, 'Divide el pendiente en pasos chequeables. Tipea abajo y presiona Enter.'),
      tareasBox,
      el('div',{class:'pend-new-row'},
        el('span',{class:'plus-icon'},'+'),
        nuevaTareaInput
      )
    ),
    el('div',{class:'pend-section'},
      el('label',{class:'pend-section-lbl'},'Seguimientos (notas con timestamp)'),
      el('div',{class:'pend-section-hint'}, 'Bitácora interna del pendiente. Tipea abajo y presiona Enter.'),
      seguimientosBox,
      el('div',{class:'pend-new-row'},
        el('span',{class:'plus-icon'},'+'),
        nuevoSegTxt
      )
    )
  ), footer:[
    el('button',{class:'danger',onclick:()=>{
      if(!confirm('¿Anular pendiente?')) return;
      p.anulado=true; save(); closeModal(); navigate(currentView,viewParams);
    }},'Anular'),
    el('button',{onclick:closeModal},'Cerrar diálogo'),
    el('button',{class:'primary',onclick:()=>{
      p.tipo = tipo.value;
      p.estado = estado.value;
      p.ejecutor = ejec.value||null;
      p.desc = desc.value;
      p.fechaComp = fComp.value||null;
      p.proxRecord = fRec.value||null;
      if(p.estado==='cerrado' && !p.fechaCierre) p.fechaCierre = hoyLocal();
      save(); closeModal();
      toast('Pendiente actualizado','success');
      navigate(currentView,viewParams);
    }},'Guardar')
  ]});
}

function cerrarPendiente(p){
  const txt = prompt('Comentario de cierre (opcional):');
  p.estado = 'cerrado';
  p.fechaCierre = hoyLocal();
  if(txt){
    p.seguimientos = p.seguimientos||[];
    p.seguimientos.push({autor:'Cristian',fecha:p.fechaCierre,texto:'Cierre: '+txt});
  }
  audit('pendiente',p.id,'estado','abierto','cerrado');
  save();
  navigate(currentView,viewParams);
  toast('Pendiente cerrado','success');
}

function cerrarCicloManual(c){
  const motivo = prompt('Justificación del cierre manual:');
  if(!motivo) return;
  cerrarCiclo(c.folio, hoyLocal(), motivo);
  save();
  toast('Ciclo cerrado','success');
  navigate(currentView,viewParams);
}

function darDeBaja(eq){
  const motivo = prompt('Motivo de la baja:');
  if(!motivo) return;
  const fecha = hoyLocal();
  // Evento informativo
  const ev = {
    id: state.counters.evento++, inv:eq.inv, equipo:eq.equipo, servicio:eq.servicio,
    tipo:'Mantención preventiva', fecha, fechaReg:fecha, resultado:'Baja',
    ejecutor:'Cristián Beltrán Oviedo', estado:'baja', obs:'Baja: '+motivo,
    oficial:'Sí', anulado:false, ts:new Date().toISOString()
  };
  state.eventos.push(ev);
  // Marcar en registro mes actual
  const mes = NUM_MES[new Date().getMonth()];
  eq.registro = eq.registro||{};
  eq.registro[mes] = {R:'Baja'};
  // Limpiar meses posteriores
  for(let i=new Date().getMonth()+1; i<12; i++){
    if(eq.registro[NUM_MES[i]]) delete eq.registro[NUM_MES[i]];
  }
  const old = eq.estado;
  eq.estado = 'baja'; eq.estadoDesde = fecha;
  audit('equipo',eq.inv,'estado',old,'baja');
  // Cerrar pendientes
  state.pendientes.filter(p => p.inv === eq.inv && p.estado !== 'cerrado').forEach(p => {
    p.estado = 'cerrado'; p.fechaCierre = fecha;
    p.seguimientos = p.seguimientos||[];
    p.seguimientos.push({autor:'Cristian',fecha,texto:'Cerrado automáticamente: equipo dado de baja'});
  });
  save();
  toast('Equipo dado de baja','success');
  navigate('equipo',{inv:eq.inv});
}

//==============================================================
// EXPORT / IMPORT
//==============================================================
function exportData(){
  const data = JSON.stringify(state,null,2);
  const blob = new Blob([data],{type:'application/json'});
  const url = URL.createObjectURL(blob);
  const a = el('a',{href:url,download:'hhha-data-'+hoyLocal()+'.json'});
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
  toast('Backup JSON exportado','success');
}

// === PLANTILLA DE ASIGNACIÓN MP ===

const MES_ESPANOL = {Ene:'Enero',Feb:'Febrero',Mar:'Marzo',Abr:'Abril',May:'Mayo',Jun:'Junio',Jul:'Julio',Ago:'Agosto',Sep:'Septiembre',Oct:'Octubre',Nov:'Noviembre',Dic:'Diciembre'};

// Detecta el índice de mes (0-11) en un nombre de archivo. Soporta variantes
// en español: Ene/Enero, Feb/Febrero, Mar/Marzo, Abr/Abril, May/Mayo, Jun/Junio,
// Jul/Julio, Ago/Agosto, Sep/Septiembre, Oct/Octubre, Nov/Noviembre, Dic/Diciembre.
// Retorna {idx, year} o null si no detecta.
function mesDelNombreArchivo(nombre){
  const norm = (nombre||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');
  const meses = [
    ['ene','enero'],['feb','febrero'],['mar','marzo'],['abr','abril'],
    ['may','mayo'],['jun','junio'],['jul','julio'],['ago','agosto'],
    ['sep','septiembre','set','sept'],['oct','octubre'],['nov','noviembre'],['dic','diciembre']
  ];
  let foundIdx = null;
  // Buscar por palabra completa con boundary o separadores
  for(let i = 0; i < meses.length; i++){
    for(const alias of meses[i]){
      const re = new RegExp(`(^|[_\\s\\-\\.])${alias}([_\\s\\-\\.]|$)`, 'i');
      if(re.test(norm)){
        foundIdx = i;
        break;
      }
    }
    if(foundIdx != null) break;
  }
  if(foundIdx == null) return null;
  const yearMatch = norm.match(/(20\d{2})/);
  return {idx: foundIdx, year: yearMatch ? parseInt(yearMatch[1]) : null};
}

function descargarPlantillaMP(year, monthIdx){
  if(typeof XLSX === 'undefined'){ toast('Parser Excel no disponible','error'); return; }
  const mes = NUM_MES[monthIdx];
  const keyMes = `${year}-${String(monthIdx+1).padStart(2,'0')}`;
  const asignaciones = state.asignacionesMP[keyMes] || {};

  // Filtrar equipos programados en el mes (excluyendo baja y los con FS/Baja/NU en meses previos)
  const equipos = state.equipos.filter(eq => {
    if(eq.estado === 'baja') return false;
    if(!mpProgramadaEnMes(eq, mes)) return false;
    const prevR = Object.entries(eq.registro||{}).some(([m,obj]) => {
      const idx = MES_NUM[m];
      return idx < monthIdx && ['FS','Baja','NU'].includes(obj.R);
    });
    if(prevR) return false;
    return true;
  });

  if(equipos.length === 0){
    toast(`No hay equipos programados para ${mes} ${year}.`, 'warn-backup');
    return;
  }

  // Hoja Asignación con el formato del usuario
  const header = ['N° Carpeta','N° Inventario','Equipo','Servicio','Unidad','Ubicación','Marca','Modelo','Serie','Año','Frecuencia MP','Programado en mes','Responsable'];
  const rows = [header];
  equipos.forEach(eq => {
    rows.push([
      eq.carpeta||'', eq.inv||'', eq.equipo||'', eq.servicio||'', eq.unidad||'',
      eq.ubic||'', eq.marca||'', eq.modelo||'', eq.serie||'', eq.ano||'',
      eq.freq||'', (eq.prog||{})[mes] || '', asignaciones[eq.inv] || ''
    ]);
  });
  const wb = XLSX.utils.book_new();
  const ws = XLSX.utils.aoa_to_sheet(rows);
  // Ancho de columnas razonable
  ws['!cols'] = [{wch:10},{wch:16},{wch:22},{wch:24},{wch:22},{wch:22},{wch:18},{wch:24},{wch:16},{wch:6},{wch:18},{wch:14},{wch:26}];
  XLSX.utils.book_append_sheet(wb, ws, 'Asignación');

  // Hoja Responsables_oficiales
  const respRows = [['Responsable oficial']].concat(EJECUTORES.map(e => [e]));
  const wsResp = XLSX.utils.aoa_to_sheet(respRows);
  wsResp['!cols'] = [{wch:28}];
  XLSX.utils.book_append_sheet(wb, wsResp, 'Responsables_oficiales');

  // Validación de datos en la columna Responsable (drop-down referenciando la otra hoja)
  // Aplicar a M2:M(equipos.length+1) — columna 12 (índice 0-based)
  const lastRow = equipos.length + 1;
  ws['!dataValidation'] = ws['!dataValidation'] || [];
  // Nota: openpyxl-equivalente no aplica drop-down directamente vía aoa_to_sheet.
  // El usuario aún podrá escribir nombres, y el upload validará contra el catálogo.
  // (Si el usuario quisiera el drop-down nativo, requeriría manipulación XML adicional.)

  const wbout = XLSX.write(wb, {bookType:'xlsx', type:'array'});
  const blob = new Blob([wbout], {type:'application/octet-stream'});
  const url = URL.createObjectURL(blob);
  const a = el('a',{href:url, download:`Plantilla_Asignacion_${MES_ESPANOL[mes]}_${year}.xlsx`});
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
  const conAsig = equipos.filter(eq => asignaciones[eq.inv]).length;
  toast(`Plantilla generada: ${equipos.length} equipos (${conAsig} con responsable pre-llenado).`, 'success');
}

async function subirPlantillaMP(file, year, monthIdx){
  if(typeof XLSX === 'undefined'){ toast('Parser Excel no disponible','error'); return; }
  // Detectar mes del nombre del archivo y comparar con el dropdown
  const detectado = mesDelNombreArchivo(file.name);
  let yearFinal = year, monthIdxFinal = monthIdx;
  if(detectado && detectado.idx !== monthIdx){
    const mesArchivo = NUM_MES[detectado.idx];
    const yearArch = detectado.year || year;
    const mesDropdown = NUM_MES[monthIdx];
    const opciones =
      `El archivo "${file.name}" parece ser de ${MES_ESPANOL[mesArchivo]} ${yearArch}.\n` +
      `El mes seleccionado en pantalla es ${MES_ESPANOL[mesDropdown]} ${year}.\n\n` +
      `Aceptar → cargar en ${MES_ESPANOL[mesArchivo]} ${yearArch} (mes del archivo)\n` +
      `Cancelar → no cargar (no se hizo cambio)`;
    if(!confirm(opciones)){
      toast('Carga cancelada por mismatch de mes.', 'warn-backup');
      return;
    }
    monthIdxFinal = detectado.idx;
    if(detectado.year) yearFinal = detectado.year;
  } else if(detectado && detectado.year && detectado.year !== year){
    if(!confirm(`El archivo es de ${detectado.year} pero la vista está en ${year}. ¿Cargar en ${detectado.year}?`)){
      toast('Carga cancelada.', 'warn-backup');
      return;
    }
    yearFinal = detectado.year;
  }
  try{
    const buf = await file.arrayBuffer();
    const wb = XLSX.read(buf, {type:'array'});
    const hojaAsig = wb.SheetNames.find(n => /asignaci/i.test(n)) || wb.SheetNames[0];
    if(!hojaAsig){ toast('No se encontró hoja de asignación en el archivo.', 'error'); return; }
    const rows = XLSX.utils.sheet_to_json(wb.Sheets[hojaAsig], {header:1, defval:null, blankrows:false});
    if(rows.length < 2){ toast('La plantilla no tiene datos.', 'error'); return; }

    // Identificar columnas de N° Inventario y Responsable por encabezado
    const header = rows[0];
    const invIdx = header.findIndex(c => /N° Inventario/i.test(String(c||'')));
    const respIdx = header.findIndex(c => /Responsable/i.test(String(c||'')));
    if(invIdx < 0 || respIdx < 0){
      toast('La plantilla debe tener columnas "N° Inventario" y "Responsable".', 'error');
      return;
    }

    const keyMes = `${yearFinal}-${String(monthIdxFinal+1).padStart(2,'0')}`;
    state.asignacionesMP[keyMes] = state.asignacionesMP[keyMes] || {};
    const ejecutoresSet = new Set(EJECUTORES);

    let cargadas = 0, sobrescritas = 0;
    const ignoradas = {invNoExiste: [], respInvalido: [], sinResp: 0};

    for(let r = 1; r < rows.length; r++){
      const row = rows[r];
      if(!row) continue;
      const inv = (row[invIdx] != null ? String(row[invIdx]).trim() : '');
      const resp = (row[respIdx] != null ? String(row[respIdx]).trim() : '');
      if(!inv) continue;
      if(!resp){ ignoradas.sinResp++; continue; }
      if(!findEquipo(inv)){ ignoradas.invNoExiste.push(inv); continue; }
      if(!ejecutoresSet.has(resp)){ ignoradas.respInvalido.push(`${inv}: ${resp}`); continue; }
      const prev = state.asignacionesMP[keyMes][inv];
      state.asignacionesMP[keyMes][inv] = resp;
      if(prev && prev !== resp) sobrescritas++;
      cargadas++;
    }
    save();

    const mes = NUM_MES[monthIdxFinal];
    let detalle = `${cargadas} asignaciones cargadas en ${mes} ${yearFinal}`;
    if(sobrescritas > 0) detalle += ` (${sobrescritas} sobrescritas)`;
    const ignorTotal = ignoradas.invNoExiste.length + ignoradas.respInvalido.length + ignoradas.sinResp;
    if(ignorTotal > 0){
      detalle += `\nIgnoradas: ${ignorTotal}`;
      if(ignoradas.sinResp > 0) detalle += `\n  · ${ignoradas.sinResp} sin responsable`;
      if(ignoradas.invNoExiste.length > 0) detalle += `\n  · ${ignoradas.invNoExiste.length} N° Inv. no encontrado: ${ignoradas.invNoExiste.slice(0,3).join(', ')}${ignoradas.invNoExiste.length>3?'…':''}`;
      if(ignoradas.respInvalido.length > 0) detalle += `\n  · ${ignoradas.respInvalido.length} responsable inválido: ${ignoradas.respInvalido.slice(0,2).join('; ')}${ignoradas.respInvalido.length>2?'…':''}`;
      alert(detalle);
    } else {
      toast(detalle, 'success');
    }
  } catch(err){
    toast('Error al leer plantilla: '+err.message, 'error');
    console.error(err);
  }
}

function exportExcel(){
  if(typeof XLSX === 'undefined'){ toast('Parser Excel no disponible','error'); return; }
  state.equipos.forEach(recalcEstadoEquipo);
  const wb = XLSX.utils.book_new();
  const year = new Date().getFullYear();
  const hoy = hoyLocal();
  // Hoja simple con anchos. Las tablas además llevan autofiltro para ordenar/buscar en Excel.
  const addPlain = (ws, nombre, cols) => { if(cols) ws['!cols']=cols; XLSX.utils.book_append_sheet(wb, ws, nombre); };
  const tabla = (rows, nombre, cols) => {
    const ws = XLSX.utils.json_to_sheet(rows.length ? rows : [{' ':'(sin datos)'}]);
    if(ws['!ref']) ws['!autofilter'] = {ref: ws['!ref']};
    addPlain(ws, nombre, cols);
  };

  // Mapeo de un evento a fila (se usa para los tuyos y para los automáticos)
  const mapEv = e => ({
    'ID': e.id, 'Fecha del evento': fmtFecha(e.fecha), 'Fecha registro': fmtFecha(e.fechaReg),
    'N° Inv.': e.inv, 'Equipo': e.equipo||'', 'Servicio': e.servicio||'',
    'Tipo': e.tipo, 'Resultado': e.resultado||'', 'Estado equipo': e.estado||'',
    'Ejecutor': e.ejecutor||'', 'Folio SIGEM': e.folio||'',
    'N° Envío': e.nEnvio||'', 'N° OC': e.nOC||'', 'N° Cotización': e.nCotiz||'',
    'Empresa': e.empresa||'', 'Técnico': e.tecnico||'',
    'Observación': e.obs||'', 'Oficial': e.oficial||'No', 'Creado por': e.creadoPor||''
  });
  const colsEv = [{wch:5},{wch:14},{wch:14},{wch:13},{wch:22},{wch:20},{wch:18},{wch:9},{wch:13},{wch:20},{wch:21},{wch:8},{wch:13},{wch:13},{wch:20},{wch:16},{wch:42},{wch:8},{wch:12}];

  // Eventos automáticos (generados al conciliar el maestro) van a una hoja OCULTA.
  // Lo que el usuario registró (incluidos borradores) va a la hoja visible "Eventos".
  const esAuto = e => e.origen === 'conciliacion_auto' || e.origen === 'conciliacion';
  const evNoAnul = state.eventos.filter(e=>!e.anulado);
  const evMios = evNoAnul.filter(e=>!esAuto(e));
  const evAuto = evNoAnul.filter(esAuto);
  const pendAb = state.pendientes.filter(p=>!p.anulado && p.estado!=='cerrado');
  const ciclosAb = state.ciclos.filter(c=>c.estado==='abierto');
  const borr = evMios.filter(e=>e.oficial!=='Sí');

  // 0. Léeme — guía para trabajar con el archivo sin el programa
  const leeme = [
    ['HHHA — Gestión de equipos biomédicos críticos'],
    ['Exportado el', hoy],
    [],
    ['RESUMEN'],
    ['Equipos en catálogo', state.equipos.length],
    ['Eventos registrados por ti', evMios.length],
    ['   · de ellos, borradores por oficializar', borr.length],
    ['Eventos automáticos (del maestro)', evAuto.length],
    ['Pendientes por resolver', pendAb.length],
    ['Ciclos correctivos abiertos', ciclosAb.length],
    [],
    ['QUÉ CONTIENE CADA HOJA'],
    ['Por resolver', 'Lo accionable: pendientes abiertos, ciclos abiertos y borradores. Pensada para imprimir y trabajar en papel.'],
    ['Eventos', 'Lo que TÚ registraste (incluye borradores; mira la columna Oficial).'],
    ['Equipos', 'Catálogo de equipos con su estado actual.'],
    ['PMP_'+year, 'Programación anual de mantención (espejo de tu carta gantt / maestro).'],
    ['Registro_MP-'+year, 'Programado (P) y Realizado (R) de la MP, por mes.'],
    ['Pendientes', 'Todos los pendientes con su estado (No iniciado / En proceso / Resuelto).'],
    ['Ciclos correctivos', 'Ciclos de falla, con apertura y cierre.'],
    ['Eventos (automáticos)', 'HOJA OCULTA. Eventos que generó el programa al conciliar el maestro: NO los registraste tú. Para verla en Excel: clic derecho sobre una pestaña → Mostrar.'],
  ];
  addPlain(XLSX.utils.aoa_to_sheet(leeme), 'Léeme', [{wch:38},{wch:82}]);

  // 1. Por resolver — para imprimir
  const prRows = [];
  pendAb.slice().sort((a,b)=>(a.fechaComp||'9999').localeCompare(b.fechaComp||'9999')).forEach(p=>prRows.push({
    'Qué': 'Pendiente', 'Estado': ESTADO_PEND_LABEL[p.estado]||p.estado,
    'N° Inv.': p.inv, 'Equipo': p.equipo||'', 'Servicio': p.servicio||'',
    'Detalle': (TIPO_PENDIENTE[p.tipo]||p.tipo)+(p.desc?(' — '+p.desc):''), 'Ejecutor': p.ejecutor||'',
    'Compromiso': fmtFecha(p.fechaComp), 'Hecho': ''
  }));
  ciclosAb.forEach(c=>{ const eq=findEquipo(c.inv); prRows.push({
    'Qué':'Ciclo abierto','Estado':'Abierto','N° Inv.':c.inv,'Equipo':eq?(eq.equipo||''):'','Servicio':eq?(eq.servicio||''):'',
    'Detalle':'Folio '+(c.folio||''),'Ejecutor':c.ingenieroAsignado||'','Compromiso':'','Hecho':''}); });
  borr.forEach(e=>prRows.push({
    'Qué':'Borrador','Estado':'Por oficializar','N° Inv.':e.inv,'Equipo':e.equipo||'','Servicio':e.servicio||'',
    'Detalle':e.tipo+(e.obs?(' — '+e.obs):''),'Ejecutor':e.ejecutor||'','Compromiso':fmtFecha(e.fecha),'Hecho':''}));
  tabla(prRows, 'Por resolver', [{wch:12},{wch:15},{wch:13},{wch:22},{wch:20},{wch:46},{wch:20},{wch:12},{wch:8}]);

  // 2. Eventos (lo que tú registraste)
  tabla(evMios.map(mapEv), 'Eventos', colsEv);

  // 3. Equipos
  const equiposRows = state.equipos.map(e => ({
    'N° Inv.': e.inv, 'N° Carpeta': e.carpeta||'', 'Serie': e.serie||'',
    'Familia': e.fam||'', 'Equipo': e.equipo||'', 'Marca': e.marca||'', 'Modelo': e.modelo||'',
    'Servicio': e.servicio||'', 'Unidad': e.unidad||'', 'Ubicación': e.ubic||'',
    'Procedencia': e.proc||'', 'Año': e.ano||'', 'VUR': e.vur||'',
    'Clasificación': e.clasif||'', 'Frecuencia MP': e.freq||'',
    'Estado': ESTADO_LABEL[e.estado]||e.estado, 'Días en estado': diasEnEstado(e),
    'Pendientes abiertos': pendientesDe(e.inv).filter(p=>p.estado!=='cerrado').length,
    'Ciclo abierto': ciclosAbiertosDe(e.inv).length > 0 ? 'Sí' : 'No'
  }));
  tabla(equiposRows, 'Equipos', [{wch:13},{wch:9},{wch:14},{wch:16},{wch:22},{wch:16},{wch:18},{wch:22},{wch:18},{wch:18},{wch:12},{wch:6},{wch:6},{wch:12},{wch:13},{wch:14},{wch:12},{wch:10},{wch:11}]);

  // 4. PMP_AAAA — espejo del maestro
  const pmpHeader = ['Fam','ID','N° Carpeta','N° Inventario','Equipo','Servicio','Unidad','Ubicación','Procedencia','Marca','Modelo','Serie','Año Instalación','Vida Útil Residual','Clasificación','ENU / Baja','Observación','Frecuencia MP','Responsable MP',...MESES];
  const pmpData = [pmpHeader];
  state.equipos.forEach((e, i) => {
    const row = [e.fam||'', i+1, e.carpeta||'', e.inv, e.equipo||'', e.servicio||'', e.unidad||'', e.ubic||'', e.proc||'', e.marca||'', e.modelo||'', e.serie||'', e.ano||'', e.vur||'', e.clasif||'', e.enu||'', '', e.freq||'', ''];
    MESES.forEach(m => row.push((e.prog||{})[m] || ''));
    pmpData.push(row);
  });
  addPlain(XLSX.utils.aoa_to_sheet(pmpData), `PMP_${year}`);

  // 5. Registro_MP-AAAA — espejo con P y R por mes
  const regHeader2 = Array(19).fill('');
  MESES.forEach(m=>{ regHeader2.push('P','R') });
  const regHeaderMonths = Array(19).fill('');
  MESES.forEach(m => { regHeaderMonths.push(m,''); });
  regHeaderMonths[3] = 'N° Inventario';
  const regData = [regHeaderMonths, regHeader2];
  state.equipos.forEach((e, i) => {
    const row = ['', i+1, e.carpeta||'', e.inv, e.equipo||'', e.servicio||'', e.unidad||'', e.ubic||'', e.proc||'', e.marca||'', e.modelo||'', e.serie||'', e.ano||'', e.vur||'', e.clasif||'', e.enu||'', '', e.freq||'', ''];
    MESES.forEach(m => {
      const reg = (e.registro||{})[m] || {};
      const prog = (e.prog||{})[m] || '';
      row.push(reg.P || prog || '', reg.R || '');
    });
    regData.push(row);
  });
  addPlain(XLSX.utils.aoa_to_sheet(regData), `Registro_MP-${year}`);

  // 6. Pendientes
  const pendRows = state.pendientes.filter(p=>!p.anulado).map(p => ({
    'ID': p.id, 'N° Inv.': p.inv, 'Equipo': p.equipo||'', 'Servicio': p.servicio||'',
    'Tipo': TIPO_PENDIENTE[p.tipo]||p.tipo, 'Descripción': p.desc||'',
    'Ejecutor': p.ejecutor||'',
    'Fecha creación': fmtFecha(p.fechaCrea), 'Fecha compromiso': fmtFecha(p.fechaComp),
    'Fecha cierre': fmtFecha(p.fechaCierre), 'Estado': ESTADO_PEND_LABEL[p.estado]||p.estado, 'Origen': p.origen||''
  }));
  tabla(pendRows, 'Pendientes', [{wch:5},{wch:13},{wch:22},{wch:20},{wch:18},{wch:42},{wch:20},{wch:14},{wch:15},{wch:13},{wch:13},{wch:14}]);

  // 7. Conflictos (si hay)
  if(state.conflictos && state.conflictos.length > 0){
    const confRows = state.conflictos.map(c => ({
      'ID': c.id, 'Tipo': c.tipo, 'N° Inv.': c.inv, 'Estado': c.estado,
      'Hoja': c.hoja||'', 'Mes': c.mes||'', 'Campo': c.campo||'',
      'Valor programa': c.valorPrograma||'', 'Valor maestro': c.valorMaestro||'',
      'Detectado': c.fechaDeteccion ? fmtFecha(c.fechaDeteccion.slice(0,10)) : '',
      'Resuelto': c.fechaResolucion ? fmtFecha(c.fechaResolucion.slice(0,10)) : '',
      'Acción aplicada': c.accionAplicada||'', 'Valor final': c.resolucionValor||''
    }));
    tabla(confRows, 'Conflictos', [{wch:5},{wch:14},{wch:13},{wch:12},{wch:9},{wch:6},{wch:8},{wch:16},{wch:16},{wch:12},{wch:12},{wch:16},{wch:12}]);
  }

  // 8. Ciclos correctivos
  if(state.ciclos && state.ciclos.length > 0){
    const cicRows = state.ciclos.map(c => ({
      'Folio SIGEM': c.folio, 'N° Inv.': c.inv, 'Estado': c.estado,
      'Apertura': fmtFecha(c.fechaApertura), 'Cierre': fmtFecha(c.fechaCierre),
      'Ingeniero asignado': c.ingenieroAsignado||'', 'Descripción inicial': c.descripcionInicial||''
    }));
    tabla(cicRows, 'Ciclos correctivos', [{wch:22},{wch:13},{wch:11},{wch:13},{wch:13},{wch:22},{wch:46}]);
  }

  // 9. Eventos (automáticos) — HOJA OCULTA
  if(evAuto.length) tabla(evAuto.map(mapEv), 'Eventos (automáticos)', colsEv);

  // Marcar como oculta la hoja de automáticos
  wb.Workbook = {Sheets: wb.SheetNames.map(n => n === 'Eventos (automáticos)' ? {Hidden:1} : {})};

  const wbout = XLSX.write(wb, {bookType:'xlsx', type:'array'});
  const blob = new Blob([wbout], {type:'application/octet-stream'});
  const url = URL.createObjectURL(blob);
  const a = el('a',{href:url, download:`hhha-export-${hoy}.xlsx`});
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
  const vis = wb.SheetNames.length - (evAuto.length?1:0);
  toast(`Excel exportado · ${vis} hoja(s)`+(evAuto.length?' + 1 oculta (automáticos)':''),'success');
}
function importData(){
  const input = el('input',{type:'file',accept:'application/json',style:{display:'none'},onchange:async e=>{
    const f = e.target.files[0]; if(!f) return;
    try{
      const txt = await f.text();
      const data = JSON.parse(txt);
      if(!data.__v) throw new Error('Archivo no válido (falta __v).');
      const msg = `Importar backup?\n· Versión: ${data.__v}\n· Equipos: ${data.equipos?.length||0}\n· Eventos: ${data.eventos?.length||0}\n· Pendientes: ${data.pendientes?.length||0}\n· Conflictos: ${data.conflictos?.length||0}\n\nReemplazará los datos actuales.`;
      if(!confirm(msg)) return;
      state = migrate(data);
      normalizarEquipos();
      state.__userActions = state.__userActions || 0;
      save();
      toast(`Importado · ${state.eventos.length} eventos`, 'success',
        {label:'Ver', fn:()=>navigate('dashboard')});
      navigate('dashboard');
    }catch(err){ toast('Error al importar: '+err.message, 'error'); }
  }});
  document.body.appendChild(input); input.click(); setTimeout(()=>input.remove(),1000);
}

//==============================================================
// SESSION RECORDER
//==============================================================
const recorder = {
  status: 'idle', // idle | recording | paused
  events: [],
  startedAt: null,
  lastEventAt: 0,
  hoverStart: null, // {el, ts}
  hoverReported: new WeakSet(),
  scrollMilestones: {}, // {view: Set(25,50,75,100)}
  el: null,
  init(){
    this.el = $('#rec-widget');
    this.makeDraggable();
    $('#rw-rec').onclick = ()=>this.start();
    $('#rw-pause').onclick = ()=>this.pause();
    $('#rw-stop').onclick = ()=>this.stop();
    $('#rw-toggle').onclick = ()=>this.toggleMin();

    // Capturar eventos globalmente
    document.addEventListener('click', e=>{
      if(this.status !== 'recording') return;
      if(e.target.closest('#rec-widget')) return;
      this.event('click', this.descTarget(e.target), e);
    }, true);
    document.addEventListener('input', e=>{
      if(this.status !== 'recording') return;
      if(e.target.closest('#rec-widget')) return;
      if(e.target.type === 'password') return;
      this.event('input', this.descTarget(e.target), e);
    }, true);
    // 'change' captura el cambio de filtros/selects con la opción elegida.
    document.addEventListener('change', e=>{
      if(this.status !== 'recording') return;
      if(e.target.closest('#rec-widget')) return;
      if(e.target.tagName === 'SELECT') this.event('change', this.descTarget(e.target));
    }, true);
    document.addEventListener('focusin', e=>{
      if(this.status !== 'recording') return;
      if(e.target.closest('#rec-widget')) return;
      this.event('focus', this.descTarget(e.target));
    }, true);
    document.addEventListener('keydown', e=>{
      if(this.status !== 'recording') return;
      if(e.target.closest('#rec-widget')) return;
      if(e.ctrlKey || e.altKey || e.metaKey || ['Escape','Enter'].includes(e.key)){
        this.event('shortcut', {...this.descTarget(e.target), key:e.key, ctrl:e.ctrlKey, alt:e.altKey, meta:e.metaKey});
      }
    }, true);
    // Hover prolongado (>2s en mismo elem, una vez por elem)
    document.addEventListener('mouseover', e=>{
      if(this.status !== 'recording') return;
      this.hoverStart = {el: e.target, ts: Date.now()};
    }, true);
    document.addEventListener('mouseout', e=>{
      if(this.status !== 'recording' || !this.hoverStart) return;
      const dur = Date.now() - this.hoverStart.ts;
      if(dur > 2000 && !this.hoverReported.has(this.hoverStart.el) && !this.hoverStart.el.closest('#rec-widget')){
        this.hoverReported.add(this.hoverStart.el);
        this.event('hover_long', {...this.descTarget(this.hoverStart.el), durMs: dur});
      }
      this.hoverStart = null;
    }, true);
    // Scroll depth por vista
    document.addEventListener('scroll', e=>{
      if(this.status !== 'recording') return;
      const t = e.target;
      if(!t || !t.scrollTop) return;
      if(!t.id && !t.tagName) return;
      const max = t.scrollHeight - t.clientHeight;
      if(max <= 0) return;
      const pct = Math.round((t.scrollTop / max) * 100);
      const view = currentView;
      this.scrollMilestones[view] = this.scrollMilestones[view] || new Set();
      [25,50,75,100].forEach(m => {
        if(pct >= m && !this.scrollMilestones[view].has(m)){
          this.scrollMilestones[view].add(m);
          this.event('scroll_depth', {pct: m, view});
        }
      });
    }, true);
    window.addEventListener('error', e=>{
      if(this.status === 'recording'){
        this.event('error',{mensaje:e.message,archivo:e.filename,linea:e.lineno});
      }
    });
    const origError = console.error;
    console.error = (...args)=>{
      if(this.status === 'recording'){
        this.event('console.error',{args: args.map(a=>String(a))});
      }
      origError.apply(console, args);
    };
  },
  descTarget(t){
    if(!t || t === document) return {};
    const tag = t.tagName ? t.tagName.toLowerCase() : '';
    const id = t.id || '';
    const cls = t.className && typeof t.className === 'string' ? t.className.slice(0,80) : '';
    const text = (t.innerText||t.textContent||'').trim().slice(0,80);
    const value = (t.type !== 'password' && t.value != null) ? String(t.value).slice(0,200) : undefined;
    const rect = t.getBoundingClientRect ? t.getBoundingClientRect() : null;
    const opcion = (tag === 'select' && t.selectedOptions && t.selectedOptions[0]) ? t.selectedOptions[0].textContent.trim().slice(0,60) : undefined;
    return {
      selector: this.selector(t),
      tag, id, cls, textoVisible: text,
      valor: value, opcion,
      coords: rect ? {x: Math.round(rect.x), y: Math.round(rect.y), w:Math.round(rect.width), h:Math.round(rect.height)} : null
    };
  },
  selector(t){
    if(!t.tagName) return null;
    const parts = [];
    let n = t;
    while(n && n !== document.body && parts.length < 5){
      let s = n.tagName.toLowerCase();
      if(n.id){ s += '#'+n.id; parts.unshift(s); break; }
      if(n.className && typeof n.className === 'string'){
        const cls = n.className.split(/\s+/).filter(Boolean).slice(0,2).join('.');
        if(cls) s += '.'+cls;
      }
      parts.unshift(s);
      n = n.parentElement;
    }
    return parts.join(' > ');
  },
  event(tipo, target, raw){
    if(this.status !== 'recording') return;
    const now = Date.now();
    // Think time: si pasaron >3s desde el último evento de usuario, registrarlo
    if(this.lastEventAt && ['click','input','focus','shortcut'].includes(tipo)){
      const idleMs = now - this.lastEventAt;
      if(idleMs > 3000){
        this.events.push({
          t: this.lastEventAt - this.startedAt,
          tipo: 'think_time', durMs: idleMs, vista: currentView
        });
      }
    }
    const ev = {
      t: now - this.startedAt,
      tipo, ...target,
      vista: currentView, params: viewParams,
      estadoApp: {
        equipos: state.equipos.length,
        eventos: state.eventos.length,
        pendientes: state.pendientes.length,
        ciclosAbiertos: state.ciclos.filter(c=>c.estado==='abierto').length,
        conflictosPend: (state.conflictos||[]).filter(c=>c.estado==='pendiente'||c.estado==='pospuesto').length,
        borradores: state.eventos.filter(e=>e.oficial!=='Sí' && !e.anulado).length,
        pendPorResolver: state.pendientes.filter(p=>!p.anulado && p.estado!=='cerrado').length
      }
    };
    if(raw && raw.clientX != null) ev.click = {x:raw.clientX, y:raw.clientY};
    this.events.push(ev);
    if(['click','input','focus','shortcut'].includes(tipo)) this.lastEventAt = now;
    this.updateUI();
  },
  start(opts){
    if(this.status === 'paused'){ this.status='recording'; }
    else { this.status='recording'; this.events=[]; this.startedAt = Date.now(); this.lastEventAt = 0; this.scrollMilestones = {}; this.hoverReported = new WeakSet(); }
    this.el.classList.remove('paused'); this.el.classList.add('recording');
    $('#rw-rec').disabled = true; $('#rw-pause').disabled = false; $('#rw-stop').disabled = false;
    this.event('rec.start', {autoStart: !!(opts && opts.silent)});
    this.updateUI();
  },
  pause(){
    if(this.status === 'recording'){
      this.status = 'paused';
      this.el.classList.remove('recording'); this.el.classList.add('paused');
      $('#rw-rec').disabled = false; $('#rw-pause').disabled = true;
      this.event('rec.pause',{});
    } else if(this.status === 'paused'){
      this.start();
    }
    this.updateUI();
  },
  stop(){
    if(this.status === 'idle') return;
    this.event('rec.stop',{});
    // Calcular métricas resumen
    const evs = this.events;
    const vistas = new Set(evs.map(e => e.vista).filter(Boolean));
    const clicks = evs.filter(e => e.tipo === 'click');
    const selectorCounts = {};
    clicks.forEach(c => { if(c.selector) selectorCounts[c.selector] = (selectorCounts[c.selector]||0)+1; });
    const clicksRepetidos = Object.values(selectorCounts).filter(n => n >= 3).length;
    const thinkTimes = evs.filter(e => e.tipo === 'think_time');
    const idleTotal = thinkTimes.reduce((a,e)=>a+(e.durMs||0), 0);
    const dur = Date.now() - this.startedAt;
    const eventosCreadosInicio = (evs.find(e=>e.estadoApp)||{}).estadoApp?.eventos || 0;
    const eventosCreadosFin = state.eventos.length;
    const sesion = {
      meta: {
        appVersion: APP_VERSION,
        ua: navigator.userAgent,
        duracionMs: dur,
        nEventos: evs.length,
        inicio: new Date(this.startedAt).toISOString(),
        fin: new Date().toISOString(),
        metrics: {
          vistasVisitadas: [...vistas],
          totalClicks: clicks.length,
          clicksRepetidos,
          thinkTimes: thinkTimes.length,
          idleMs: idleTotal,
          activeMs: Math.max(0, dur - idleTotal),
          eventosCreadosEnSesion: Math.max(0, eventosCreadosFin - eventosCreadosInicio),
          errores: evs.filter(e => e.tipo === 'error' || e.tipo === 'console.error').length,
          formErrors: evs.filter(e => e.tipo === 'form_error').length,
          modalAborts: evs.filter(e => e.tipo === 'modal_abort').length,
          hoverLong: evs.filter(e => e.tipo === 'hover_long').length
        }
      },
      eventos: evs
    };
    const stamp = new Date().toISOString().replace(/[-:]/g,'').slice(0,13);
    const blob = new Blob([JSON.stringify(sesion,null,2)],{type:'application/json'});
    const url = URL.createObjectURL(blob);
    const a = el('a',{href:url,download:`sesion-${stamp.slice(0,8)}-${stamp.slice(9,13)}.json`});
    document.body.appendChild(a); a.click(); a.remove();
    URL.revokeObjectURL(url);

    this.status = 'idle';
    this.events = [];
    this.el.classList.remove('recording','paused');
    $('#rw-rec').disabled = false; $('#rw-pause').disabled = true; $('#rw-stop').disabled = true;
    toast('Sesión exportada','success');
    this.updateUI();
  },
  updateUI(){
    const info = $('#rw-info');
    if(this.status==='idle') info.textContent = 'Detenido · 0 eventos';
    else {
      const segs = Math.floor((Date.now()-this.startedAt)/1000);
      info.textContent = `${this.status==='recording'?'Grabando':'Pausado'} · ${this.events.length} ev · ${segs}s`;
    }
  },
  toggleMin(){
    this.el.classList.toggle('minimized');
  },
  makeDraggable(){
    const hd = this.el.querySelector('.rw-hd');
    let drag = false, sx, sy, ox, oy;
    hd.addEventListener('mousedown', e=>{
      if(e.target.tagName === 'BUTTON') return;
      drag = true;
      const r = this.el.getBoundingClientRect();
      sx = e.clientX; sy = e.clientY; ox = r.left; oy = r.top;
      e.preventDefault();
    });
    document.addEventListener('mousemove', e=>{
      if(!drag) return;
      const nx = ox + (e.clientX - sx), ny = oy + (e.clientY - sy);
      this.el.style.left = Math.max(0,Math.min(window.innerWidth-50,nx))+'px';
      this.el.style.top = Math.max(0,Math.min(window.innerHeight-30,ny))+'px';
      this.el.style.bottom = 'auto'; this.el.style.right = 'auto';
    });
    document.addEventListener('mouseup', ()=>drag=false);
  }
};
setInterval(()=>{ if(recorder.status==='recording') recorder.updateUI(); }, 1000);

//==============================================================
// INIT
//==============================================================
// Barra lateral agrupada en los dos momentos del trabajo. Pendientes/Ciclos/Eventos
// no van en el menú: se acceden desde "Por resolver" y desde la ficha del equipo.
const NAV_GRUPOS = [
  ['GESTIONAR', [['porResolver','Por resolver'],['equipos','Buscar equipos'],['registroMP','Registro MP'],['dashboard','Resumen']]],
  ['REGISTRAR', [['mp','MP del mes'],['conciliacion','Conciliación']]]
];
function navBadge(k, b){
  if(k === 'porResolver'){
    const n = state.pendientes.filter(p=>!p.anulado && p.estado!=='cerrado').length;
    if(n > 0) b.appendChild(el('span',{class:'nav-badge'}, String(n)));
  }
  if(k === 'conciliacion'){
    const pend = (state.conflictos||[]).filter(c => c.estado === 'pendiente' || c.estado === 'pospuesto').length;
    if(pend > 0) b.appendChild(el('span',{class:'nav-badge'}, String(pend)));
  }
}
function buildNav(){
  const nav = $('#nav');
  nav.innerHTML = '';
  NAV_GRUPOS.forEach(([titulo, items])=>{
    nav.appendChild(el('div',{class:'s-group'}, titulo));
    items.forEach(([k,l])=>{
      const b = el('button',{'data-view':k,onclick:()=>navigate(k)}, l);
      navBadge(k,b);
      nav.appendChild(b);
    });
  });
}
function refreshNav(){
  buildNav();
  $$('#nav button').forEach(b => b.classList.toggle('active', b.dataset.view === currentView));
}

function quickSearch(){
  const input = el('input',{type:'search',placeholder:'N° Inv · serie · equipo · marca · modelo · servicio…',class:'quick-search-input',autocomplete:'off'});
  const results = el('div',{class:'quick-search-results'});
  let selected = 0;
  let filtered = [];
  function norm(s){ return (s||'').toString().toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,''); }
  function render(){
    const q = norm(input.value.trim());
    if(!q){
      results.innerHTML = '';
      results.appendChild(el('div',{class:'qs-hint'}, 'Escribe para buscar. Enter para abrir · Esc para cerrar.'));
      filtered = [];
      return;
    }
    const tokens = q.split(/\s+/).filter(Boolean);
    filtered = state.equipos.filter(eq => {
      const hay = [eq.inv, eq.serie, eq.equipo, eq.marca, eq.modelo, eq.servicio, eq.unidad, eq.carpeta].map(norm).join(' ');
      return tokens.every(t => hay.includes(t));
    }).slice(0, 12);
    results.innerHTML = '';
    if(filtered.length === 0){
      results.appendChild(el('div',{class:'qs-hint'}, 'Sin resultados.'));
      return;
    }
    filtered.forEach((eq, i) => {
      const row = el('div',{class:'qs-row'+(i===selected?' selected':''), onclick:()=>{open(eq.inv);}},
        el('div',{class:'qs-inv'}, eq.inv||'—'),
        el('div',{class:'qs-eq'},
          el('strong',{}, eq.equipo||'—'),
          el('div',{class:'qs-meta'}, `${eq.marca||''} ${eq.modelo||''} · ${eq.servicio||''} · serie ${eq.serie||'—'}`)
        ),
        eq.estado ? badgeEstado(eq.estado) : null,
        conflictosDe(eq.inv).length > 0 ? el('span',{class:'badge noop'}, conflictosDe(eq.inv).length+' conf') : null
      );
      results.appendChild(row);
    });
  }
  function open(inv){
    closeModal();
    navigate('equipo',{inv});
  }
  input.addEventListener('input', render);
  input.addEventListener('keydown', e => {
    if(e.key === 'ArrowDown'){ e.preventDefault(); selected = Math.min(filtered.length-1, selected+1); render(); }
    else if(e.key === 'ArrowUp'){ e.preventDefault(); selected = Math.max(0, selected-1); render(); }
    else if(e.key === 'Enter' && filtered[selected]){ e.preventDefault(); open(filtered[selected].inv); }
  });
  modal({title:'🔍 Buscar equipo (Ctrl+K)', body:el('div',{class:'quick-search'},
    input, results
  )});
  setTimeout(()=>{ input.focus(); render(); }, 50);
}

function bootstrap(){
  state = load();
  if(state){
    // State existente: limpiar efectos huérfanos de eventos anulados (idempotente)
    const cambios = limpiarEfectosAnulados();
    if(cambios > 0){
      save({internal:true});
      setTimeout(()=>toast(`Migración: ${cambios} inconsistencia${cambios>1?'s':''} de versiones previas corregida${cambios>1?'s':''}.`, 'success'), 600);
    }
  }
  if(!state){
    state = init();
    // Reconstruir ciclos desde eventos seed
    state.eventos.forEach(ev => {
      if(ev.tipo === 'Solicitud de trabajo' && ev.folio){
        if(!state.ciclos.find(c => c.folio === ev.folio)){
          state.ciclos.push({
            folio: ev.folio, inv: ev.inv, fechaApertura: ev.fecha,
            fechaCierre:null, estado:'abierto',
            descripcionInicial: ev.obs||'', ingenieroAsignado: ev.ejecutor||null,
            id: state.counters.ciclo++
          });
        }
      }
    });
    // Cerrar ciclos cuyo último evento de Reparación dejó operativo
    state.eventos.forEach(ev => {
      if((ev.tipo === 'Reparación' || ev.tipo === 'Recepción' || (ev.tipo === 'Visita técnica' && ev.tipoVisita==='correctiva')) && ev.estado === 'operativo' && ev.folio){
        const c = state.ciclos.find(x => x.folio === ev.folio && x.estado==='abierto');
        if(c) { c.estado='cerrado'; c.fechaCierre = ev.fecha; }
      }
    });
    // Recalcular estado de cada equipo a partir de sus eventos. Sin eventos → 'desconocido'.
    state.equipos.forEach(recalcEstadoEquipo);
    save({internal:true});
  }
  normalizarEquipos();

  buildNav();
  $('#btn-excel').onclick = exportExcel;
  $('#btn-export').onclick = exportData;
  $('#btn-import').onclick = importData;
  $('#btn-reset').onclick = resetState;
  $('#btn-theme').onclick = toggleTheme;
  $('#btn-sidebar').onclick = toggleSidebar;
  if(getPref('sidebarColapsada', false) === true) document.querySelector('.app').classList.add('sb-collapsed');
  // Aplicar tema persistido
  setTheme(getPref('theme', 'light'));
  recorder.init();
  // Auto-start del grabador si el usuario no lo deshabilitó
  if(getPref('recorderAutoStart', true) !== false){
    setTimeout(()=>recorder.start({silent:true}), 300);
  }
  // Atajo Ctrl+K (o Cmd+K) para buscador rápido global
  document.addEventListener('keydown', e=>{
    if((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')){
      e.preventDefault();
      quickSearch();
    } else if(e.key === '/' && !['INPUT','TEXTAREA','SELECT'].includes((e.target.tagName||'')) && !document.querySelector('.modal')){
      e.preventDefault();
      quickSearch();
    }
  });
  refreshStateIndicator();
  navigate('porResolver');
}
document.addEventListener('DOMContentLoaded', bootstrap);
</script>
</body>
</html>
"""

# Sustituir placeholder con el SEED (sin re-escapar; JSON ya es JS-safe excepto </script>)
seed_safe = seed_str.replace("</", "<\\/")
out = HTML.replace("__SEED_PLACEHOLDER__", seed_safe)

# Embebber SheetJS mini para parseo XLSX offline.
# OJO: solo escapamos </script> (case-insensitive), no todos los </ — eso rompería regex literales.
import re
with open("/tmp/node_modules/xlsx/dist/xlsx.mini.min.js", "r", encoding="utf-8") as f:
    sheetjs = f.read()
sheetjs_safe = re.sub(r"</(script)", r"<\\/\1", sheetjs, flags=re.IGNORECASE)
out = out.replace("__SHEETJS_PLACEHOLDER__", sheetjs_safe)

# Embebber lz-string para compresión de localStorage
with open("/tmp/node_modules/lz-string/libs/lz-string.min.js", "r", encoding="utf-8") as f:
    lzs = f.read()
lzs_safe = re.sub(r"</(script)", r"<\\/\1", lzs, flags=re.IGNORECASE)
out = out.replace("__LZSTRING_PLACEHOLDER__", lzs_safe)

# Sincronizar el número de versión visible del encabezado con APP_VERSION (una sola fuente de verdad).
_mver = re.search(r"const APP_VERSION = '([^']+)'", out)
if _mver:
    out = out.replace("__APP_VERSION__", _mver.group(1))

target = str(pathlib.Path(__file__).resolve().parent / "app.html")
pathlib.Path(target).write_text(out, encoding="utf-8")
print(f"Wrote {target}: {len(out)} bytes")

# --- Prueba de humo automática del camino crítico (Equipos, ficha, filtros, Ctrl+K, folio).
# Regla del repo: ningún cambio se da por terminado sin que esta prueba pase.
import subprocess
_smoke = pathlib.Path(__file__).resolve().parent / "tools" / "smoke_test.js"
if _smoke.exists():
    try:
        r = subprocess.run(["node", str(_smoke), target], capture_output=True, text=True, timeout=120)
        print(r.stdout, end="")
        if r.returncode == 2:
            print("⚠  Prueba de humo OMITIDA (falta jsdom). Instálalo una vez: npm install jsdom")
        elif r.returncode != 0:
            print("⚠  PRUEBA DE HUMO FALLÓ: revisa el camino crítico ANTES de entregar.")
            if r.stderr.strip():
                print(r.stderr.strip())
    except FileNotFoundError:
        print("⚠  Prueba de humo OMITIDA: no se encontró 'node' en este entorno.")
    except Exception as _e:
        print(f"⚠  Prueba de humo no pudo ejecutarse: {_e}")
else:
    print("⚠  No existe tools/smoke_test.js; no se ejecutó la prueba de humo.")

# --- Guardián (autocorrección): bloquea las CLASES de error ya cometidas (patrón incompleto,
# vistas rotas, fórmulas legacy) y avisa de código muerto / clases CSS de riesgo.
_guard = pathlib.Path(__file__).resolve().parent / "tools" / "guard.js"
if _guard.exists():
    try:
        rg = subprocess.run(["node", str(_guard), target], capture_output=True, text=True, timeout=120)
        print(rg.stdout, end="")
        if rg.returncode == 2:
            print("⚠  Guardián OMITIDO (falta jsdom). Instálalo una vez: npm install jsdom")
        elif rg.returncode != 0:
            print("⛔ GUARDIÁN: hay problemas que BLOQUEAN. NO entregues hasta corregirlos.")
            if rg.stderr.strip():
                print(rg.stderr.strip())
    except FileNotFoundError:
        print("⚠  Guardián OMITIDO: no se encontró 'node' en este entorno.")
    except Exception as _e:
        print(f"⚠  Guardián no pudo ejecutarse: {_e}")
else:
    print("⚠  No existe tools/guard.js; no se ejecutó el guardián.")
