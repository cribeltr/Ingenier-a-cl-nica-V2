# Eventos del sistema HHHA — nombre y campos que registra cada uno

> Referencia de los **7 tipos de evento**, qué campos pide cada uno y qué efecto tiene en el
> estado del equipo y en el ciclo correctivo. Basado en `build_app.py` (v0.47).

---

## Campos comunes a TODOS los eventos

Sin importar el tipo, cada evento guarda siempre:

| Campo (lo que ves) | Para qué sirve |
|---|---|
| Equipo (N° Inventario) | A qué equipo pertenece el evento. |
| Fecha | Fecha real en que ocurrió el evento. |
| Fecha de registro | Día en que se registró en el programa (automático). |
| Ejecutor | Quién lo hizo / responsable. |
| Observación | Texto libre: descripción, informe, notas. |
| Oficial | "Borrador" (No) u "Oficial" (Sí). Oficial = congelado para imprimir. |
| Creado por | Autor del registro (hoy: Cristian). |

**Además, internos/automáticos:** identificador del evento, equipo/servicio/familia copiados,
marca de hora de creación, si está **anulado** (con fecha y motivo de anulación) y el **origen**
(manual, automático del maestro, conciliación o registro en lote).

---

## Los 7 tipos de evento

### 1. Solicitud de trabajo
*Abre el ciclo correctivo.*

| Campo | Valores / nota |
|---|---|
| Folio SIGEM | Texto. Si se deja vacío, se genera uno automático. |
| Descripción de la falla | Observación. |

- **Efecto:** abre un **ciclo correctivo** con ese folio y el equipo pasa a **no operativo**.

### 2. Visita técnica
*Diagnóstica o correctiva.*

| Campo | Valores / nota |
|---|---|
| Empresa | Texto. |
| Técnico | Texto. |
| Tipo de visita | Diagnóstica · Correctiva. |
| Vincular a Folio SIGEM | Se preselecciona el ciclo abierto del equipo. |
| Estado resultante | No operativo · Operativo · En servicio técnico. |
| Informe / Observación | Observación. |

- **Efecto:** una visita **correctiva** que deja el equipo **operativo** **cierra** el ciclo.

### 3. Orden de Compra
*Gestión dentro del ciclo.*

| Campo | Valores / nota |
|---|---|
| N° Cotización | Texto. |
| N° OC | Texto. |
| Empresa | Texto. |
| Vía | Trato directo · Compra ágil. |
| Folio informe (TD) | Texto. Solo si es trato directo. |
| Vincular a Folio SIGEM | Se preselecciona el ciclo abierto. |
| Observación | Texto. |

- **Efecto:** queda registrada dentro del ciclo. No cambia el estado del equipo.

### 4. Envío a servicio técnico
*El equipo sale del hospital.*

| Campo | Valores / nota |
|---|---|
| N° de envío | Correlativo. |
| Empresa | Texto. |
| Folio SIGEM | Se preselecciona el ciclo abierto. |
| Estado resultante | **Fijo: "en servicio técnico"** (no se elige). |
| Observación | Texto. |

- **Efecto:** el equipo queda **en servicio técnico**.

### 5. Recepción
*El equipo retorna.*

| Campo | Valores / nota |
|---|---|
| N° envío original | Texto. |
| Folio guía de despacho | Texto. |
| Folio SIGEM | Se preselecciona el ciclo abierto. |
| Estado resultante | No operativo · Operativo. |
| Informe técnico / Observación | Texto. |

- **Efecto:** si la recepción deja el equipo **operativo**, **cierra** el ciclo. Si no hay ciclo
  abierto, el programa avisa.

### 6. Reparación
*Cierre típico del ciclo.*

| Campo | Valores / nota |
|---|---|
| Repuestos | Repuestos utilizados (texto). |
| Folio SIGEM | Se preselecciona el ciclo abierto. |
| Estado resultante | Operativo (cierra ciclo) · No operativo · En servicio técnico (no cierra). |
| Descripción de la tarea | Observación. |

- **Efecto:** **operativo** **cierra** el ciclo; "en servicio técnico" lo deja abierto. Si no hay
  ciclo abierto, el programa avisa.

### 7. Mantención preventiva (MP)
*Programada / ejecutada.*

| Campo | Valores / nota |
|---|---|
| Ejecutor 2 | Segundo ejecutor (opcional). |
| Resultado | Si · C1–C8 · FS · Baja · NU · No (ver tabla de códigos abajo). |
| Estado resultante | **Automático**, derivado del resultado (solo lectura). |
| Observación | Texto. |

- **Efecto del estado (automático según el resultado):**
  - **Si** → operativo
  - **C2** → en servicio técnico
  - **C3 / FS / NU** → no operativo
  - **Baja** → equipo dado de baja
  - **C1, C4–C8** → no cambian el estado (son reprogramaciones sin falla)
- **Efectos automáticos extra:**
  - Resultado **C1–C8** → crea un **pendiente de reprogramación** y marca una **"R" (reprogramado)
    en la programación del mes siguiente**.
  - Resultado **NU** → crea el pendiente "Localizar equipo".
  - Resultado **Baja** → el equipo pasa a **baja**.

---

## Códigos del campo "Resultado" de la MP

| Código | Significado | Estado que deja |
|---|---|---|
| Si | MP realizada | Operativo |
| C1 | Imposibilidad de desocupar el equipo del paciente | (sin cambio) — reprograma |
| C2 | Equipo en servicio técnico | En servicio técnico |
| C3 | Equipo no operativo, espera de repuestos/accesorios | No operativo |
| C4 | Equipo en préstamo a otro hospital | (sin cambio) — reprograma |
| C5 | No disponibilidad de HH funcionario SEC (carga laboral) | (sin cambio) — reprograma |
| C6 | No disponibilidad de HH servicio técnico externo | (sin cambio) — reprograma |
| C7 | Ausencia funcionario SEC > 15 días | (sin cambio) — reprograma |
| C8 | Contingencia hospitalaria | (sin cambio) — reprograma |
| FS | Fuera de servicio | No operativo |
| Baja | Equipo dado de baja | Baja |
| NU | No ubicable | No operativo |
| No | No realizada (sin causal) | (sin cambio) |

---

## Notas

- El **Folio SIGEM** es el hilo que une todo un ciclo correctivo: una vez abierto (con la
  Solicitud de trabajo), los demás eventos del ciclo lo heredan preseleccionado, no se escribe a mano.
- Ningún evento se borra: si hay un error se **anula** (queda con fecha y motivo de anulación).
- Los eventos también pueden nacer **automáticamente** al subir el archivo maestro (origen
  "Auto-maestro") o al aceptar un conflicto en Conciliación.
