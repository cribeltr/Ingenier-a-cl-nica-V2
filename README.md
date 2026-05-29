# Gestión de Equipos Biomédicos Críticos (HHHA)

Sistema offline de un solo archivo para gestionar equipos biomédicos críticos:
estado de cada equipo, ciclo correctivo, mantención preventiva por mes,
pendientes y conciliación con el archivo maestro.

## Cómo se trabaja en este proyecto

Las reglas de trabajo están en **`CLAUDE.md`** (en la raíz). Claude Code lo lee
solo al abrir esta carpeta y queda obligado a:

- Confirmar contigo antes de cambiar algo.
- Revisar el programa completo y simular en cada ajuste.
- Hablar en español, breve y sin tecnicismos.
- Pensar como experto (no ejecutar literal).
- Dejar por escrito lo aprendido en `docs/LEARNINGS.md`.

## Qué hay en cada carpeta

- **`build_app.py`** — el código fuente. Es lo que se edita. Genera `app.html`.
- **`app.html`** — la aplicación lista para abrir en el navegador (no editar a mano).
- **`seed.json`** — datos iniciales embebidos (893 equipos).
- **`CLAUDE.md`** — reglas de trabajo.
- **`docs/CONTEXTO.md`** — traspaso: la historia del proyecto y lo pendiente.
- **`docs/LEARNINGS.md`** — memoria: lo aprendido sesión a sesión.
- **`docs/`** — especificación y archivos de referencia.
- **`sesiones/`** — grabaciones de uso real (para revisar y mejorar).
- **`data/`** — respaldos del estado.
- **`exports/`** — exportaciones a Excel.
- **`plantillas/`** — plantillas de asignación de MP por mes.

## Para usar la aplicación

Abrir `app.html` con doble clic en cualquier navegador. Funciona 100% sin internet.

## Para regenerar la aplicación tras un cambio

Editar `build_app.py` y ejecutar:

```
python3 build_app.py
```
