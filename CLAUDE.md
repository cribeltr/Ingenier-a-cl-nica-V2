# CLAUDE.md — Protocolo de trabajo para HHHA

> Claude Code lee este archivo automáticamente al iniciar cada sesión.
> No es opcional: define cómo se trabaja en este repo.

## REGLA #0 — Nunca actuar sin confirmar (la más importante)

Antes de crear, cambiar o borrar CUALQUIER cosa:

1. Repetir, en palabras simples, qué entendí que se pide.
2. Esperar el "sí, dale" del usuario.
3. Recién entonces actuar.

Esto aplica SIEMPRE, no solo cuando algo es ambiguo o grande. Si el usuario ya
dio una orden explícita de ejecutar ("hazlo tú", "entrégame el final"), se
puede actuar, pero igual se resume en una línea qué se va a hacer.

## Cómo hablar con el usuario

- Siempre en **español**.
- Respuestas **breves**, partiendo por la conclusión.
- **Sin tecnicismos.** El usuario es experto en su trabajo (gestión de equipos
  biomédicos), no en computación. Traducir todo lo técnico a lenguaje claro.
- Si hay que nombrar algo técnico, explicarlo en una frase simple al lado.

## Pensar como experto, no ejecutar literal

Tomar las palabras del usuario al pie de la letra es un error. Antes de
responder hay que entender el PROPÓSITO detrás de lo que pide y proponer con
criterio profesional.

Esto es especialmente importante en **diseño**. Cuando el usuario pide "mejora
el diseño" o algo parecido, NO basta con cambios literales y superficiales
(por ejemplo, intercambiar emojis o mover un botón). Hay que:

1. Preguntarse para qué sirve esa pantalla y qué problema real tiene el usuario ahí.
2. **Simular cómo se vive de verdad:** ¿se entiende a la primera?, ¿dónde duda
   o se traba? (apoyarse en los `think_time` y abortos de `sesiones/`).
3. Proponer como lo haría un diseñador con criterio, no como quien solo cumple
   la frase. Si la propuesta del usuario no es la mejor para su objetivo,
   decirlo con respeto y ofrecer la alternativa.

Esta regla aplica a TODO el trabajo (lógica, diseño, datos): entender el porqué,
simular, y proponer con juicio de experto. La literalidad sin comprensión está
prohibida.

## Qué es este proyecto

HHHA es un sistema **offline de un solo archivo** para gestión de equipos
biomédicos críticos (893 equipos, máquina de estados, ciclo correctivo,
mantención preventiva por mes, pendientes, conciliación con archivo maestro).

- **Fuente de verdad: `build_app.py`.** Genera `app.html`.
- **NUNCA editar `app.html` a mano.** Se edita `build_app.py` y se regenera con
  `python3 build_app.py`.
- El estado se guarda en el navegador (localStorage, comprimido). Las fechas se
  guardan como texto `YYYY-MM-DD`.

## Ritual de inicio (obligatorio, antes de tocar nada)

1. Leer `docs/CONTEXTO.md`: el traspaso con la historia del proyecto y lo pendiente.
2. Leer `docs/LEARNINGS.md` completo. Es la memoria acumulada de sesiones
   anteriores: trampas conocidas, invariantes, heurísticas confirmadas.
3. Leer la sección "Invariantes" de abajo.
4. Aplicar REGLA #0.

## El ciclo de trabajo (para CADA ajuste, sin saltarse pasos)

El "panel de expertos" son lentes, no personas. Reproducir en orden:

### 1. Entender
Reformular en 1 frase qué se pide y por qué. Confirmar con el usuario (REGLA #0).

### 2. Revisar el PROGRAMA COMPLETO (lente: ingeniero)
No basta con leer la función que se va a tocar. Obligatorio:
- Buscar en TODO `build_app.py` cada lugar que use el mismo dato o el mismo
  patrón (usar `grep`), no solo la función actual.
- Regla de oro: *si arreglas algo en un sitio, tienen que quedar arreglados
  TODOS los sitios que repiten ese patrón.* Casi todos los bugs de este repo
  nacen de "lo arreglé en N lugares y omití M".
- Dejar anotado cuántos lugares se encontraron y cuáles se tocan.

### 3. Evaluar el impacto (lente: arquitecto)
Listar explícitamente, antes de cambiar, qué más toca ese dato:
¿quién lo **escribe**, quién lo **lee**, aparece en el **tablero**, en el
**Excel exportado**, en la **migración**? Cambiar la escritura sin revisar la
lectura (o al revés) es un bug garantizado.

### 4. Simular (OBLIGATORIO en cada cambio) (lentes: QA + diseñador)
Nunca cerrar un ajuste sin simular. Mínimo:
- **Caso normal.**
- **Casos borde:** fecha día 1 y último día del mes, equipo dado de baja,
  evento anulado, equipo sin eventos.
- **El escenario exacto que motivó el cambio.**
- **Regresión con `sesiones/`:** revisar que los flujos que el usuario ya hizo
  en esas grabaciones sigan funcionando.
- **Fricción (diseñador):** en `sesiones/`, los `think_time` altos, los
  abortos de modal y los clicks repetidos marcan dónde el usuario se traba.
Reportar al usuario qué se simuló y el resultado, en lenguaje simple.

**Prueba de humo OBLIGATORIA (no negociable).** Ningún cambio se da por terminado
sin que pase la prueba del camino crítico. `python3 build_app.py` la corre sola al
final; también se puede correr a mano con `node tools/smoke_test.js` (requiere, una
sola vez, `npm install jsdom`). Verifica: importar un respaldo de `data/` → la lista
de Equipos se ve completa → abrir una ficha → filtros por columna (incluida una
numérica) → Ctrl+K → folio heredado del ciclo abierto. Si toca un flujo crítico
nuevo, agrégale un chequeo a `tools/smoke_test.js`. Causa raíz histórica de los bugs:
tocar funciones grandes/compartidas y validar con el seed o solo con `node --check`,
sin EJECUTAR el camino básico con datos reales. La prueba de humo cierra ese hueco.

**Guardián de autocorrección (`tools/guard.js`, también automático en el build).**
Bloquea las CLASES de error ya cometidas: (1) un patrón arreglado a medias —p. ej. el
estado de una MP debe derivarse de `estadoMPDesdeResultado` en TODOS los sitios que crean
MP; (2) fórmulas/patrones legacy prohibidos; (3) cualquier vista que falle al dibujarse con
un respaldo real (las 10 vistas); y avisa de (4) funciones muertas y (5) clases CSS con
layout agresivo compartidas por varias tablas. Si el guardián marca ❌, NO se entrega hasta
corregir. Al introducir un patrón nuevo que deba estar en varios sitios, agrégale un chequeo.

**Diseño/visual: lo que el headless NO ve.** jsdom no mide píxeles (anchos, si algo cabe,
si el texto se parte). Por eso, ante un cambio de DISEÑO o de CSS: (a) revisar TODAS las
vistas/tablas que comparten esa clase o ese dato (no solo la que se está tocando), y (b)
pedirle al usuario una mirada visual o abrirlo en un navegador real antes de darlo por
bueno. Dos regresiones visuales (ancho de Equipos, Registro MP aplastado) las detectó el
usuario, no las pruebas: el ojo humano sigue siendo obligatorio para lo visual.

### 5. Registrar (lente: documentalista)
Antes de cerrar:
- Subir la versión y anotar el cambio en el CHANGELOG dentro de `build_app.py`.
- Añadir una entrada a `docs/LEARNINGS.md` con su formato.
- Regenerar `app.html` y confirmar que no da error.

## Invariantes (romper esto = bug)

- **Fechas:** una fecha guardada `YYYY-MM-DD` SIEMPRE se parsea como
  `new Date(f + 'T00:00:00')` antes de usar `.getMonth()/.getFullYear()/.getDate()`.
  Sin el `'T00:00:00'`, JavaScript la lee en horario UTC y en Chile retrocede un
  día → el mes o el año se corren. Para sacar solo el mes, mejor partir el texto:
  `f.split('-').map(Number)`. Nunca usar `new Date(f)` sobre una fecha cruda.
- **Estado del equipo:** `recalcEstadoEquipo` (recálculo tras anular) y
  `aplicarEfectosEvento` (aplicación en vivo) DEBEN traducir `ev.estado` igual.
  Si una maneja un valor que la otra no, el equipo queda en estados distintos
  según el camino. Mantenerlas espejadas o usar un solo helper compartido.
- **Textos de estado del formulario:** son `'no operativo'`, `'operativo'`,
  `'en servicio técnico'` (con espacios y acento). Cualquier comparación debe
  usar exactamente esos textos.
- **Iconos:** ➕ crear · ⊘ destructivo · ✓ confirmar · ✗ rechazar ·
  🔗 origen automático · ⚡ lote. No inventar iconos nuevos.

## Cómo usar `sesiones/`

Cada archivo es una sesión real del usuario (clicks, textos, navegación, dudas,
errores, abortos). Sirve para dos cosas:
- **Regresión:** ¿el flujo que el usuario hizo ahí sigue funcionando tras el cambio?
- **Fricción:** ordenar por tiempo de duda y por abortos = puntos a mejorar de
  la experiencia, no donde el usuario es lento.

## Cómo mejora el sistema con tu uso (auto-retroalimentación)

El programa ya funciona. La idea es que mejore solo a partir del uso real:

1. El usuario lo usa en su día a día y va dejando sus sesiones reales en `sesiones/`.
2. En cada conversación, antes de trabajar, se lee la memoria (`docs/LEARNINGS.md`)
   y se revisan esas sesiones para entender qué hace el usuario y dónde se traba.
3. Cada ajuste deja una entrada nueva en la memoria: qué se cambió, qué se
   confirmó, qué se aprendió.
4. La siguiente conversación arranca sabiendo más que la anterior.

No es un modelo que se reprograma solo: es conocimiento del usuario que se
acumula y obliga a no repetir errores y a entender cada vez mejor su trabajo.
