# PSEUDOCÓDIGO — Sistema de Gestión de Equipos Biomédicos HHHA

> Versión integrada. Sin prescripciones de interfaz: se describe **qué** debe poder hacer el sistema, no cómo se ve.
> Convenciones: **MAYÚSCULAS** = acción del sistema · *cursiva* = acción del usuario · `código` = campo, estado o valor literal.

---

## ÍNDICE

1. Glosario
2. Modelo de datos (entidades y relaciones)
3. Máquina de estados del equipo
4. Ciclo correctivo (concepto agrupador)
5. Tipos de evento (7) y sus efectos
6. Mantenimiento preventivo (programación + flujo mensual)
7. Pendientes y tareas
8. Puesta en marcha y baja
9. Carga del archivo maestro
10. Búsqueda y consulta
11. Documentos y adjuntos
12. Notificaciones y correos
13. Análisis IA de informes
14. Roles, permisos y auditoría
15. Sincronización y modo offline
16. Alertas, reglas automáticas y dashboard
17. Resumen de cambios respecto a versiones anteriores

---

## 1. GLOSARIO

- **Equipo**: cada uno de los ~970 dispositivos biomédicos del maestro.
- **Evento**: acción concreta registrada sobre un equipo (uno de 7 tipos).
- **Ciclo correctivo**: secuencia de eventos correctivos sobre un mismo equipo, agrupados por `Folio SIGEM`. Comienza con una `Solicitud de trabajo` y termina con un evento de `Reparación` (o equivalente).
- **MP**: Mantención preventiva.
- **Pendiente**: tarea o gestión abierta vinculada a un equipo, con plazo y responsable.
- **Ejecutor**: una de las 11 personas autorizadas para ejecutar MP o atender correctivos (incluye "Personal externo").
- **Cristian**: usuario administrador del sistema (responsable operativo).

---

## 2. MODELO DE DATOS

### 2.1. Entidad `Equipo` (maestro, ~970 registros)

| Categoría | Campos |
|---|---|
| Identificadores | `ID` (posición planilla), `N° Carpeta`, `N° Inventario`, `Serie` |
| Descripción | `Fam`, `Equipo`, `Marca`, `Modelo`, `Año Instalación` |
| Ubicación | `Servicio`, `Unidad`, `Ubicación`, `Procedencia` |
| Estado físico | `Vida Útil Residual`, `Clasificación`, `ENU / Baja` |
| Gestión MP | `Frecuencia MP` |
| **Calculados** | `Estado actual`, `Sub-estado`, `Días en estado actual`, `Ciclo correctivo abierto?` (bool), `Pendientes abiertos` (contador), `MP del mes ejecutada?` (bool) |

> Los campos `Responsable MP` y `Observación` del maestro Excel **no se importan** (especificación).
> Identificadores reales = `N° Inventario` y `Serie`. `ID` es solo posición de fila.

### 2.2. Entidad `Evento` (bitácora — hoja de vida digital)

Campos comunes:
`ID Evento`, `N° Inventario` (FK Equipo), `Tipo de evento`, `Fecha del evento`, `Fecha registro`, `Ejecutor`, `Estado del equipo` (resultante), `Observación`, `Adjuntos` (lista de URLs), `Oficial` (Sí/No), `Folio SIGEM` (FK Ciclo correctivo, si aplica), `Creado por`, `Actualizado por`, `Timestamp creación`, `Timestamp actualización`.

Campos específicos según tipo: ver Módulo 5.

### 2.3. Entidad `Ciclo correctivo`

`Folio SIGEM` (PK), `N° Inventario`, `Fecha apertura`, `Fecha cierre` (nullable), `Estado` ∈ {`abierto`, `cerrado`}, `Descripción inicial`, `Ingeniero asignado`.
- Se crea automáticamente al registrar una `Solicitud de trabajo`.
- Agrupa todos los eventos correctivos posteriores que comparten el mismo `Folio SIGEM`.
- Se cierra cuando un evento de `Reparación` (o cierre explícito de la solicitud) deja al equipo en `operativo`.

### 2.4. Entidad `Pendiente`

`ID Pendiente`, `N° Inventario`, `Tipo` ∈ {`documento_faltante`, `reprogramacion`, `recomendacion_tecnica`, `gestion_general`}, `Descripción`, `Origen` ∈ {`manual`, `auto_mp_causal`, `auto_ia_informe`, `auto_documento_faltante`}, `Fecha creación`, `Fecha compromiso`, `Próximo recordatorio`, `Fecha cierre`, `Ejecutor`, `Estado` ∈ {`creado`, `abierto`, `cerrado`}, `Seguimientos` (lista), `Adjuntos`, `Evento origen` (FK opcional al evento que lo generó).

### 2.5. Entidad `Tarea`

Sub-ítem de un pendiente: `ID Tarea`, `ID Pendiente` (FK), `Descripción`, `Estado` ∈ {`abierto`, `cerrado`}, `Fecha cierre`.

### 2.6. Entidad `Programación MP`

Matriz mensual derivada de `PMP_2026`: por `N° Inventario` y mes (`Ene`–`Dic`), un código `P` ∈ {`X`, `R`, `RA`, `PM`} o vacío.

### 2.7. Entidad `Registro MP`

Matriz derivada de `Registro_MP-2026`: por `N° Inventario` y mes, par `(P, R)`. `R` ∈ {`Si`, `C1`–`C8`, `FS`, `Baja`, `NU`} o vacío.

### 2.8. Catálogos fijos

- `Causales` (C1–C8): código, descripción, regla (ver Módulo 6.3).
- `Ejecutores` (11): los 10 internos + `Personal externo`.
- `Códigos P` y `Códigos R`.
- `Tipos de documento esperado` por tipo de MP (catálogo predefinido).
- `Pendientes habituales` (templates para creación rápida).

### 2.9. Entidad `Contacto`

`ID`, `Nombre`, `Rol` ∈ {`supervisor_servicio_clinico`, `encargado_equipos`, `jefe_cr`, `empresa_externa`, `tecnico_externo`}, `Servicio` (si aplica), `Email`, `Teléfono`, `Equipos que atiende` (lista de N° Inventario, si aplica).

### 2.10. Entidad `Cambio` (audit log)

`ID`, `Entidad`, `ID entidad`, `Campo`, `Valor anterior`, `Valor nuevo`, `Usuario`, `Timestamp`.

---

## 3. MÁQUINA DE ESTADOS DEL EQUIPO

Estados primarios:

```
                          ┌──────────────┐
                          │   OPERATIVO  │ ◀────────────────┐
                          └──────┬───────┘                  │
                                 │ Solicitud de trabajo     │ Reparación
                                 ▼                          │ (op=Sí)
                          ┌──────────────┐                  │
                          │ NO OPERATIVO │──────────────────┤
                          └──────┬───────┘                  │
                                 │ Envío a servicio técnico │
                                 ▼                          │
                          ┌──────────────────┐              │
                          │ EN SERVICIO TÉC. │──────────────┤
                          └──────────────────┘ Recepción +
                                               Reparación
                          ┌──────────────┐
                          │     BAJA     │ (terminal)
                          └──────────────┘
```

Sub-estados (información complementaria, no terminal):

- Bajo `NO OPERATIVO`: `esperando_visita_tecnica`, `esperando_cotizacion`, `esperando_OC`, `esperando_repuestos`, `en_reparacion_interna`, `otro`.
- Bajo `EN SERVICIO TÉCNICO`: `enviado`, `cotizacion_pendiente`, `OC_emitida`, `en_reparacion_externa`, `despachado_de_regreso`.

REGLA: el `Estado actual` y `Sub-estado` se derivan del último evento del equipo. Cada evento declara explícitamente el estado resultante (Módulo 5).

---

## 4. CICLO CORRECTIVO

### 4.1. Concepto

Un ciclo correctivo agrupa todos los eventos generados a partir de **una misma `Solicitud de trabajo`**, identificada por su `Folio SIGEM`.

### 4.2. Apertura

1. Al crear un evento `Solicitud de trabajo` → **CREAR** automáticamente un `Ciclo correctivo` con:
   - `Folio SIGEM` = folio ingresado
   - `Estado` = `abierto`
   - `Fecha apertura` = fecha de la solicitud
   - `Ingeniero asignado` = el indicado en la solicitud.

### 4.3. Eventos asociados

Todos los eventos posteriores cuyo `Folio SIGEM` coincida quedan asociados al mismo ciclo. El usuario, al crear eventos correctivos, debe poder **vincularlos** a un ciclo abierto del equipo (lista desplegable de folios abiertos).

### 4.4. Cierre

REGLAS de cierre del ciclo:
- Al registrar un evento `Reparación` con `Estado del equipo` = `operativo` vinculado al ciclo → **CERRAR** el ciclo automáticamente (`Estado` = `cerrado`, `Fecha cierre` = fecha de la reparación).
- También se puede cerrar manualmente (con justificación).

### 4.5. Concurrencia

Un mismo equipo puede tener **varios ciclos** en el tiempo, pero solo uno `abierto` a la vez. Al intentar abrir un segundo ciclo sobre un equipo con ciclo ya abierto → **PEDIR CONFIRMACIÓN** y registrar advertencia.

---

## 5. TIPOS DE EVENTO (7)

Agrupados por función. Cada evento se asocia a un `N° Inventario` y, si es correctivo, a un `Folio SIGEM`.

### 5.1. `Solicitud de trabajo` *(apertura de ciclo correctivo)*

- Campos: `Fecha de solicitud`, `Ejecutor asignado`, `Folio SIGEM`, `Observación` (descripción de la falla), `Estado del equipo` = `no operativo`.
- Efectos:
  - **CREAR** Ciclo correctivo (Módulo 4.2).
  - **CAMBIAR** estado del equipo a `no operativo`, sub-estado inicial = `otro` (o el que aplique).
- Documento físico esperado: solicitud SIGEM impresa.

### 5.2. `Visita técnica` *(gestión dentro del ciclo)*

- Campos: `Fecha`, `Empresa`, `Técnico`, `Tipo de visita` ∈ {`diagnóstica`, `correctiva`}, `Observación` (informe), `Adjuntos` (PDF del informe), `Folio SIGEM` (link), `Estado del equipo` resultante.
- Efectos:
  - Si `Tipo` = `diagnóstica` y no repara → estado se mantiene `no operativo`; sub-estado = `esperando_cotizacion` o `esperando_OC`.
  - Si `Tipo` = `correctiva` y deja equipo operativo → estado = `operativo`. Si vincula a un ciclo, **CERRAR** el ciclo.

### 5.3. `Orden de Compra` *(gestión dentro del ciclo)*

- Campos: `Fecha`, `N° Cotización`, `N° OC`, `Empresa`, `Vía` ∈ {`trato_directo`, `compra_agil`}, `Folio informe técnico` (correlativo, solo si trato directo), `Folio SIGEM` (link), `Observación`.
- Efectos:
  - Sub-estado pasa a `esperando_OC` → `esperando_repuestos` cuando se confirma envío.
  - No cambia estado primario.

### 5.4. `Envío a servicio técnico`

- Campos: `Fecha de envío`, `N° de envío` (correlativo), `Empresa`, `Ejecutor`, `Observación`, `Folio SIGEM` (link), `Estado del equipo` = `en servicio técnico`.
- Efectos: estado primario = `en servicio técnico`, sub-estado = `enviado`.

### 5.5. `Recepción`

- Campos: `Fecha de recepción`, `N° de envío` (link al envío original), `Folio guía de despacho`, `Adjuntos` (informe técnico de la empresa), `Estado del equipo` resultante (`operativo` / `no operativo`), `Folio SIGEM` (link).
- Efectos:
  - Si `Estado` = `operativo` → desbloquea cierre del ciclo (puede esperar a un evento `Reparación` explícito o cerrarse aquí).
  - Si `Estado` = `no operativo` → sub-estado `despachado_de_regreso` y permanece a la espera de reparación interna o nueva gestión.

### 5.6. `Reparación` *(cierre típico del ciclo correctivo)*

- Campos: `Fecha de reparación`, `Descripción de la tarea`, `Repuestos utilizados` (opcional), `Ejecutor`, `Folio SIGEM` (link), `Estado del equipo` = `operativo` / `no operativo`.
- Efectos:
  - Si `Estado` = `operativo` y `Folio SIGEM` vinculado a ciclo abierto → **CERRAR** el ciclo (Módulo 4.4).
  - Si `Estado` = `no operativo` → el ciclo sigue abierto.

### 5.7. `Mantención preventiva`

- Campos: `Fecha`, `Resultado` ∈ {`Si`, `C1`–`C8`, `FS`, `Baja`, `NU`, `No`}, `Ejecutor`, `Ejecutor 2` (si aplica), `Observación`, `Adjuntos` (protocolo + informes), `Estado del equipo` resultante.
- Efectos:
  - **ESCRIBIR** `Resultado` en la sub-columna `R` del mes correspondiente a `Fecha` en `Registro_MP-2026` para ese `N° Inventario`.
  - Si `Resultado` ∈ {`C1`–`C8`} → **CREAR** `Pendiente` tipo `reprogramacion` (Módulo 7.2.1).
  - Si `Resultado` = `Si` → si faltan documentos esperados según catálogo → **CREAR** `Pendiente` tipo `documento_faltante`.
  - Si la observación o adjuntos contienen recomendaciones → **EJECUTAR IA** (Módulo 13).
  - No abre ciclo correctivo (MP es independiente).

### 5.8. Reglas comunes a todos los eventos

- Al crear: `Oficial` = `No` por defecto (borrador).
- Al editar o eliminar: registrar en audit log (Módulo 14).
- `Oficializar` un evento es un acto explícito (`Oficial` = `Sí`) que congela el registro y permite imprimir/archivar.
- Ningún evento puede borrarse físicamente; solo marcarse como `anulado` (con motivo + autor).

---

## 6. MANTENIMIENTO PREVENTIVO

### 6.1. Programación anual

1. A inicio de año, **CARGAR** la matriz mensual desde `PMP_2026` (Módulo 9).
2. Cada equipo tiene una `Frecuencia MP` que indica cuántas MP/año le corresponden y en qué meses (codificados como `X`).

### 6.2. Códigos

- **`P` (Programación)**: `X` programado · `R` reprogramado · `RA` reprogramado del año anterior · `PM` puesta en marcha.
- **`R` (Resultado)**: `Si` realizado · `C1`–`C8` causal · `FS` fuera de servicio · `Baja` · `NU` no ubicable · `No` no realizado sin causal.

### 6.3. Causales C1–C8

| Código | Descripción | Regla |
|---|---|---|
| `C1` | Imposibilidad de desocupar el equipo del paciente | Reprogramar dentro de 30 días |
| `C2` | Equipo en servicio técnico | Sin fecha; esperar reintegro |
| `C3` | Equipo no operativo, espera de repuestos/accesorios | Sin fecha; esperar reintegro |
| `C4` | Equipo en préstamo a otro hospital | Sin fecha; esperar reintegro |
| `C5` | No disponibilidad de HH funcionario SEC (carga laboral) | Reprogramar dentro de 30 días |
| `C6` | No disponibilidad de HH servicio técnico externo | Reprogramar dentro de 30 días |
| `C7` | Ausencia funcionario SEC > 15 días | Reprogramar dentro de 30 días |
| `C8` | Contingencia hospitalaria | Reprogramar dentro de 30 días |

Efecto en la planilla:
- `C2` / `C3` / `C4`: no fijan fecha destino; la MP se registra en el mes real de ejecución cuando ocurra.
- `C1` / `C5` / `C6` / `C7` / `C8`: el mes original conserva `X` en `P` y la causal en `R`; el mes destino lleva `R` en `P`.

### 6.4. Flujo mensual

#### 6.4.1. Inicio de mes

1. **FILTRAR** equipos con `P` ∈ {`X`, `R`, `RA`, `PM`} en el mes en curso, **EXCLUYENDO** los que tengan `FS` / `Baja` / `NU` en meses anteriores del mismo año.
2. **GENERAR** lista de asignación con: `N° Carpeta`, `N° Inventario`, `Equipo`, `Servicio`, `Unidad`, `Ubicación`, `Marca`, `Modelo`, `Serie`, `Año`, `Frecuencia MP`, `Programado en mes` (código `P` original), `Responsable` (vacío).
3. Cristian *asigna manualmente* cada equipo a uno de los 11 ejecutores (puede ser `Personal externo`).
4. La asignación queda registrada y es visible para cada ejecutor.

#### 6.4.2. Durante el mes

- Cada ejecutor *ejecuta sus MP asignadas* y entrega documentación.
- Cristian *crea un evento `Mantención preventiva`* (Módulo 5.7) por cada entrega.
- El sistema actualiza automáticamente `Registro_MP-2026` (Módulo 5.7).

#### 6.4.3. Cierre del mes

1. **VERIFICAR** que todas las MP del mes tengan evento registrado. Las que no, quedan visibles en el dashboard.
2. **CONSOLIDAR** resultados por equipo y por servicio clínico:
   - Resultado (Si / causal / FS / Baja / NU).
   - Observaciones extraídas (IA o manuales).
   - Pendientes generados.
   - Recomendaciones técnicas.
3. **GENERAR Y ENVIAR** correo automatizado por servicio clínico (Módulo 12.2).
4. **OFICIALIZAR** los eventos del mes (uno a uno o en lote).

---

## 7. PENDIENTES Y TAREAS

### 7.1. Tipos de pendiente

| Tipo | Origen típico |
|---|---|
| `documento_faltante` | Falta firma, falta informe, pauta de monitoreo, etc. |
| `reprogramacion` | MP con causal C1–C8 |
| `recomendacion_tecnica` | IA extrajo recomendación de un informe |
| `gestion_general` | Consulta de estado, solicitar a servicio que cree solicitud, etc. |

### 7.2. Creación automática

#### 7.2.1. MP con causal C1–C8
- `Tipo` = `reprogramacion`
- `Descripción` = "Reprogramar MP por causal `Cn` — <descripción de la causal>. <regla aplicable>."
- `Fecha compromiso`:
  - Si causal ∈ {`C2`,`C3`,`C4`} → **NULL** (espera reintegro).
  - Si causal ∈ {`C1`,`C5`,`C6`,`C7`,`C8`} → fecha dentro de 30 días desde la MP.
- `Ejecutor` = mismo de la MP.
- `Estado` = `creado`.
- `Evento origen` = ID del evento MP.

#### 7.2.2. Documentos faltantes
- Al cerrar una MP, **COMPARAR** adjuntos vs catálogo de documentos esperados según tipo de MP.
- Por cada documento faltante → crear `Pendiente` tipo `documento_faltante`.

#### 7.2.3. Recomendaciones de IA
- Al extraer recomendaciones de un informe (Módulo 13), **OFRECER** crear un pendiente por cada recomendación (configurable: automático o con confirmación).

### 7.3. Creación manual

- Desde la ficha del equipo, *crear pendiente* eligiendo `Tipo` y completando campos.
- `Estado` inicial = `abierto`.

### 7.4. Ciclo de vida

`creado` → `abierto` → `cerrado`.

- `creado`: generado por sistema; aún no gestionado.
- `abierto`: en gestión activa; puede tener `Fecha compromiso` y `Próximo recordatorio`.
- `cerrado`: completado; **REGISTRAR** `Fecha cierre` y opcionalmente seguimiento final.

### 7.5. Seguimientos

Lista de notas con timestamp dentro del pendiente. Cada seguimiento: `Fecha`, `Autor`, `Texto`.

### 7.6. Tareas (sub-ítems)

Un pendiente puede tener N tareas atómicas (ej. "transcribir la ficha técnica porque tiene un borrón"). Cada tarea se cierra independientemente. Al cerrar la última tarea, **SUGERIR** cerrar el pendiente.

### 7.7. Recordatorios

REGLA: cuando `Próximo recordatorio` ≤ hoy → **GENERAR ALERTA** para el `Ejecutor` y para Cristian.

### 7.8. Reasignación

Un pendiente puede reasignarse a otro ejecutor; **REGISTRAR** en audit log y en `Seguimientos`.

---

## 8. PUESTA EN MARCHA Y BAJA

### 8.1. Puesta en marcha (equipo nuevo)

1. *Ingresar equipo nuevo* al maestro con todos sus datos.
2. **VERIFICAR** que `N° Inventario` y `Serie` no estén duplicados.
3. **OCUPAR** un slot vacío en `PMP_2026` (slot existente o agregar al final).
4. **MARCAR** la MP con código `PM` en el mes de instalación.
5. **REGISTRAR** evento informativo en la bitácora del equipo.

### 8.2. Baja

1. *Marcar el equipo como `Baja`*; **EXIGIR** motivo y fecha.
2. **ESCRIBIR** `Baja` en la sub-columna `R` del mes de baja en `Registro_MP-2026`.
3. **LIMPIAR** automáticamente los meses posteriores del equipo en `Registro_MP-2026` (resultado vacío; programación se mantiene pero ignorada).
4. **EXCLUIR** el equipo de los filtros mensuales futuros, pero **CONSERVAR** en el histórico y la búsqueda (con marca visible `Baja`).
5. **CERRAR** automáticamente todos los pendientes abiertos del equipo (con motivo "equipo dado de baja").

### 8.3. Estados especiales (`FS`, `NU`)

- `FS` (fuera de servicio temporal): solo afecta el mes detectado; no propaga.
- `NU` (no ubicable): solo afecta el mes detectado; debe generar pendiente automático tipo `gestion_general` ("Localizar equipo").

---

## 9. CARGA DEL ARCHIVO MAESTRO

### 9.1. Importación inicial

1. **ABRIR** `Programacion_MP_[año].xlsm`.
2. **DETECTAR AUTOMÁTICAMENTE** los encabezados en ambas hojas (`PMP_[año]` y `Registro_MP-[año]`), tolerando espacios y variaciones de mayúsculas.
3. **IMPORTAR** todas las columnas de identificación del equipo **EXCEPTO** `Responsable MP` y `Observación` (por especificación).
4. **IMPORTAR** los slots vacíos como filas reservadas (futuras `PM`).
5. **IMPORTAR** la matriz mensual `P` desde `PMP_[año]`.
6. **IMPORTAR** la matriz mensual `(P, R)` desde `Registro_MP-[año]`.
7. **VALIDAR**: que los códigos sean del catálogo; reportar inconsistencias sin interrumpir la carga.

### 9.2. Reimportación / actualización

- Permitir reimportar para sincronizar cambios externos.
- Detectar y reportar conflictos (filas que existen en la app pero ya no en el Excel, y viceversa).
- No sobreescribir eventos ni pendientes creados en la app.

### 9.3. Validaciones

- `N° Inventario` único.
- `Serie` única (con advertencia, no bloqueante, si se repite — hay casos legítimos).
- Códigos `P` y `R` ∈ catálogo.
- Meses cuadran con la frecuencia MP declarada.

---

## 10. BÚSQUEDA Y CONSULTA

### 10.1. Búsqueda principal

Por: `N° Inventario`, `Serie`, `N° Carpeta`, `Equipo`, `Marca`, `Modelo`, `Servicio`, `Unidad`, `Ubicación`, `Ejecutor`, `Folio SIGEM`, `N° Envío`, `N° OC`, `N° Cotización`. Coincidencia parcial e insensible a mayúsculas/tildes.

### 10.2. Filtros combinados

- Estado actual del equipo.
- Servicio clínico.
- Pendientes abiertos (sí/no, por tipo).
- MP del mes (ejecutada, pendiente, reprogramada).
- Rango de fechas.

### 10.3. Consulta por equipo (ficha)

Al consultar un equipo, el sistema debe poder mostrar:
- Datos del maestro.
- Estado actual y sub-estado, con `Días en estado`.
- Programación MP del año (12 meses con códigos `P`).
- Resultado MP del año (12 meses con códigos `R`).
- Bitácora cronológica de eventos.
- Ciclos correctivos (abiertos y cerrados).
- Pendientes y tareas (abiertos y cerrados).
- Adjuntos.

### 10.4. Consulta agregada

- Por servicio clínico: lista de equipos, estados, MP del mes, pendientes.
- Por ejecutor: MP asignadas, pendientes, eventos creados.
- Por empresa externa: ciclos correctivos en curso, OC pendientes.

---

## 11. DOCUMENTOS Y ADJUNTOS

### 11.1. Catálogos de documentos esperados

**Correctivo**:
- Solicitud SIGEM impresa con tarea cerrada
- Cotización
- Informe técnico de trato directo (con correlativo)
- Orden de compra
- Guía de despacho de repuestos
- Informe técnico de visita diagnóstica
- Informe técnico de visita correctiva
- Hoja de envío (con correlativo)
- Informe técnico de reparación de servicio técnico externo
- Guía de despacho de retorno

**Preventivo**:
- Protocolo / hoja de mantenimiento preventivo
- Pauta de monitoreo diario (DEA)
- Firma del jefe de equipo médico
- Informe técnico de empresa externa (cuando aplica)

### 11.2. Almacenamiento

- Cada adjunto se sube y queda con URL pública (Google Drive u otro almacenamiento).
- Adjuntos vinculados a equipo y/o evento.
- Tamaño máximo configurable.
- Conserva nombre original + ID interno.

### 11.3. Verificación automática

Al oficializar un evento, **VERIFICAR** que los documentos esperados del catálogo estén adjuntos. Si faltan → crear pendientes (Módulo 7.2.2).

---

## 12. NOTIFICACIONES Y CORREOS

### 12.1. Notificaciones internas (dashboard / alertas)

- Recordatorios de pendientes.
- Alertas de equipos con > 30 días en `no operativo` o `en servicio técnico`.
- MP del mes sin ejecutar al llegar fin de mes.
- Eventos sin oficializar.

### 12.2. Correo de cierre mensual

Al cierre del mes, **POR CADA SERVICIO CLÍNICO** con MP en el mes:

1. **DESTINATARIO**: supervisor del servicio clínico.
2. **COPIA**: encargado de equipos, jefe del centro de responsabilidad.
3. **CONTENIDO**:
   - Resultado de las MP del mes (tabla por equipo).
   - Observaciones encontradas.
   - Pendientes asociados.
   - Recomendaciones técnicas.
4. **ADJUNTAR** copia de los informes técnicos si están disponibles.

### 12.3. Plantillas

- Plantillas editables almacenadas en el sistema.
- Permitir vista previa antes de enviar.

### 12.4. Registro de envío

Cada correo enviado queda registrado: `Fecha`, `Destinatarios`, `Servicio`, `Contenido`, `Adjuntos`. Reenvío permitido.

---

## 13. ANÁLISIS IA DE INFORMES

### 13.1. Disparador

Al adjuntar o pegar el texto de un informe técnico (en cualquier evento que lo admita: MP, Visita técnica, Recepción).

### 13.2. Extracción

La IA debe extraer y separar:
- `Observaciones` (qué se encontró durante la inspección).
- `Recomendaciones` (qué se sugiere hacer).
- `Pendientes detectados` (acciones explícitas, ej. "cotizar", "reemplazar baterías").

### 13.3. Persistencia

- Texto original se conserva.
- Cada elemento extraído se guarda como registro estructurado vinculado al evento.
- Las recomendaciones y pendientes detectados pueden convertirse en `Pendientes` del Módulo 7 (con confirmación).

### 13.4. Revisión humana

Cristian puede *revisar y editar* las extracciones antes de oficializar el evento.

---

## 14. ROLES, PERMISOS Y AUDITORÍA

### 14.1. Roles

- **Administrador (Cristian)**: acceso total; único que puede crear/editar eventos, oficializar, dar de baja, importar maestro.
- **Ejecutor**: ve su lista de MP asignadas y pendientes; puede subir adjuntos y proponer cierres (no oficializa).
- **Supervisor de servicio clínico**: solo lectura sobre los equipos de su servicio; recibe correos de cierre.
- **Lectura pública** (opcional): solo búsqueda y consulta de ficha sin datos sensibles.

### 14.2. Auditoría

- Cada cambio (creación, edición, anulación, oficialización, asignación) se registra en la entidad `Cambio` (Módulo 2.10).
- Histórico consultable por equipo, por usuario y por rango de fechas.
- Nunca se borra físicamente: las eliminaciones son lógicas con motivo y autor.

---

## 15. SINCRONIZACIÓN Y MODO OFFLINE

### 15.1. Arquitectura

- App web accesible vía link, autenticada con cuenta Gmail personal.
- Base de datos propia (servidor) + base local en cada PC (cache + offline).
- Respaldo continuo a Google Sheets.

### 15.2. Modo offline

- Toda operación es posible sin conexión: lectura, creación, edición.
- Los cambios se encolan localmente con timestamp.

### 15.3. Sincronización al recuperar conexión

1. **ENVIAR** la cola local al servidor.
2. **DESCARGAR** cambios remotos posteriores a la última sync.
3. **RESOLVER CONFLICTOS**:
   - Estrategia por defecto: `last-write-wins` por campo.
   - Para eventos: nunca se sobreescriben; se conservan ambos y se marca el conflicto para revisión.
4. **REPLICAR** a Google Sheets como respaldo.

### 15.4. Multi-PC

- Cristian usa al menos dos equipos (trabajo + notebook); ambos deben ver el mismo estado tras sync.

---

## 16. ALERTAS, REGLAS AUTOMÁTICAS Y DASHBOARD

### 16.1. Reglas automáticas (background)

Ejecutar periódicamente (ej. cada hora o al abrir la app):

1. **RECALCULAR** campos derivados del equipo: `Estado actual`, `Sub-estado`, `Días en estado actual`, `Pendientes abiertos`, `MP del mes ejecutada?`, `Ciclo correctivo abierto?`.
2. **GENERAR ALERTA** si `Días en estado actual` > 30 y estado ∈ {`no operativo`, `en servicio técnico`}.
3. **REVISAR** pendientes: si `Próximo recordatorio` ≤ hoy → notificar al ejecutor.
4. **VERIFICAR** MP del mes en curso: por cada equipo programado sin evento MP del mes → marcar como pendiente.
5. **VERIFICAR** documentos esperados de MPs ya registradas; crear pendientes por faltantes.
6. SI hay conexión → sincronizar.

### 16.2. Información del dashboard

El sistema debe poder reportar (formato libre — UI a definir):

- Equipos en `no operativo` o `en servicio técnico` con > 30 días sin actualización.
- Pendientes abiertos por tipo y por ejecutor.
- Recordatorios vencidos o por vencer.
- Eventos sin oficializar.
- MP del mes: ejecutadas / reprogramadas / pendientes / con causal.
- Ciclos correctivos abiertos.
- Equipos próximos a tener MP (mes siguiente).

### 16.3. KPIs propuestos

- % MP cumplidas en el mes programado (vs total programadas).
- % MP reprogramadas y motivo dominante.
- Tiempo promedio de ciclo correctivo (desde solicitud hasta reparación).
- Distribución de causales por servicio clínico.
- Equipos con más eventos correctivos en el año.
- Empresas externas con tiempos de respuesta más largos.

---

## 17. RESUMEN DE CAMBIOS RESPECTO A VERSIONES ANTERIORES

1. **Nuevo concepto: `Ciclo correctivo`** agrupado por `Folio SIGEM`. Da coherencia a los eventos correctivos sueltos.
2. **7 tipos de evento** consolidados (con función clara cada uno): `Solicitud de trabajo`, `Visita técnica`, `Orden de Compra`, `Envío a servicio técnico`, `Recepción`, `Reparación`, `Mantención preventiva`. Se resuelve la inconsistencia previa entre los 5 de la última especificación y los 5 reales en los registros: ambos conjuntos son sub-listas del catálogo unificado.
3. **Máquina de estados explícita** con estados primarios y sub-estados.
4. **Pendientes tipificados** (4 tipos) con origen marcado (manual / auto), para filtrado y automatizaciones.
5. **Reglas de automatización explícitas**: MP con causal → pendiente; documento faltante → pendiente; IA → pendientes propuestos.
6. **Sin prescripciones de UI**: el documento describe capacidades funcionales, dejando libre el diseño visual.
7. Se agregan módulos completos para: **Documentos y adjuntos**, **Notificaciones y correos**, **Análisis IA**, **Roles y permisos**, **Auditoría**, **Sincronización offline**, **KPIs**.
8. **Campos derivados del maestro** explicitados (lo que antes era implícito): `Estado actual`, `Sub-estado`, `Días en estado`, `Ciclo abierto?`, etc.
9. **Reglas de carga del maestro** completas: ignorar columnas (`Responsable MP`, `Observación`), cargar slots vacíos, validar códigos.
10. **Permisos diferenciados**: administrador, ejecutor, supervisor — cada uno con su alcance.

FIN.
