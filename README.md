# Taller de Ideas — versión Streamlit

Métodos y técnicas de creatividad guiadas para resolver problemas, solo o en
equipo: **SCAMPER**, **Design Thinking**, **Double Diamond**, **CPS (Creative
Problem Solving)**, **TRIZ**, **Foresight · Previsión Estratégica** (Tendencias +
Escenarios, Backcasting, PESTEL), **Seis Sombreros para Pensar** y
**Brainstorming** (clásico, Brainwriting 6-3-5, mapa mental). Incluye un
recomendador que usa la API de Anthropic para sugerir qué método o técnica
usar según tu situación, un botón "✨ Sugerir con IA" en cada paso de cada
método/técnica para generar ideas nuevas cuando te quedas trabado, y en
Design Thinking → Prototipar un botón para que la IA dibuje un boceto
(wireframe SVG) de tu prototipo.

Esta es la versión Streamlit del [artifact original](https://claude.ai/artifact/F6evJRQh6HZwaJWQ3BiNbk).
Se comporta distinto porque Streamlit es un framework de Python que necesita un
proceso corriendo, no una página estática:

- El progreso vive en memoria (`st.session_state`) mientras la pestaña /
  proceso está abierto. Se pierde al cerrar o reiniciar — exporta a Markdown
  antes de cerrar si quieres conservarlo.
- El asistente de IA necesita tu propia API key de Anthropic (no usa ninguna
  cuenta de Claude compartida).
- El cronómetro de Seis Sombreros y Brainstorming clásico avanza con el reloj
  real, pero el número en pantalla solo se actualiza cuando interactúas con
  algo (Streamlit no hace auto-refresh en vivo salvo que agregues un paquete
  adicional como `streamlit-autorefresh`).

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecutar localmente

```bash
streamlit run app.py
```

Se abre en `http://localhost:8501`.

## Configurar el asistente de IA (opcional)

El recomendador funciona sin configuración adicional: solo pega tu API key de
Anthropic en la barra lateral cuando abras la app (se usa solo en memoria,
durante esa sesión).

Si prefieres no pegarla cada vez, puedes definirla como variable de entorno:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
streamlit run app.py
```

o como secreto de Streamlit, creando `.streamlit/secrets.toml`:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

Si el modelo configurado en la barra lateral (por defecto `claude-haiku-4-5`,
rápido y económico) deja de existir o cambia de nombre, revisa el listado
vigente en
[platform.claude.com/docs/en/about-claude/models/overview](https://platform.claude.com/docs/en/about-claude/models/overview)
y actualiza el campo "Modelo" en la barra lateral (por ejemplo a
`claude-sonnet-5` si quieres respuestas de mayor calidad, a costo de ser un
poco más lento).

## Subir esto a GitHub

Esta carpeta ya viene con un repositorio git inicializado (rama `main`, con
un primer commit hecho). Solo falta conectarla a GitHub:

1. Entra a [github.com/new](https://github.com/new), crea un repositorio
   nuevo (por ejemplo `taller-ideas`) **sin** marcar "Add a README" ni
   `.gitignore` (para que no choque con los que ya trae esta carpeta).
2. Copia la URL que te da GitHub (algo como
   `https://github.com/tu-usuario/taller-ideas.git`).
3. Desde una terminal, dentro de esta carpeta, corre:
   ```bash
   git remote add origin https://github.com/tu-usuario/taller-ideas.git
   git push -u origin main
   ```
   Te pedirá tu usuario y una contraseña — GitHub ya no acepta tu contraseña
   normal ahí, necesitas un
   [Personal Access Token](https://github.com/settings/tokens) (clásico,
   con permiso `repo`) y lo pegas como si fuera la contraseña. Si tienes
   instalado [GitHub CLI](https://cli.github.com/), es más simple:
   ```bash
   gh repo create taller-ideas --public --source=. --remote=origin --push
   ```
   (te autentica con tu cuenta desde el navegador, sin pedirte tokens).

A partir de ahí, cualquier cambio futuro es el flujo normal de git:
`git add -A && git commit -m "..." && git push`.

## Desplegar en la nube

La forma más simple y gratuita es
[Streamlit Community Cloud](https://streamlit.io/cloud):

1. Con el repo ya en GitHub (paso anterior).
2. En Streamlit Community Cloud, "New app" → elige el repo y `app.py` como
   archivo principal.
3. En **Settings → Secrets** del app desplegado, agrega:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
   (opcional — si no lo agregas, cada visitante puede pegar su propia key en
   la barra lateral).

También funciona en cualquier otro servicio que corra un contenedor con
Python (Hugging Face Spaces con SDK "Streamlit", Render, Railway, un VPS
propio con `streamlit run app.py --server.port 8501`, etc.).

## Diseño

La app tiene una identidad visual propia (no el tema gris por defecto de
Streamlit): tipografía **Fredoka** (títulos, redondeada y amigable) +
**Nunito Sans** (texto, muy legible), fondo cálido, un color vívido por
método/técnica (con texto blanco u oscuro elegido para mantener buen
contraste) y componentes redondeados con estados de foco visibles. Se
controla desde dos archivos:

- `.streamlit/config.toml` — paleta base de Streamlit (fondo, color primario,
  texto).
- `styles.py` — CSS adicional (tipografía, tarjetas, botones, barra de
  progreso). Si quieres cambiar colores o fuentes, edita `THEME` en
  `data.py` y `styles.py`.

Si personalizas el CSS: evita aplicar `font-family` a elementos `<span>` o
selectores comodín como `[class*="st-"]` con `!important` — Streamlit dibuja
varios de sus íconos (mostrar contraseña, flechas de expander, checks) como
texto con una fuente de íconos dentro de un `<span>`, y forzar la tipografía
ahí los rompe (se ve el nombre del ícono en texto en vez del ícono).

Otro punto importante: **todos los botones tienen fondo explícito** (blanco,
`var(--surface)`) y `styles.py` fuerza `color-scheme: light` en todo el
documento. Si algún visitante tiene su sistema operativo o su Streamlit en
modo oscuro, sin esto los botones "secundarios" (los que no llevan
`type="primary"`) heredan el fondo casi negro del tema oscuro de Streamlit,
mientras el texto se queda oscuro por nuestro CSS — el resultado es texto
invisible sobre fondo negro. Si agregas un botón o componente nuevo, dale
siempre un fondo explícito en vez de dejar que herede el tema activo.

## Estructura del proyecto

```
app.py             # punto de entrada, barra lateral, enrutado
data.py            # contenido estático: métodos, pasos, sombreros, principios TRIZ
state.py           # estructura de st.session_state y cálculo de progreso
export_utils.py     # genera el Markdown exportable de una sesión
advisor.py         # llamadas a la API de Anthropic: recomendador de método y
                   # generador de sugerencias de ideas por paso
ui.py              # widgets reutilizables (captura de ideas + botón de IA, pasos, cronómetro)
views.py           # las 8 vistas de método + inicio + selector de método
requirements.txt
```

## Diferencias conocidas frente al artifact original

- Sin multi-sesión guardada en el navegador: una sesión activa a la vez
  (puedes exportar antes de "Empezar una sesión nueva").
- El asistente de IA requiere tu propia API key en vez de usar tu sesión de
  Claude automáticamente.
- El cronómetro no hace tick en vivo sin interacción (ver arriba).

Si quieres que agregue persistencia en archivo/JSON entre ejecuciones, se
puede extender desde aquí.
