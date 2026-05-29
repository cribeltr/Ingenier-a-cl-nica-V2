# Traspaso del proyecto HHHA · v0.23 — 28-05-2026

## 1. Decisiones de diseño y qué se descartó

**Arquitectura: HTML único offline**
- *Elegido:* un solo `app.html` con todo embebido (JS, CSS, SheetJS, lz-string, seed JSON).
- *Por qué:* el usuario abre con doble clic desde cualquier carpeta del hospital, sin servidor, sin instalación, sin permisos de TI. Portabilidad total en pendrive.
- *Descartado:* SPA con framework (React/Vue), backend Node, app electron. Todos requieren build/instalación que no aporta valor en este contexto.

**Persistencia: localStorage + LZ-string**
- *Elegido:* `localStorage['hhha_v1_data']` con compresión lz-string (~10×).
- *Por qué:* a las pocas semanas la base crecía >1 MB y Chrome rechazaba writes. Compresión + auto-prune de conflictos resueltos al fallar.
- *Descartado:* IndexedDB (API engorrosa, sin ventaja real a esta escala) y backend (rompía el "offline").

**Migración de estado versionada**
- *Elegido:* cadena `migrate_vN_to_vN+1()` ejecutada al cargar/importar. Cada release agrega un step idempotente.
- *Por qué:* el usuario tiene backups JSON de cada versión anterior y debe poder importarlos sin perder datos.
- *Descartado:* migración destructiva o "borrar y empezar". Inaceptable con datos reales del hospital.

**Diseño visual: minimalista + dual theme**
- *Elegido:* paleta neutra, CSS variables, `data-theme="dark|light"`, iconos unificados (gramática visual v0.22).
- *Por qué:* feedback explícito del usuario tras v0.1 ("suéltate, hazlo minimalista intuitivo"). Trabajo prolongado → light fatiga; dark cómodo de noche.
- *Descartado:* librerías de UI (Tailwind, Bootstrap). Sobrecargaban el HTML y no aportaban más que ~200 líneas de CSS propio.

**Conciliación con maestro: no destructiva**
- *Elegido:* cualquier diferencia genera un conflicto que el usuario resuelve. Excepción v0.21: si el programa tiene campo vacío y el maestro tiene valor → autollena sin conflicto.
- *Por qué:* el maestro Excel es la verdad oficial pero el programa local tiene info más fresca (MPs del día). Nunca pisar sin confirmar.
- *Descartado:* "el maestro siempre gana" y "el local siempre gana". Ambos perdían información.

**Grabador de sesiones embebido**
- *Elegido:* auto-start, captura clicks/inputs/focus/think_time/hover_long/scroll/form_error/modal_abort, exportable como JSON.
- *Por qué:* las primeras versiones se ajustaron analizando sesiones reales del usuario; el grabador queda como herramienta de diagnóstico continuo.
- *Descartado:* telemetría a servidor externo. Privacidad + offline.

**Plantillas Excel de asignación mensual**
- *Elegido:* el usuario descarga plantilla del mes, la llena en Excel (su flujo natural), y la sube.
- *Por qué:* asignar 80–120 MPs/mes en la app sería lentísimo; en Excel lo hace en minutos.
- *Descartado:* drag-drop interno o tabla editable. No competía con la velocidad de Excel.

---

## 2. Problemas conocidos y cosas a medio terminar

**Técnicos**
- `recalcEstadoEquipo()` no está cacheado — se recalcula en cada render. Tolerable con 893 equipos pero degradará si pasa de ~5.000.
- `conflictosDe(eqId)` hace filter lineal sobre todo el array. Aceptable hoy; añadir índice por `eqId` cuando duela.
- Migración probada solo con un backup real (el del usuario). Hay riesgo en backups de versiones intermedias que él no haya guardado.
- Contador `__userActions` puede doble-contar en clicks con event bubbling no atrapado.
- Patrón de closures frágil: `VIEWS.equipo` necesita recibir `setTab` como callback; si alguien añade una vista nueva olvidando esto, los botones quedan no-op (v0.19 fue exactamente ese bug).
- Parser de Excel depende de regex sobre nombres de hoja/columna. Cambios menores en el maestro pueden romperlo silenciosamente.
- Eventos auto-completados (v0.21) **no son idempotentes**: reimportar dos veces el mismo maestro puede crear duplicados si entremedio se editó el equipo. Mitigado pero no eliminado.
- `navStack` crece sin tope. En sesiones muy largas (>1 h) consume RAM.
- Sin throttle en clicks rápidos → confirmar MP dos veces seguidas puede crear dos registros.
- Fallback de compresión cuando lz-string falla no está probado a escala (el caso real fue 1 MB; nadie probó 5 MB).

**Funcional / UX**
- Quick search (Ctrl+K) no busca dentro de bitácora ni pendientes, solo equipos.
- Resumen del equipo (v0.17) muestra los últimos 5 eventos; no hay paginación.
- Exports XLSX no traen formato condicional (colores de estado); van en texto plano.
- Banner amarillo de "no detecto actividad" puede confundir a un usuario nuevo que sí cargó datos pero no interactuó aún.

**A medio terminar / no implementado del pseudocódigo**
- Módulo 13: análisis IA de patrones de falla — no iniciado.
- Módulo 12.2: correos automáticos mensuales — no iniciado (requeriría backend).
- Módulo 14: roles y permisos — no iniciado (la app asume usuario único).
- Módulo 15: sync Google Sheets — no iniciado.
- Módulo de alertas proactivas (MPs sin ejecutar a fin de mes) — no iniciado.

---

## 3. Qué se pidió y qué quedó pendiente

**Pedidos cumplidos (v0.1 → v0.23)**
- App funcional offline con los 7 tipos de evento, ciclo correctivo, MP, pendientes.
- Conciliación con maestro Excel + 4 tipos de conflicto + resolución masiva.
- Export XLSX (7 hojas) + plantillas mensuales descargables/subibles.
- Dual theme, Ctrl+K, grabador de sesiones, compresión de localStorage.
- Migración no destructiva entre versiones.
- Bundle ZIP completo con app, build script, seed, docs, sesiones, backups, exports, plantillas, README.
- Distinción visual de eventos auto-completados (caso 2-115785, v0.23).

**Pendiente de decisión del usuario (no es bug, son reglas de negocio sin definir — ver §4)**
- Las 9 preguntas abiertas listadas abajo.

**Pendiente de implementación**
- Los 5 módulos del pseudocódigo no iniciados (§2).
- Reorganizar Resumen del equipo con paginación.
- Tests automatizados (toda la verificación fue manual + headless tests ad-hoc).

---

## 4. Reglas de negocio y supuestos asumidos (no estaban en la especificación)

Estos los inventé yo basado en lo observado; **deben ratificarse**:

1. **Folio SIGEM**: lo dejé opcional con autogenerado `AUTO-{timestamp}` si está vacío. El pseudocódigo no decía si era obligatorio.
2. **MP fuera del mes programado**: la app *permite* registrar, solo marca aviso. Asumí flexibilidad operativa; podría exigirse bloqueo.
3. **Equipos en programa pero no en maestro**: quedan como "huérfanos" en lista propia. No los doy de baja automáticamente.
4. **Día del evento sintético** (cuando el maestro tiene R pero no fecha): asumí día 15 del mes. Pseudocódigo no lo precisaba.
5. **Catálogo de documentos**: lo manejé genérico (un campo libre por equipo). No por familia de equipo.
6. **Mark oficial sin documentos**: la app *no bloquea*. Permite marcar aunque falten docs.
7. **Alertas de MP no ejecutadas**: no las implementé; solo se ven al filtrar Dashboard.
8. **Usuario para eventos sintéticos**: asumí "SISTEMA" como autor. No hay login.
9. **Maestro vacío vs programa con valor**: en v0.21 decidí que el maestro vacío **no pisa** al programa (solo el programa vacío recibe del maestro). Asimetría asumida.

---

## 5. ¿v0.23 es la versión final?

**No es "final" en el sentido de cerrada — es la última estable de esta tanda.**

- *Es entregable y usable hoy:* el usuario puede operar el ciclo completo (importar maestro, registrar MPs, conciliar, exportar) sin esperar más código.
- *No está congelada:* hay 5 módulos del pseudocódigo sin implementar y 9 reglas de negocio sin ratificar. Cualquiera de esas convierte a v0.23 en una base para v0.24+.
- *Recomendación práctica:* tratarla como **release operativa "buena para producción interna"**, no como producto terminado. Antes de seguir agregando features, validar con uso real 2–4 semanas para que afloren los problemas que ningún test sintético detecta.

---

## Para retomar en la próxima conversación

- **Rama:** `claude/modest-thompson-Kg8Ih` · **último commit:** `3eb7040` · **PR:** #1
- **Archivo de arranque:** `app.html` (v0.23, ~900 KB).
- **Estado a importar para reproducir:** `data/11_hhhadata20260528_6.json` desde el banner amarillo.
- **Para regenerar app:** `python3 build_app.py` (lee `seed.json` + embeds).
- **Bundle completo:** `hhha-bundle-v0.23.zip` (52 archivos, 6 MB).
