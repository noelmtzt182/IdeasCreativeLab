"""Inyección de CSS + tipografía para darle a la app una identidad visual propia:
divertida, con buen contraste, alineación consistente y legible para cualquier
persona. Se llama una sola vez desde app.py."""
import streamlit as st

from data import THEME


def inject_css():
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Nunito+Sans:opsz,wght@6..12,400;6..12,600;6..12,700;6..12,800&display=swap');

:root {{
  --primary: {THEME['primary']};
  --primary-dark: {THEME['primary_dark']};
  --bg: {THEME['bg']};
  --surface: {THEME['surface']};
  --surface-tint: {THEME['surface_tint']};
  --ink: {THEME['ink']};
  --ink-soft: {THEME['ink_soft']};
  --line: {THEME['line']};
  --success: {THEME['success']};
  --warning: {THEME['warning']};
  --danger: {THEME['danger']};
  color-scheme: light;
}}

/* Fuerza esquema claro pase lo que pase: si el visitante tiene su sistema u
   Streamlit en modo oscuro, sin esto los botones "secundarios" (sin fondo
   propio en nuestro CSS) heredan el fondo casi negro del tema oscuro de
   Streamlit, mientras el texto se queda en nuestro --ink oscuro → texto
   invisible sobre fondo negro. Bloquear color-scheme evita ese choque de
   temas por completo, en vez de depender de que .streamlit/config.toml
   gane siempre (el visitante puede tener guardada su propia preferencia). */
html {{ color-scheme: light !important; }}

/* ---------- Base: tipografía, tamaños, contraste ----------
   OJO: nunca aplicar font-family a `span` o a selectores comodín como
   [class*="st-"] con !important — Streamlit dibuja sus iconos (mostrar
   contraseña, flechas de expander, checks, etc.) como texto-ligadura
   dentro de <span> usando una fuente de íconos; forzar la tipografía ahí
   los convierte en texto literal ilegible ("visibility", "check", ...). */
html, body, .stApp, .stMarkdown, .stCaption, p, label, li {{
  font-family: 'Nunito Sans', -apple-system, 'Segoe UI', sans-serif;
  color: var(--ink);
}}
h1, h2, h3, h4, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {{
  font-family: 'Fredoka', 'Nunito Sans', sans-serif !important;
  font-weight: 600 !important;
  letter-spacing: -0.01em;
  color: var(--ink) !important;
}}
/* Los botones sí son texto plano nuestro (nunca íconos-ligadura), así que
   ahí sí forzamos la tipografía con seguridad. */
button, .stButton, .stDownloadButton, .stFormSubmitButton {{
  font-family: 'Nunito Sans', -apple-system, 'Segoe UI', sans-serif;
}}
html {{ font-size: 17px; }}
p, li, .stMarkdown, .stCaption, .stTextInput label, .stTextArea label {{ font-size: 1rem; line-height: 1.55; }}
.stCaption, [data-testid="stCaptionContainer"] {{ color: var(--ink-soft) !important; font-size: 0.92rem !important; }}

/* Alto contraste también en modo oscuro del sistema, si el visitante lo fuerza */
@media (prefers-color-scheme: dark) {{
  .stApp {{ background-color: var(--bg); }}
}}

.stApp {{ background-color: var(--bg); }}
.main .block-container {{
  max-width: 880px;
  padding-top: 2rem;
  padding-bottom: 4rem;
}}

/* ---------- Encabezados con acento de color ---------- */
.stApp h1 {{ font-size: 2.1rem; text-wrap: balance; }}
.stApp h1::after {{
  content: ""; display: block; width: 64px; height: 5px; margin-top: 10px; border-radius: 99px;
  background: linear-gradient(90deg, var(--primary), var(--warning));
}}

/* ---------- Botones: redondeados, juguetones, buen contraste ---------- */
/* OJO: fondo SIEMPRE explícito (var(--surface), blanco) en todos los estados.
   Si se deja sin fondo propio, el botón hereda el fondo del tema activo de
   Streamlit (que puede ser oscuro), y como el texto usa nuestro --ink oscuro,
   el botón se ve negro sobre negro — el bug de "no se ven los botones". */
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {{
  background: var(--surface) !important;
  border-radius: 14px !important;
  font-weight: 700 !important;
  font-family: 'Nunito Sans', sans-serif !important;
  padding: 0.55rem 1.1rem !important;
  border: 2px solid var(--line) !important;
  transition: transform 0.08s ease, box-shadow 0.15s ease, border-color 0.15s ease, background 0.15s ease;
  color: var(--ink) !important;
}}
.stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {{
  background: var(--surface-tint) !important;
  border-color: var(--primary) !important;
  color: var(--ink) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(109, 40, 217, 0.18);
}}
.stButton > button:active, .stFormSubmitButton > button:active {{
  background: var(--surface-tint) !important;
}}
.stButton > button p, .stFormSubmitButton > button p, .stDownloadButton > button p {{
  color: inherit !important;
}}
.stButton > button:focus-visible, .stFormSubmitButton > button:focus-visible {{
  outline: 3px solid var(--primary) !important;
  outline-offset: 2px;
}}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"], .stDownloadButton > button {{
  background: var(--primary) !important;
  border-color: var(--primary) !important;
  color: #FFFFFF !important;
}}
.stButton > button[kind="primary"]:hover, .stDownloadButton > button:hover {{
  background: var(--primary-dark) !important;
  border-color: var(--primary-dark) !important;
}}

/* ---------- Inputs: más amigables y con contraste claro ---------- */
.stTextInput input, .stTextArea textarea {{
  border-radius: 12px !important;
  border: 2px solid var(--line) !important;
  background: var(--surface) !important;
  color: var(--ink) !important;
  font-size: 1rem !important;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 3px rgba(109, 40, 217, 0.15) !important;
}}
.stTextInput label, .stTextArea label, .stCheckbox label p {{
  font-weight: 700 !important;
  color: var(--ink) !important;
}}

/* ---------- Contenedores con borde (tarjetas) ---------- */
[data-testid="stVerticalBlockBorderWrapper"] > div > [data-testid="stVerticalBlock"] {{
  gap: 0.5rem;
}}
div[data-testid="stExpander"], div[data-testid="stVerticalBlockBorderWrapper"] {{
  border-radius: 16px !important;
  border-color: var(--line) !important;
  background: var(--surface);
}}
div[data-testid="stExpander"] summary {{
  font-weight: 700 !important;
  font-family: 'Fredoka', sans-serif !important;
}}

/* ---------- Barra de progreso: gradiente divertido ---------- */
.stProgress > div > div > div > div {{
  background-image: linear-gradient(90deg, var(--primary), var(--warning)) !important;
  border-radius: 99px;
}}
.stProgress > div > div {{ border-radius: 99px; background: var(--line) !important; }}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {{
  background: var(--surface-tint) !important;
  border-right: 1px solid var(--line);
}}
[data-testid="stSidebar"] * {{ color: var(--ink) !important; }}

/* ---------- Alertas (info/success/warning/error) con más personalidad ---------- */
div[data-testid="stAlert"] {{
  border-radius: 14px !important;
  font-size: 1rem;
  border-width: 0 0 0 5px !important;
  border-style: solid !important;
}}

/* ---------- Checkbox más grande y fácil de tocar (accesibilidad) ---------- */
.stCheckbox {{ transform: scale(1.05); }}

/* ---------- Divisores sutiles ---------- */
hr {{ border-color: var(--line) !important; }}

/* ---------- Tabs / step-pills: alto contraste en estado activo ---------- */
.stButton > button[aria-pressed="true"] {{
  background: var(--primary) !important;
  color: #FFFFFF !important;
  border-color: var(--primary) !important;
}}
</style>
""",
        unsafe_allow_html=True,
    )
