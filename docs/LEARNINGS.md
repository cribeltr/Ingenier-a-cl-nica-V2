# LEARNINGS.md — Memoria evolutiva de HHHA

> Esta es la "memoria humana" del proyecto. No es un changelog de features
> (eso vive en build_app.py). Aquí se acumulan **trampas, patrones e
> heurísticas confirmadas** sesión a sesión.
>
> **Reglas:**
> 1. Solo se AÑADE, no se borra. Si algo se invalida, se marca `[REVISADO]` y
>    se explica por qué, pero se conserva.
> 2. Cada sesión que toca el código debe dejar al menos una entrada.
> 3. Antes de codear, lee TODO este archivo.
>
> **Formato de cada entrada:**
> ```
> ## [AAAA-MM-DD] Título corto
> - Disparador: qué cambio/pregunta lo originó.
> - Confirmado: qué se verificó (cómo, con qué prueba).
> - Heurística: la regla generalizable que queda para el futuro.
> - Dónde aplica: archivos/funciones/líneas.
> ```

---

## [2026-05-28] Bug de fechas UTC parcheado a medias

- **Disparador:** revisión general tras el ajuste v0.23 (badges de bitácora).
- **Confirmado:** las fechas se guardan como `YYYY-MM-DD`. El parse seguro
  `new Date(f+'T00:00:00')` se usa en líneas 885, 2092, 3016, 3104, pero se
  omitió en `mpDelMesEjecutada` (línea 1119) y `aplicarEfectosEvento` (línea
  1209), que usan `new Date(f)`. Reproducido en Node con TZ=America/Santiago:
  `new Date('2026-05-01').getMonth()` → 3 (abril) en vez de 4; `'2026-01-01'`
  → año 2025. Impacto: una MP del día 1 se escribe en el mes anterior (1209,
  escritura) y no se detecta como ejecutada en su mes (1119, lectura).
- **Heurística:** cuando arregles un patrón, haz `grep` del patrón completo y
  arréglalo en TODOS los sitios. Un fix aplicado en 4 de 6 lugares es la causa
  raíz de bugs futuros. Para fechas, este repo nunca debe usar `new Date(f)`
  sobre un string `YYYY-MM-DD` crudo.
- **Dónde aplica:** build_app.py líneas 1119 y 1209 (pendientes de fix);
  patrón correcto en 885, 2092, 3016, 3104.

## [2026-05-28] Divergencia recalc vs apply en el estado del equipo

- **Disparador:** misma revisión general.
- **Confirmado:** `recalcEstadoEquipo` (líneas 1097-1100) mapea
  `ev.estado==='baja'` → `'baja'`, pero `aplicarEfectosEvento` (1184-1186) no
  lo contempla y caería en el `else` → `'no_operativo'`. Hoy NO es alcanzable
  porque el formulario de evento no ofrece "baja" como estado resultante; solo
  se llega a baja por la causal MP='Baja' (camino aparte) o por `darDeBaja`.
- **Heurística:** cualquier dato derivado por dos caminos (aplicación en vivo
  vs recálculo tras anular) debe usar la MISMA lógica. Ideal: extraer un solo
  helper `mapearEstado(ev.estado)` y llamarlo desde ambos. Mientras sigan
  duplicados, todo valor nuevo de estado hay que agregarlo en los dos.
- **Dónde aplica:** build_app.py, `recalcEstadoEquipo` y `aplicarEfectosEvento`.

## [2026-05-28] Observación de diseño: badge de lote sin estilo "auto"

- **Disparador:** revisión del cambio v0.23.
- **Confirmado:** en `renderBitacora` (línea 2160) la clase `auto` (borde/fondo
  verde) se aplica a `conciliacion_auto` y `conciliacion`, pero el badge
  ⚡ Lote (`origen==='masivo'`, línea 2167) no la recibe, aun siendo también
  generado por el sistema. Es decisión de diseño, no error.
- **Heurística:** al introducir una distinción visual ("eventos generados por
  el sistema"), decidir explícitamente si TODOS los orígenes automáticos
  (`conciliacion_auto`, `conciliacion`, `masivo`) entran o no, y dejarlo escrito.
- **Dónde aplica:** build_app.py, `renderBitacora`.

## [2026-05-28] El protocolo mismo se endureció

- **Disparador:** el usuario observó que entregué archivos sin confirmar antes
  de actuar — justo lo contrario de lo que pide.
- **Confirmado:** se probó el protocolo nuevo contra el bug de fechas de hoy.
  Resultado: el paso 2 (revisar el programa completo con grep del patrón)
  habría detectado los 2 lugares omitidos. El protocolo, si se sigue, funciona.
- **Heurística:** (1) nunca actuar sin confirmar entendimiento y esperar el "sí"
  del usuario — es la REGLA #0. (2) Hablar siempre en español, breve y sin
  tecnicismos; el usuario es experto en su trabajo, no en computación.
  (3) Simular es obligatorio en cada cambio, no opcional.
- **Dónde aplica:** CLAUDE.md (REGLA #0, pasos 2 y 4, sección de trato).

## [2026-05-28] Regla nueva: pensar como experto, no literal

- **Disparador:** el usuario notó que al pedir "diseño" se le entregaban cambios
  literales y superficiales (ej. intercambiar emojis) en vez de pensamiento de
  diseñador.
- **Confirmado:** se agregó la sección "Pensar como experto, no ejecutar literal"
  a CLAUDE.md y se reforzó el bucle de auto-mejora con el uso diario.
- **Heurística:** ante cualquier pedido (sobre todo diseño), entender el
  propósito real, simular cómo se vive, y proponer con criterio; si la idea del
  usuario no es la mejor para su objetivo, decirlo con respeto. Nunca ejecutar
  la frase al pie de la letra sin comprenderla.
- **Dónde aplica:** CLAUDE.md (sección nueva + "Cómo mejora el sistema con tu uso").

## [2026-05-28] Bug de fechas CORREGIDO (v0.24)

- **Disparador:** instrucción del usuario "revisa, ajusta, implementa, simula".
- **Confirmado:** se aplicó `+'T00:00:00'` en `mpDelMesEjecutada` y
  `aplicarEfectosEvento` (build_app.py y app.html). Simulado en TZ
  America/Santiago: una MP del 2026-05-01 ahora cae en Mayo (antes caía en
  Abril) y se detecta como ejecutada en su mes. Regresión: 6 parseos seguros,
  0 inseguros; los 4 lugares previos quedaron intactos. Versión subida a 0.24.
- **Heurística:** confirmada la regla anterior — al arreglar un patrón, buscarlo
  en todo el archivo. Aquí faltaban 2 de 6 sitios.
- **Dónde aplica:** RESUELTO. Reemplaza el estado "pendiente" de la entrada del
  bug de fechas más arriba.

## [2026-05-28] Integrado el TRASPASO.md del chat constructor

- **Disparador:** el chat que construyó el programa entregó `TRASPASO.md` con
  decisiones de diseño, problemas conocidos y supuestos. Se guardó en
  `docs/TRASPASO.md`.
- **Confirmado:** al cruzarlo con el código, el `TRASPASO.md` NO mencionaba el
  bug de fechas (su hueco principal). Sí aporta info valiosa que no estaba en
  ningún lado, en especial:
  - Eventos auto-completados (v0.21) **no son idempotentes**: reimportar el
    mismo maestro puede duplicar si entremedio se editó el equipo.
  - Sin throttle en clicks → confirmar una MP dos veces seguidas puede crear
    dos registros.
  - Patrón de closures frágil (`VIEWS.equipo` necesita `setTab`); olvidarlo deja
    botones no-op (fue el bug v0.19).
  - 9 supuestos de regla de negocio SIN ratificar (folio opcional, día 15 del
    evento sintético, MP fuera de mes permitida, etc.) → ver §4 de TRASPASO.md.
- **Heurística:** un traspaso escrito por otro agente puede tener huecos;
  siempre cruzarlo contra el código antes de confiar en él.
- **Dónde aplica:** docs/TRASPASO.md (referencia); ítems técnicos pendientes.

## [2026-05-28] Carga de datos reales desde un export XLSX (v0.25)

- **Disparador:** el usuario pidió "entrégame el programa sin ningún dato y usa
  estos", adjuntando un export del propio sistema (hhhaexport…xlsx, hojas
  Eventos / Pendientes / Ciclos correctivos). Tras confirmar (eligió "solo los
  datos del Excel"), se reemplazaron los datos demo por los suyos reales.
- **Confirmado:**
  - El export es una SALIDA con pérdida: NO trae el catálogo de equipos ni la
    programación MP anual. Esos se conservaron del seed previo (893 equipos +
    matriz). Solo se reemplazaron eventos (85) y pendientes (34); tareas a 0.
  - La traducción XLSX→interno invierte EXACTAMENTE el mapeo de `exportExcel()`
    (build_app.py ~4793-4838): cada columna ↔ su campo. Fechas DD-MM-YYYY →
    YYYY-MM-DD por split de texto (NUNCA `new Date` sobre crudo: invariante de
    fechas). Tipo de pendiente: etiqueta → clave (inverso de `TIPO_PENDIENTE`).
  - Los ciclos NO se guardan en el seed: `bootstrap()` los reconstruye desde las
    Solicitudes de trabajo con folio. Verificado en Node: 3 solicitudes → 3
    ciclos abiertos idénticos a la hoja Ciclos. 0 Reparaciones operativas → los
    3 quedan "abierto" (coincide).
  - Los estados de equipo NO se guardan: `recalcEstadoEquipo` los deriva del
    evento de mayor fecha. Simulado: 71 operativo, 5 no_operativo, 817
    desconocido (equipos sin actividad aún); 76 equipos con eventos.
  - Causales C3/C8 (campo `resultado` de MP) se preservan; 'Creado por'=Cristian
    y 'Técnico' vacío en los 85 (sin pérdida).
  - Regresión bug fechas v0.24: 0 MP corridas de mes; una MP del 2026-04-01
    (día 1) se detecta como ejecutada en abril. El fix sigue firme con datos reales.
- **Heurística:**
  1. Un export del sistema sirve para RE-INGESTAR, pero es con pérdida: cruzar
     sus columnas contra la función exportadora y conservar del seed lo que el
     export no trae (catálogo, programación, estados derivados, ciclos).
  2. Preferir reconstruir lo DERIVADO (ciclos, estados) con la lógica del propio
     programa, no inyectarlo, para no divergir.
  3. `init()` ahora respeta `tipo`/`origen` del seed si vienen; antes los derivaba
     del texto y reclasificaba mal 2 pendientes ("Reprogramación MP" con desc
     "abril"). Regla: la carga del seed no debe "adivinar" lo que el dato afirma.
- **Dónde aplica:** seed.json (datos); build_app.py `init()` (respeta
  tipo/origen) + `target` relativo a `__file__` + CHANGELOG v0.25; app.html
  regenerado. Conversor reproducible en `tools/excel_a_seed.py` (verificado:
  reproduce el seed byte a byte); insumo en `docs/origen_datos_20260528.xlsx`.

## [2026-05-28] Cierre de ciclo por Recepción + Reparación "en servicio técnico" (v0.26)

- **Disparador:** caso real del usuario (equipo 2-117812): reparado en el servicio
  técnico externo pero aún sin retornar al hospital; no debía cerrarse el ciclo
  hasta que el equipo volviera operativo. El programa no lo permitía bien.
- **Confirmado:** el cierre automático del ciclo vivía en 3 puntos del MISMO patrón
  y solo contemplaba Reparación / Visita correctiva operativa:
  1. `aplicarEfectosEvento` (registro en vivo, ~1225).
  2. reconstrucción al cargar el seed en `bootstrap` (~5248).
  3. reapertura al anular (~4291), con doble condición (el `if` y el `otraOp`).
  La "Recepción" ("equipo retorna") NO cerraba el ciclo → un equipo reparado afuera
  y recibido dejaba el ciclo abierto para siempre. Se agregó `Recepción` operativa
  en los 3 puntos (4 condiciones) y se añadió "en servicio técnico" al estado
  resultante del formulario de Reparación.
  - Simulado en Node con 2-117812: carga ciclo abierto → Recepción operativa CIERRA
    → anular REABRE → Reparación "en servicio técnico" NO cierra (equipo queda
    en_servicio_tecnico) → Recepción operativa CIERRA. Los 5 pasos ✅.
  - Regresión: la carga del seed sigue dando 85 eventos / 34 pendientes / 3 ciclos
    abiertos (no hay Recepciones en el seed; la nueva condición no dispara).
- **Heurística:** confirmada la regla de oro del repo: el cierre/reapertura de ciclo
  es UN patrón replicado en 3 sitios (4 condiciones); tocar uno obliga a tocar
  todos. El `grep` de `cerrarCiclo` / `'abierto'` / `'cerrado'` antes de editar
  evitó dejar un sitio sin cambiar.
- **Pendiente detectado (no tocado):** inconsistencia de texto del tipo "Envío":
  `TIPOS_EVENTO` usa 'Envío a servicio técnico' pero el seed/export usa 'Envío a
  Serv. Técnico'. Conviene unificar para que filtros y `DOCS_CORRECTIVO` (~4130) lo
  reconozcan igual. Anotado para una próxima sesión.
- **Dónde aplica:** build_app.py `aplicarEfectosEvento`, `bootstrap`
  (reconstrucción), anulación (reapertura) y formulario Reparación; CHANGELOG
  v0.26; app.html regenerado.

## [2026-05-28] El número de versión del encabezado quedaba "pegado" (v0.27)

- **Disparador:** el usuario notó que el programa mostraba "v0.23" en el encabezado
  aunque APP_VERSION ya iba en 0.26.
- **Confirmado:** el header tenía el número escrito a mano (`<small>… v0.23</small>`,
  línea ~782), independiente de APP_VERSION (~802). Subir la versión no lo tocaba.
  Se reemplazó por el placeholder `__APP_VERSION__`, que build_app.py sustituye con
  el valor real de APP_VERSION (regex) al generar. Verificado: el encabezado quedó
  en v0.27, sin placeholder residual.
- **Heurística:** todo dato que el usuario ve y que también existe como constante
  debe derivarse de la constante (una sola fuente de verdad), nunca duplicarse a
  mano; si no, se desincroniza. Conviene revisar otros textos "duplicados" del HTML.
- **Observación de uso (no es bug):** el usuario trabajaba sobre un app.html v0.25
  con datos antiguos (1035 eventos en localStorage), no sobre su seed de 85. Chrome
  guarda el estado por ruta del archivo: reemplazar app.html en la misma carpeta
  conserva el localStorage viejo. Para ver el seed nuevo: ↻ Reset o carpeta nueva.
- **Dónde aplica:** build_app.py (header ~782 + sustitución final de
  `__APP_VERSION__`); CHANGELOG v0.27.

## [2026-05-28] Folio del ciclo: preselección + aviso (v0.28)

- **Disparador:** el usuario reportó que en la Reparación "el folio no se carga" y
  que si la solicitud sigue abierta debería mostrarlo.
- **Confirmado:** el campo folio era `ciclosAb.length ? <select con '— sin ciclo —'
  primero> : <input mudo>`, repetido idéntico en 5 formularios (Visita, Orden de
  Compra, Envío, Recepción, Reparación). Con ciclo abierto el folio SÍ estaba en la
  lista, pero el `<select>` arrancaba en "— sin ciclo —" (no preseleccionado) → el
  usuario debía abrirlo y elegir; si no elegía, la Reparación operativa guardaba
  folio vacío y NO cerraba el ciclo. Sin ciclo abierto: casilla muda sin explicación.
- **Arreglo:** helper único `folioCicloControl(ciclosAb)` que preselecciona el ciclo
  abierto (`sel.value = ciclosAb[0].folio`; "— sin vincular —" al final) o entrega un
  input manual si no hay. Reparación y Recepción muestran `avisoSinCicloAbierto()`
  (notice warn) cuando no hay ciclo. Validado: `node --check` OK; el helper precarga
  "19-3788" con ciclo y devuelve input sin ciclo; 5 usos + 1 definición.
- **Heurística:** (1) un `<select>` de vinculación debe venir preseleccionado al valor
  más probable, no en una opción vacía, o el usuario cree que "no carga". (2) Una
  casilla sin datos debe explicar por qué (aviso), no quedar muda. (3) La expresión
  repetida 5 veces se unificó en un helper → menos código y un solo lugar que tocar
  (alineado con el objetivo de simplificar la interfaz).
- **Dónde aplica:** build_app.py helpers `folioCicloControl` / `avisoSinCicloAbierto`
  y los 5 formularios de evento; CHANGELOG v0.28.

## [2026-05-28] Fase 1 rediseño: pendientes accionables + pantalla "Por resolver" (v0.29)

- **Disparador:** el usuario quiere un programa que lo empuje a RESOLVER, no solo a
  registrar; pendientes con un estado inicial que "obligue"; pantalla de inicio
  accionable. (Aprobó la dirección "de archivador a centro de acción".)
- **Análisis de 13 sesiones:** vistas realmente usadas = dashboard, equipos,
  conciliación, ficha de equipo; ciclos/pendientes/eventos como pestañas casi no se
  abren (1 de 13). Más dudas en la ficha del equipo (28 pausas) y conciliación (14,
  con una mirada de 54 s al filtro). 32 clics en "← Volver" (navegación ir-y-volver).
- **Confirmado en código:** estados de pendiente eran 'creado' (auto) / 'abierto'
  (manual) / 'cerrado', inconsistentes; ~12 lugares cuentan `!== 'cerrado'`.
- **Hecho:** estados **No iniciado → En proceso → Resuelto** (internos
  'no_iniciado'/'en_proceso'/'cerrado'; se CONSERVA 'cerrado' como final para no
  tocar los ~12 conteos). Migración en `init()` y `migrate()` ('creado'/'abierto' →
  'no_iniciado'). Helpers `normalizarEstadoPend`, `badgePend`, `cambiarEstadoPend`.
  Botones rápidos "Empezar"/"Resolver" en la tabla. Nueva vista `porResolver` como
  inicio (bandeja: vencidos, no iniciados, en proceso, ciclos abiertos, borradores
  por oficializar, conflictos). "Dashboard" pasa a "Resumen". Badge en el menú.
- **Validado:** `node --check` OK; migración 34 pendientes → 34 'no_iniciado';
  porResolver cuenta 2 vencidos / 32 no iniciados / 3 ciclos / 31 borradores;
  regresión `!== 'cerrado'` intacta (34 activos de 34).
- **Heurística:** (1) el estado inicial debe tener un nombre que empuje a actuar
  ("No iniciado"), no neutro ("creado"). (2) Para anti-procrastinación, la pantalla
  de inicio muestra ACCIONES, no números. (3) Conservar el valor interno final
  ('cerrado') y cambiar solo la etiqueta visible evita tocar N conteos.
- **Pendiente de afinar con el usuario:** qué cuenta el badge del menú (hoy =
  pendientes activos, no incluye ciclos/borradores); el diseño visual moderno y las
  ventanas flotantes (fase siguiente); el Excel autónomo (fase siguiente).
- **Dónde aplica:** build_app.py (ESTADO_PEND_LABEL, normalizarEstadoPend, badgePend,
  cambiarEstadoPend, init, migrate, crearPendienteAuto, nuevoPendiente, filtro selEst,
  selector de edición, renderPendientesTabla, exportExcel, buildNav, VIEWS.porResolver,
  bootstrap/resetState); CHANGELOG v0.29.

## [2026-05-28] Look moderno aplicado vía capa de override (v0.30)

- **Disparador:** el usuario aprobó la muestra de diseño (docs/muestra_diseno.html)
  y pidió aplicarla a todo el programa, manteniendo claro/oscuro.
- **Hecho:** en vez de reescribir ~400 líneas de CSS (riesgoso), se añadió una **capa
  de estilo moderno al final del `<style>`** que sobre-escribe por cascada las
  propiedades clave de los selectores existentes (radios mayores, sombras suaves, nav
  tipo "pastilla", modal con `backdrop-filter: blur` y esquinas redondeadas). No se
  tocó ningún selector ni la estructura → no rompe funcionalidad. `VIEWS.porResolver`
  reescrita con tarjetas `.pr-card` (banda de color por urgencia: rojo/gris/ámbar/teal).
- **Validado:** `node --check` OK; clases nuevas presentes; conteos de Por resolver
  intactos (2 vencidos / 32 no iniciados / 3 ciclos / 31 borradores); tema conservado.
- **Heurística:** para un restyle amplio de bajo riesgo en un CSS grande, una **capa de
  override al final** (misma especificidad, gana por orden de aparición) moderniza todo
  sin editar cada regla ni arriesgar romper. Deuda asumida: el CSS base y el override
  coexisten; conviene consolidar si el diseño se estabiliza.
- **Dónde aplica:** build_app.py (`<style>` capa final + `VIEWS.porResolver`);
  CHANGELOG v0.30. Falta (fases siguientes): Excel autónomo, simplificar el menú,
  y pulir vista por vista (ficha de equipo, conciliación) con el mismo lenguaje.

## [2026-05-28] Menú simplificado con desplegable "Más" (v0.31)

- **Disparador:** el usuario eligió simplificar el menú (8 pestañas = ruido). El
  análisis de sesiones mostró que solo 4 vistas se usan seguido.
- **Hecho:** `NAV_PRINCIPAL` (Por resolver · Equipos · Conciliación · MP del mes)
  arriba; `NAV_SECUNDARIO` (Resumen · Pendientes · Ciclos · Eventos) en un desplegable
  "Más ▾". No se elimina nada; las vistas siguen accesibles (y también desde "Por
  resolver"). El botón "Más" se marca activo si la vista actual es secundaria. Cierre
  al hacer click fuera con un listener único (flag `window.__navMoreBound`).
- **Validado:** `node --check` OK; las 8 `VIEWS` siguen existiendo; desplegable presente.
- **Heurística:** esconder ≠ eliminar; el análisis de uso real decide qué va arriba.
  Centralizar las listas (`NAV_PRINCIPAL`/`NAV_SECUNDARIO`) evita duplicarlas entre
  `buildNav` y `refreshNav`.
- **Dónde aplica:** build_app.py (NAV_PRINCIPAL/SECUNDARIO, navBadge, buildNav,
  refreshNav, CSS `.nav-more`); CHANGELOG v0.31. Falta: Excel autónomo y pulir vistas.

## [2026-05-28] Excel autónomo: hoja oculta + guía + "Por resolver" (v0.32)

- **Disparador:** el usuario quiere que el Excel exportado sirva como respaldo de
  trabajo SIN el programa, con lo automático (del maestro) en hoja oculta y lo suyo
  aparte; y poder trabajar en papel.
- **Hecho:** `exportExcel()` reestructurado. Hojas: **Léeme** (guía + totales),
  **Por resolver** (pendientes abiertos + ciclos + borradores, con columna "Hecho"
  para tildar en papel), **Eventos** (solo lo registrado por el usuario, incluye
  borradores), Equipos, PMP, Registro_MP, Pendientes, Conflictos, Ciclos, y
  **"Eventos (automáticos)" OCULTA** (origen `conciliacion`/`conciliacion_auto`).
  Tablas con `!cols` y `!autofilter`. Ocultar vía `wb.Workbook.Sheets[].Hidden=1`.
- **Validado:** SheetJS mini escribe/relee la hoja oculta; prueba generando un xlsx
  con el seed + 1 evento auto: 9 hojas, "Eventos (automáticos)" oculta, evMios=85 /
  evAuto=1, por resolver=34, borradores=31.
- **Heurística:** SheetJS community SÍ soporta hojas ocultas (`Workbook.Sheets[].Hidden`),
  `!autofilter` y `!cols`; freeze panes no es confiable → se omitió. Criterio "lo que
  yo no registré" = origen automático de conciliación (no 'masivo' ni manual).
- **Pendiente de confirmar:** si los eventos 'masivo' (registro en lote de MP) deben ir
  también a la hoja oculta. Pulir vista por vista (ficha equipo, conciliación) es opcional.
- **Dónde aplica:** build_app.py `exportExcel()`; CHANGELOG v0.32.

## [2026-05-28] BUG MP del mes: la realización vive en la matriz, no en eventos (v0.33)

- **Disparador:** el usuario filtró Febrero + Pendientes y aparecían equipos cuya MP YA
  estaba hecha en la carta gantt (`registro.Feb.R='Si'`) pero sin evento. "Se hicieron en
  febrero, no son pendientes."
- **Confirmado con su backup real:** `mpDelMesEjecutada` miraba SOLO eventos. Equipo
  2-116070 tenía `registro.Feb.R='Si'` sin evento MP en feb → contado como pendiente. A
  nivel febrero: **300 "pendientes" falsos de 301** programadas (casi todo, porque su
  realización vive en la matriz, no en eventos uno a uno).
- **Hecho:** `resultadoMPMes()` y `mpEstadoMes()` consideran AMBAS fuentes (evento del mes
  + matriz `registro[mes].R` del año vigente). Estados: ejecutada (Si) / reprogramada
  (C1-C8) / otro (FS,NU,Baja,No) / pendiente (nada). `mpDelMesEjecutada` deriva de
  `mpEstadoMes`. Aplicado en `renderSumMesesMP`, `renderSumEjecutoresMP`, ficha del equipo
  y `VIEWS.mp` (filtro + etiqueta). El filtro "Reprogramadas" pasa a mirar el resultado.
  Validado: 2-116070 feb → ejecutada; febrero 247 ejecutadas / 51 reprog / 1 pendiente.
- **Heurística:** cuando un dato existe en DOS representaciones (matriz agregada de la
  carta gantt vs eventos individuales), toda lógica de "hecho/pendiente" debe consultar
  ambas mediante UN helper. El usuario registra la realización en la matriz (al subir el
  maestro), no como eventos uno a uno: por eso el bug era masivo.
- **Mejoras:** MP del mes con flechas ‹ › + selector de año (antes el año quedaba fijo).
  Grabador: captura los avisos/toasts (resultado de cada acción), el cambio de filtros con
  la opción elegida, y más contexto de estado (conflictos, borradores, por resolver).
- **Limitación:** la matriz `registro` no guarda año; se asume el año vigente. Navegar a
  otro año usa solo eventos. (A revisar si algún día se maneja multi-año en la matriz.)
- **Dónde aplica:** build_app.py (`resultadoMPMes`/`mpEstadoMes`/`mpDelMesEjecutada`,
  `renderSumMesesMP`, `renderSumEjecutoresMP`, `VIEWS.mp`, `recorder`, `toast`); CHANGELOG v0.33.

## [2026-05-28] Cacería proactiva: el estado del equipo también ignoraba la gantt (v0.34)

- **Disparador:** el usuario preguntó por qué no vi venir el bug de MP. **Causa real de mi
  falla:** validé con el seed (donde las MP son eventos), no con su backup real (donde la
  actividad vive en la matriz), y no simulé su flujo completo aunque me lo describió. Hice
  una cacería con sus datos reales.
- **Hallazgo (mismo patrón):** `recalcEstadoEquipo` derivaba el estado SOLO de eventos →
  811 de 894 equipos "Desconocido". De esos, 31 tenían causal de no-operatividad en la
  gantt (C2=15, C3=11, Baja=5): marcarlos a todos operativo habría repetido el error.
- **Hecho:** sin eventos de estado, se infiere de la matriz (`MP_CAUSAL_ESTADO`: C2→serv.
  técnico, C3/FS/NU→no operativo, Baja→baja); si no hay falla → operativo. Resultado:
  858 operativo / 16 no op / 15 serv. técnico / 5 baja / 0 desconocido.
- **Auditoría completa (datos reales):** 0 IDs duplicados, 0 huérfanos, 0 fechas corridas,
  contadores OK, MP por mes coherente con la gantt en los 12 meses. Sin otros bugs de integridad.
- **Heurística de PROCESO (la importante):** validar SIEMPRE con el backup real del usuario
  y simular su flujo de punta a punta, no el seed ni funciones aisladas. Las demoras
  (`think_time` altos) en `sesiones/` son señal de BUG, no solo de UX. Todo dato con doble
  representación (matriz/eventos) debe cruzarse en TODA la lógica.
- **Pendiente:** idempotencia al reimportar el maestro (no verificable sin el `.xlsm` del usuario).
- **Dónde aplica:** build_app.py (`MP_CAUSAL_ESTADO`, `estadoDesdeMatriz`,
  `recalcEstadoEquipo`); CHANGELOG v0.34.

## [2026-05-28] Verificada la idempotencia de la conciliación del maestro

- **Disparador:** riesgo anotado en TRASPASO.md ("reimportar el maestro puede duplicar").
  El usuario sube el maestro cada mañana, así que era crítico confirmarlo.
- **Verificado con SU maestro real** (`ProgramaciónMP_2026.xlsm`, 893/894 equipos) y SU
  backup, replicando `parsearMaestro` + `compararMaestro` + `registrarOActualizarConflicto`
  en Node:
  - Resubir sobre su estado actual: 3 subidas → 0 conflictos / 0 auto / 0 sintéticos, sin cambios.
  - Desde estado vacío: 1ª subida crea 3337 auto-completados + 961 eventos sintéticos (las MP
    de la gantt); 2ª y 3ª → 0/0/0. Total estable en 1046 eventos.
  - **Conclusión: la conciliación ES idempotente.** La doble protección lo evita: celda ya
    escrita (`vp===vm` → no reescribe) y `yaExiste` verifica evento MP del mes (→ no recrea).
- **Observación:** la 1ª conciliación desde cero convierte la gantt en ~961 eventos sintéticos
  (`origen='conciliacion_auto'`). Tras v0.33/0.34 la lógica ya lee la matriz directamente, así
  que esos sintéticos son redundantes pero inofensivos (dan trazabilidad en bitácora y van a la
  hoja oculta del Excel). A considerar si algún día se quiere aligerar.
- **Dónde aplica:** verificación (sin cambio de código); confirma `compararMaestro`.

## [2026-05-28] Rediseño a barra lateral izquierda + columnas de Equipos (v0.35)

- **Disparador:** el usuario pidió, con una referencia (`ref.html`, otra versión de HHHA con
  sidebar oscuro), una barra lateral izquierda con el apartado Equipos y columnas específicas.
- **Hecho:** layout `.app` pasa de grid por filas (header+main) a grid por columnas
  (sidebar 232px + content[topbar+main]). Barra lateral oscura fija (#0f172a) con TODOS los
  apartados (se elimina el desplegable "Más"), activo en `--accent`. Herramientas movidas a
  una topbar delgada. `VIEWS.equipos` con 13 columnas (ID, N° Carpeta, N° Inventario, Equipo,
  Servicio, Unidad, Ubicación, Procedencia, Marca, Modelo, Estado, Pendientes, Días en estado).
- **Validado:** `node --check` OK; sidebar/topbar/columnas presentes; "Más" eliminado.
- **Nota de proceso:** `ref.html` era de otra implementación (clases Tailwind); se extrajo el
  CONCEPTO de diseño y se reimplementó en build_app.py (fuente de verdad), no se copió el HTML.
- **Pendiente de feedback visual** (no se pudo renderizar aquí). El grabador flotante queda
  sobre el sidebar (es arrastrable; a reubicar si molesta).
- **Dónde aplica:** build_app.py (HTML app/sidebar, CSS layout, `buildNav`/`refreshNav`,
  `VIEWS.equipos`); CHANGELOG v0.35.

## [2026-05-28] Sidebar agrupado + Equipos como centro de consulta (v0.36)

- **Disparador:** el usuario pidió simplificar (menos ventanas/redundancia), separar sus 2
  momentos (registrar / gestionar) y poder responder preguntas al vuelo (equipos en servicio
  técnico, cuántos monitores por servicio, qué MP falta por ejecutor).
- **Hallazgo clave:** la tabla Equipos YA respondía esas preguntas (búsqueda + filtros);
  faltaba hacerlo evidente. Demostrado con sus datos: 15 en servicio técnico; 77 monitores en
  Medicina, 53 en UPC Adulto, etc. → no se inventó, se hizo más directo.
- **Hecho:** barra lateral en 2 grupos (GESTIONAR: Por resolver, Equipos, Resumen / REGISTRAR:
  MP del mes, Conciliación). Pendientes/Ciclos/Eventos salen del menú (siguen accesibles). En
  Equipos, accesos rápidos con conteo (En servicio técnico / No operativos / Con pendientes /
  Todos) y, para no operativo / servicio técnico, el encargado (`encargadoDe`).
- **Pendiente de esta propuesta:** unificar las 3 ventanas de un evento (editar/anular/
  oficializar) en una sola — es el refactor más delicado, se hará aparte y verificado.
- **Heurística:** antes de "agregar para responder una pregunta", verificar si los filtros
  existentes ya la responden; muchas veces el problema es visibilidad, no falta de función.
- **Dónde aplica:** build_app.py (`NAV_GRUPOS`, `buildNav`, `encargadoDe`, `VIEWS.equipos`
  accesos rápidos, CSS sidebar/quick-access); CHANGELOG v0.36.

## [2026-05-28] Equipos como planilla tipo Excel (v0.37)

- **Disparador:** el usuario está acostumbrado a Excel y pidió la vista de Equipos como
  planilla: ordenar por cualquier columna, filtro en cada columna, y botones para registrar
  evento/pendiente desde la fila.
- **Hecho:** se reescribió `VIEWS.equipos` con columnas declarativas (`COLS`: key, label,
  getter, lista/num). Ordenar por clic en el título (▲/▼); filtro por columna (select de
  valores únicos para categóricas, input "contiene" para texto/números). Botones por fila
  "➕ Evento" / "➕ Pend." / "Ficha". Los accesos rápidos setean los filtros; la navegación
  desde el dashboard (params.estado/servicio) se traduce a filtros de columna. Se quitaron los
  3 selects redundantes del toolbar; queda la búsqueda global.
- **Validado:** `node --check` OK; COLS/th-sort/filtros-col/botones presentes; selects viejos
  eliminados. El filtro de Estado compara por etiqueta (`ESTADO_LABEL`) y coincide con el
  getter de esa columna.
- **Heurística:** columnas declarativas (un array de definición) hacen que encabezados,
  filtros y celdas se generen de forma uniforme y sea trivial agregar/ordenar columnas.
- **Dónde aplica:** build_app.py (`VIEWS.equipos` completa, CSS `.th-sort`/`.filtros-col`);
  CHANGELOG v0.37.

## [2026-05-28] Vista "Registro MP" (carta gantt navegable) (v0.38)

- **Disparador:** el usuario quiere una vista idéntica a la hoja Registro_MP-2026 + Estado /
  Días en estado / Pendientes al final, con filtro en todas las columnas, clic → ficha y
  poder colapsar los meses fácilmente.
- **Hecho:** `VIEWS.registroMP` reutiliza el patrón de planilla (COLS declarativas + orden +
  filtro por columna). Columnas: identificación completa (15: ID, Carpeta, Inventario, Equipo,
  Servicio, Unidad, Ubicación, Procedencia, Marca, Modelo, Serie, Año, VUR, Clasificación,
  Frecuencia) + 12 meses con P y R (24 columnas) + Estado / Días / Pendientes. Botón
  "Ocultar/Mostrar meses" (preferencia recordada) para colapsar las 24 columnas. P =
  `registro.P || prog`; R = `registro.R`; R='Si' en verde, C1-C8 en ámbar. "Abrir" → ficha.
  En el menú, grupo GESTIONAR.
- **Validado:** `node --check` OK; vista/menú/colapso/estilo presentes; muestra con datos
  reales coherente con la matriz (2-115361: Feb P:X R:Si, May P:X R:Si…).
- **Nota:** 894 equipos × ~42 columnas; render limitado a 500 filas, filtrar agiliza.
- **Dónde aplica:** build_app.py (`VIEWS.registroMP`, `NAV_GRUPOS`, CSS `.mp-col`); CHANGELOG v0.38.

## [2026-05-29] La lista de Equipos quedaba VACÍA: número en columna de texto (v0.39)

- **Disparador:** el usuario reportó que al importar datos la lista de Equipos no se ve.
- **Reproducido headless (jsdom):** cargando `app.html` e importando respaldos reales de
  `data/`, navegar a **Equipos** lanzaba `TypeError: a.localeCompare is not a function`
  (en `valoresUnicos`, al ordenar el filtro de columna) → el `render()` se aborta y la
  tabla queda en 0 filas. **Registro MP** (misma técnica de planilla) fallaba idéntico.
  El resto de las vistas (Resumen, MP del mes, Pendientes, Ciclos, Eventos, Conciliación)
  funcionaba: solo 2 de 9 rotas.
- **Causa raíz (dato):** 18 equipos traen `modelo` y 3 traen `ubic` como **número**
  (ej. modelo 840/980, ubic 501) en el seed y en TODOS los backups. Las planillas de
  v0.37 (Equipos) y v0.38 (Registro MP) ordenan/filtran columnas categóricas con
  `String.prototype.localeCompare`, que no existe en un Number → excepción.
- **Arreglo (doble, raíz + defensa):**
  1. `normalizarEquipos()` (nueva) convierte a texto los campos de identificación del
     equipo (`fam,equipo,servicio,unidad,ubic,proc,marca,modelo,serie,clasif,freq`).
     Se llama en `bootstrap` (cubre carga del seed y de respaldo) y tras `migrate` en la
     importación. Arregla de paso búsqueda y export (quedan parejos como texto).
  2. Defensa en las DOS planillas: `valoresUnicos`, el orden y el filtro por columna
     envuelven el valor en `String()` para no caerse nunca más ante un número suelto.
- **Verificado headless:** Equipos y Registro MP muestran 894 equipos; el filtro por la
  columna Modelo con el valor numérico "840" devuelve 8 equipos; filtro por Servicio,
  abrir ficha (con PMP/historial) y Ctrl+K funcionan; 0 errores. Probado con 3 backups.
- **Heurística:** (1) en una planilla genérica por columnas, un getter categórico DEBE
  garantizar texto, o `localeCompare` revienta la vista entera. Coercionar en el ÚNICO
  punto donde se ordena/compara no basta si hay varias planillas: arreglar en TODAS
  (aquí 2 vistas × 3 puntos) + normalizar el dato. (2) Un error JS no atrapado en
  `render()` no deja la lista "filtrada en vacío": la deja **rota y muda**; si una vista
  sale vacía sin causa de datos, sospechar de una excepción en el dibujado.
- **Dónde aplica:** build_app.py (`normalizarEquipos`, `CAMPOS_TEXTO_EQUIPO`, `bootstrap`,
  handler de importar, `VIEWS.equipos` y `VIEWS.registroMP` en `valoresUnicos`/orden/filtro);
  CHANGELOG v0.39; app.html regenerado.

## [2026-05-29] Patrón raíz de los bugs y prueba de humo permanente

- **Disparador:** tras arreglar la lista de Equipos vacía (v0.39), el usuario pidió
  aprender del error y dejar un mecanismo que impida repetirlo.
- **Patrón común (mirando todos los bugs del proyecto):** casi todos nacen igual —
  se modifica una **función grande y compartida** (una vista, `recalcEstadoEquipo`,
  la lógica de MP) y se valida con el **seed** o solo con `node --check` (sintaxis),
  **sin ejecutar el camino básico con los datos reales**. Casos:
  · v0.33/v0.34: lógica de MP/estado validada con el seed (donde la MP es evento), no
    con el backup real (donde vive en la matriz) → bug masivo.
  · v0.39: planillas nuevas (v0.37/v0.38) validadas con `node --check` y muestras, sin
    abrir la vista con los datos reales → un `modelo` numérico tiraba toda la pantalla.
  El **tipo** de error es siempre el mismo: *cambio en código compartido + verificación
  que no ejecuta el flujo real = regresión silenciosa en el camino básico.*
- **Por qué no se detectaba a tiempo:** `node --check` solo mira sintaxis; las "pruebas"
  eran manuales o sobre el seed. Nunca se ejecutaba la app de verdad con un respaldo.
- **Mecanismo permanente (hecho):** `tools/smoke_test.js` (jsdom, headless) ejecuta el
  camino crítico sobre un respaldo de `data/`: importar sin errores → Equipos completa →
  filtro por columna numérica (el bug histórico) → abrir ficha → Ctrl+K → folio heredado
  del ciclo abierto. `build_app.py` lo corre **solo** al final de cada generación e imprime
  ✅/❌ (si falta jsdom o node, avisa y sigue). Devuelve código ≠0 si algo falla.
- **Regla nueva (incorporada a CLAUDE.md, paso 4 del ciclo):** ningún cambio se da por
  terminado sin que la prueba de humo pase. Si se agrega un flujo crítico nuevo, se le
  añade un chequeo a `tools/smoke_test.js`.
- **Cómo correrla a mano:** `node tools/smoke_test.js` (una vez: `npm install jsdom`).
- **Dónde aplica:** tools/smoke_test.js (nuevo), build_app.py (paso final), CLAUDE.md
  (ciclo de trabajo paso 4), este LEARNINGS.

## [2026-05-29] Alineación de las vistas con la especificación funcional (v0.40)

- **Disparador:** el usuario subió la especificación funcional (docx, basada en v0.38) y
  pidió "ajustar la app a la especificación". Se confirmó esa opción antes de actuar.
- **Hecho (vista por vista):**
  · Cap. 3: "Equipos" → "Buscar equipos" (menú + título). Columnas reordenadas al orden del
    documento y se agregó **Serie**: ID, N° Inventario, Serie, Equipo, Marca, Modelo,
    Servicio, Unidad, Ubicación, Procedencia, Estado, Días, Pendientes. Las celdas del cuerpo
    ahora se generan desde la definición de columnas (`COLS` con `cell` opcional), no a mano,
    así reordenar no descuadra la tabla.
  · Cap. 4: la ficha pasa de PESTAÑAS a **secciones contraíbles** apiladas (helper
    `seccionColapsable` con `<details>/<summary>`): Datos · Programación PMP · Historial ·
    Pendientes · Ciclos · Conflictos (si hay). Reutiliza los render existentes.
  · Cap. 4.2: la Programación PMP de la ficha suma la fila **Ejecutor** (Mes / P / R / Ejecutor).
- **Ya cumplían la especificación (verificado, sin tocar):** aviso al abrir un 2º ciclo con
  uno ya abierto (línea ~1441); folio preseleccionado del ciclo y aviso si no hay (v0.28);
  Ctrl+K con coincidencia parcial; filtros por columna tipo Excel.
- **No tocado a propósito (anotado para confirmar con el usuario):** la tabla de la vista
  Pendientes no agrega columnas "Responsable" ni "Recordatorio" del documento porque el
  modelo de datos no tiene un campo "responsable" separado del ejecutor; añadir columnas
  vacías confundiría. Queda como decisión a ratificar.
- **Verificado headless:** prueba de humo 6/6 OK; además chequeo dirigido confirma el título
  "Buscar equipos", la columna Serie en orden, 5–6 secciones contraíbles en la ficha y la
  fila Ejecutor en la PMP. 0 errores.
- **Heurística:** cuando una tabla declara columnas en un array, el CUERPO debe generarse
  desde ese mismo array (no filas a mano), o reordenar columnas descuadra los datos. Para
  "secciones contraíbles" nativas, `<details>/<summary>` evita JS de estado y no se rompe.
- **Dónde aplica:** build_app.py (`VIEWS.equipos` COLS+cuerpo, `NAV_GRUPOS`, `VIEWS.equipo`
  reescrita, `seccionColapsable`, `renderMatrizMP` fila Ejecutor, CSS `.ficha-sec`);
  CHANGELOG v0.40; app.html regenerado.

<!-- Próximas entradas debajo de esta línea -->
