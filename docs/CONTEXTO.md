# CONTEXTO — Traspaso para una conversación nueva

> Si eres Claude leyendo esto al inicio de una conversación nueva: este
> documento te pone al día de qué es el proyecto, qué se hizo antes, cómo
> quiere trabajar el usuario y qué quedó pendiente. Léelo junto a `CLAUDE.md`
> (las reglas) y `docs/LEARNINGS.md` (la memoria).

## 1. Qué es el proyecto

HHHA es un sistema **offline de un solo archivo** para gestionar equipos
biomédicos críticos (893 equipos): estado de cada equipo, ciclo correctivo,
mantención preventiva (MP) por mes, pendientes y conciliación con un archivo
maestro. Se abre con doble clic en `app.html`, sin internet.

- **Lo que se edita es `build_app.py`** (el código fuente). Genera `app.html`.
- **Nunca editar `app.html` a mano.** Tras un cambio se regenera con
  `python3 build_app.py`.

## 2. Quién es el usuario y cómo hay que trabajar con él

El usuario es **experto en su trabajo** (gestión de equipos biomédicos),
**no en computación**. Por eso:

- Hablarle siempre en **español, breve y sin tecnicismos**.
- **Confirmar antes de actuar:** repetir qué se entendió y esperar su "sí"
  antes de crear, cambiar o borrar algo (es la REGLA #0 de `CLAUDE.md`).
- **Pensar como experto, no ejecutar literal:** entender el propósito real,
  simular cómo se vive, y proponer con criterio (sobre todo en diseño). No
  basta con cambios superficiales.
- En cada ajuste seguir el ciclo completo: entender → revisar el programa
  completo → evaluar impacto → simular → registrar lo aprendido.

Todo esto está detallado en `CLAUDE.md`. Este documento solo lo resume.

## 3. Qué se hizo en la conversación inicial (la historia)

1. **Revisión del programa.** A pedido del usuario se revisó el código buscando
   errores. Hallazgos:
   - **Error de fechas (importante, pendiente de arreglar):** las fechas se
     guardan como texto `YYYY-MM-DD`. En 4 lugares se leen de forma segura
     (`new Date(f+'T00:00:00')`), pero en 2 lugares se omitió: las funciones
     `mpDelMesEjecutada` y `aplicarEfectosEvento` (parte de MP). Sin el
     `'T00:00:00'`, en Chile la fecha retrocede un día y el mes/año se corren.
     Efecto: una MP del día 1 se guarda en el mes anterior y no se detecta como
     ejecutada en su mes. Se comprobó reproduciéndolo.
   - **Divergencia de estado (menor, no alcanzable hoy):** `recalcEstadoEquipo`
     y `aplicarEfectosEvento` traducen el estado del equipo de forma distinta;
     hoy no se dispara, pero conviene alinearlas.
   - **Detalle de diseño (menor):** el badge ⚡ Lote no recibe el estilo verde
     de "evento automático" que sí reciben los de conciliación.
2. **Se creó el protocolo de trabajo** (`CLAUDE.md`) y **la memoria**
   (`docs/LEARNINGS.md`), reforzados con el pedido del usuario de confirmar
   siempre, revisar completo, simular y no actuar literal.
3. **Se armó esta carpeta** para subirla al repositorio del usuario y trabajar
   desde ahí en adelante.

## 4. Qué quedó pendiente (por orden sugerido)

1. ✅ **HECHO (v0.24):** se corrigió el error de fechas en `mpDelMesEjecutada` y
   `aplicarEfectosEvento`, siguiendo el ciclo completo y con simulación.
2. Decidir si se alinea la **divergencia de estado** (recalc vs aplicación).
   No alcanzable hoy; queda documentado.
3. Decidir el **detalle visual del badge ⚡ Lote**.
4. Revisar los problemas conocidos y los 9 supuestos de negocio sin ratificar
   que dejó el chat constructor en **`docs/TRASPASO.md`** (idempotencia de
   eventos auto, doble-click sin throttle, folio opcional, día 15, etc.).

## 5. Cómo empezar la próxima conversación

1. Abrir Claude Code apuntando a esta carpeta.
2. Leer `CLAUDE.md`, este `CONTEXTO.md` y `docs/LEARNINGS.md`.
3. Tomar el primer pendiente y aplicar el ciclo (confirmando con el usuario).
4. Al terminar, registrar lo hecho en `docs/LEARNINGS.md`.
