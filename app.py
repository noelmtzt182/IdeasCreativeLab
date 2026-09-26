"""Taller de Ideas — versión Streamlit.

Métodos y técnicas de creatividad guiadas (SCAMPER, Design Thinking, Double
Diamond, CPS, TRIZ, Seis Sombreros y Brainstorming con variantes), con un
recomendador que usa la API de Anthropic para sugerir qué usar según tu reto.

Ejecutar localmente:
    pip install -r requirements.txt
    streamlit run app.py
"""
import streamlit as st

from state import ensure_session_state, reset_session
from styles import inject_css
from views import render_home, render_session_bar, render_method_select, METHOD_RENDERERS

st.set_page_config(page_title="Taller de Ideas", page_icon="💡", layout="wide")

ensure_session_state()
inject_css()

with st.sidebar:
    st.markdown("### 💡 Taller de Ideas")
    st.caption("Métodos de creatividad guiados")
    st.divider()

    st.markdown("**Asistente de IA (opcional)**")
    st.session_state.api_key = st.text_input(
        "API key de Anthropic", value=st.session_state.api_key, type="password",
        help="Se usa solo en esta sesión, para pedirle una recomendación a Claude. "
             "También puedes definir la variable de entorno ANTHROPIC_API_KEY o un "
             "secreto de Streamlit con ese nombre en vez de pegarla aquí.",
    )
    st.session_state.model_id = st.text_input(
        "Modelo", value=st.session_state.model_id,
        help="Revisa el ID de modelo vigente en docs.claude.com/en/docs/about-claude/models "
             "si esta recomendación deja de funcionar.",
    )

    st.divider()
    if st.button("🔄 Empezar una sesión nueva", use_container_width=True):
        reset_session()
        st.rerun()

    st.caption("El progreso vive solo en memoria mientras esta pestaña esté abierta. "
               "Exporta tu sesión a Markdown antes de cerrarla.")

# --- Enrutado principal -------------------------------------------------
if not st.session_state.started:
    render_home()
else:
    render_session_bar()
    st.divider()
    if st.session_state.method is None:
        render_method_select()
    else:
        renderer = METHOD_RENDERERS.get(st.session_state.method)
        if renderer:
            renderer()
        else:
            st.error("Método desconocido. Vuelve al inicio.")
            st.session_state.method = None
            st.rerun()
