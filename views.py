"""Todas las vistas de la app: inicio, selector de método, y los 7 flujos guiados."""
import streamlit as st

from data import (
    METHODS, GOALS, SCAMPER_STEPS, DT_LABELS, DD_LABELS, CPS_LABELS, TRIZ_LABELS,
    SIX_HATS, BRAIN_RULES, BRAIN_MODES, TRIZ_PRINCIPLES, method_by_id,
    FORESIGHT_MODES, FORESIGHT_SCENARIOS_LABELS, FORESIGHT_BACKCAST_LABELS, PESTEL_CATEGORIES,
)
from state import compute_progress, reset_session
from export_utils import build_export_text, slugify
from advisor import ask_advisor, has_api_key, ask_triz_suggestions, ask_prototype_sketch
from ui import method_header, step_tabs, nav_row, list_capture, timer_widget, badge


# ============================================================
# Inicio
# ============================================================

def render_home():
    st.markdown("##### MÉTODOS DE CREATIVIDAD GUIADOS")
    st.title("Convierte un problema difícil en una lista de ideas")
    st.write("Describe tu reto, elige un método probado, y avanza paso a paso — solo o con tu equipo.")

    cols = st.columns(4)
    steps = ["Cuenta tu reto", "Elige o pide recomendación", "Sigue el proceso guiado", "Exporta tus resultados"]
    for i, (c, s) in enumerate(zip(cols, steps)):
        c.markdown(f"**0{i + 1}**  \n{s}")

    st.divider()
    st.session_state.problem = st.text_area(
        "¿Cuál es el reto o problema que quieres resolver?",
        value=st.session_state.problem,
        placeholder="Ej. Nuestras entregas a domicilio llegan tarde y los clientes se quejan.",
        height=90,
    )
    if st.button("Comenzar →", type="primary"):
        st.session_state.started = True
        st.rerun()


def render_session_bar():
    """Barra compacta con el reto actual y opción de editarlo, mostrada una vez iniciada la sesión."""
    cols = st.columns([8, 2])
    with cols[0]:
        with st.expander(f'📝 "{st.session_state.problem or "(sin problema definido)"}"', expanded=False):
            st.session_state.problem = st.text_area("Editar el reto", value=st.session_state.problem, key="edit_problem_box")
    with cols[1]:
        if st.button("Inicio", use_container_width=True):
            st.session_state.started = False
            st.session_state.method = None
            st.rerun()
    if st.session_state.method:
        pct = compute_progress(st.session_state.method)
        st.caption(f"Progreso: {pct}%")


# ============================================================
# Selector de método / recomendador
# ============================================================

def render_method_select():
    st.markdown("###### PASO 2")
    st.subheader("Elige qué usar para tu reto")
    st.caption(f'"{st.session_state.problem or "(sin problema definido)"}"')

    with st.container(border=True):
        st.markdown("#### 🎯 ¿Qué quieres lograr?")
        st.caption("Elige la opción más parecida a tu objetivo y vas directo a la herramienta indicada.")
        for g in GOALS:
            gm = method_by_id(g["id"])
            c1, c2 = st.columns([1, 11])
            with c1:
                st.markdown(
                    f'<div style="width:14px;height:14px;border-radius:5px;background:{gm["color"]};'
                    f'margin-top:10px;"></div>',
                    unsafe_allow_html=True,
                )
            with c2:
                if st.button(g["label"], key=f"goal_{g['id']}", use_container_width=True):
                    st.session_state.method = g["id"]
                    st.rerun()

        st.markdown("&nbsp;")
        st.markdown("#### 🤖 ¿No estás seguro? Pregúntale al asistente")
        render_advisor()

    st.divider()
    st.markdown("## Métodos")
    st.caption("Procesos completos, varias etapas")
    _render_method_grid([m for m in METHODS if m["category"] == "metodo"])

    st.markdown("## Técnicas y herramientas")
    st.caption("Generadores puntuales de ideas")
    _render_method_grid([m for m in METHODS if m["category"] == "tecnica"])


def _render_method_grid(items):
    cols = st.columns(2)
    for i, m in enumerate(items):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(
                    f'<div style="height:6px;border-radius:99px;background:{m["color"]};margin:-1rem -1rem 0.8rem;"></div>',
                    unsafe_allow_html=True,
                )
                badge(m["code"], m["color"], m.get("text_on", "white"))
                st.markdown(f"**{m['name']}**  \n{m['tagline']}")
                st.caption(f"Ideal para: {m['best_for']} · {m['time']}")
                if st.button("Elegir", key=f"choose_{m['id']}", use_container_width=True):
                    st.session_state.method = m["id"]
                    st.rerun()


def render_advisor():
    adv = st.session_state.advisor
    if not has_api_key():
        st.caption("Configura tu API key de Anthropic en la barra lateral para activar el asistente.")

    text = st.text_area(
        "Cuéntame tu situación",
        value=adv.get("input", ""),
        placeholder="Ej. Tengo que rediseñar el proceso de onboarding, ya existe pero está desordenado...",
        key="advisor_input_box",
        label_visibility="collapsed",
        height=80,
    )
    if st.button("Preguntar", key="ask_advisor_btn"):
        adv["input"] = text
        if not text.strip():
            st.warning("Escribe primero tu situación.")
        else:
            with st.spinner("Pensando en la mejor opción para ti…"):
                result = ask_advisor(text.strip())
            st.session_state.advisor = {**adv, **result}
            st.rerun()

    if adv.get("status") == "unavailable":
        st.warning("El asistente con IA no está disponible: agrega tu API key de Anthropic en la barra lateral.")
    elif adv.get("status") == "error":
        st.error(adv.get("error") or "Algo salió mal. Intenta de nuevo.")
    elif adv.get("status") == "done":
        m = method_by_id(adv["id"])
        if m:
            st.success(f"**Recomendación: {m['name']}**\n\n{adv.get('reason', '')}")
            if st.button(f"Usar {'esta técnica' if m['category'] == 'tecnica' else 'este método'}", key="use_advisor_rec", type="primary"):
                st.session_state.method = m["id"]
                st.session_state.advisor = {"status": "idle", "input": "", "id": None, "reason": None, "error": None}
                st.rerun()


# ============================================================
# Export helper (usado en cada resumen)
# ============================================================

def render_export_button(method):
    text = build_export_text(st.session_state.problem, method, st.session_state.data)
    filename = f"taller-ideas-{method}-{slugify(st.session_state.problem)}.md"
    st.download_button("⬇ Exportar sesión (.md)", data=text, file_name=filename, mime="text/markdown",
                        key=f"export_{method}")


def render_change_method_button():
    if st.button("← Cambiar método", key="change_method_top"):
        st.session_state.method = None
        st.rerun()


# ============================================================
# SCAMPER
# ============================================================

def render_scamper():
    m = method_by_id("scamper")
    d = st.session_state.data["scamper"]
    method_header(m)
    render_change_method_button()
    idx = d["step"]
    labels = [s["key"] for s in SCAMPER_STEPS]
    step_tabs(labels, idx, "scamper", ("scamper", "step"))

    if idx < len(SCAMPER_STEPS):
        st_ = SCAMPER_STEPS[idx]
        with st.container(border=True):
            st.markdown(f"#### {st_['key']} — {st_['title']}")
            for p in st_["prompts"]:
                st.markdown(f"— {p}")
            list_capture(d[st_["key"]], f"scamper_{st_['key']}", f'Escribe una idea para "{st_["title"]}"...',
                         ai_label=f"SCAMPER — {st_['title']} ({', '.join(st_['prompts'])})")
        nav_row(idx, len(SCAMPER_STEPS), "scamper", ("scamper", "step"))
    else:
        _render_scamper_summary(d, m)


def _render_scamper_summary(d, m):
    total = sum(len(d[s["key"]]) for s in SCAMPER_STEPS)
    st.markdown(f"### Resumen SCAMPER — {total} ideas en total")
    for st_ in SCAMPER_STEPS:
        with st.expander(f"{st_['key']} — {st_['title']} ({len(d[st_['key']])})", expanded=bool(d[st_["key"]])):
            if d[st_["key"]]:
                for it in d[st_["key"]]:
                    st.markdown(f"- {it}")
            else:
                st.caption("Sin ideas.")
    render_export_button("scamper")


# ============================================================
# Design Thinking
# ============================================================

def _render_prototype_sketch(proto):
    store = st.session_state.setdefault("ai_suggestions", {})
    key = "dt_sketch"
    has_sketch = bool(proto.get("sketch_svg"))
    label = "🔄 Regenerar boceto con IA" if has_sketch else "🎨 Generar boceto con IA"

    if st.button(label, key=f"{key}_btn"):
        if not has_api_key():
            store[key] = {"status": "unavailable"}
        else:
            with st.spinner("Dibujando un boceto…"):
                store[key] = ask_prototype_sketch(proto.get("description", ""), st.session_state.get("problem", ""))
            if store[key].get("status") == "done":
                proto["sketch_svg"] = store[key]["svg"]
        st.rerun()

    result = store.get(key)
    if result and result.get("status") == "unavailable":
        st.caption("Agrega tu API key de Anthropic en la barra lateral para generar un boceto con IA.")
    elif result and result.get("status") == "error":
        st.warning(result.get("error") or "Algo salió mal generando el boceto.")

    if proto.get("sketch_svg"):
        with st.container(border=True):
            st.markdown(
                f'<div style="max-width:480px;margin:0 auto;">{proto["sketch_svg"]}</div>',
                unsafe_allow_html=True,
            )
            st.caption("Boceto ilustrativo generado por IA a partir de tu descripción — no es un diseño final.")


def render_design_thinking():
    m = method_by_id("design-thinking")
    d = st.session_state.data["design_thinking"]
    method_header(m)
    render_change_method_button()
    idx = d["step"]
    step_tabs(DT_LABELS, idx, "dt", ("design_thinking", "step"))

    if idx >= len(DT_LABELS):
        _render_dt_summary(d)
        return

    with st.container(border=True):
        if idx == 0:
            st.markdown("#### Empatizar")
            st.markdown("— ¿Quién vive este problema de cerca?  \n— ¿Qué observas, escuchas o sabes de esas personas?  \n— ¿Qué necesidades no dichas podrían tener?")
            list_capture(d["empathize"], "dt_empathize", "Una observación, cita o necesidad detectada...",
                         ai_label="Design Thinking — Empatizar: observaciones, citas o necesidades no dichas de las personas afectadas")
        elif idx == 1:
            st.markdown("#### Definir")
            st.caption("Construye tu declaración de punto de vista (POV):")
            d["define"]["user"] = st.text_input("¿Quién es la persona?", value=d["define"]["user"], placeholder="Ej. un repartidor nuevo")
            d["define"]["need"] = st.text_input("¿Qué necesita?", value=d["define"]["need"], placeholder="Ej. conocer la ruta más rápida")
            d["define"]["insight"] = st.text_input("¿Por qué? (insight)", value=d["define"]["insight"], placeholder="Ej. el tráfico cambia cada hora")
            st.info(f"{d['define']['user'] or '[Persona]'} necesita {d['define']['need'] or '[necesidad]'} porque {d['define']['insight'] or '[insight]'}.")
        elif idx == 2:
            st.markdown("#### Idear")
            st.caption("Genera tantas ideas como puedas, sin juzgarlas todavía. Meta sugerida: 15 ideas.")
            st.progress(min(1.0, len(d["ideate"]) / 15))
            list_capture(d["ideate"], "dt_ideate", "Una idea nueva, por alocada que parezca...",
                         ai_label="Design Thinking — Idear: ideas de solución para la necesidad definida, sin filtrar")
        elif idx == 3:
            st.markdown("#### Prototipar")
            st.caption("Describe un prototipo simple: un boceto, un storyboard, una maqueta de papel, un guion de rol-play.")
            d["prototype"]["description"] = st.text_area("Descripción del prototipo", value=d["prototype"]["description"],
                                                           placeholder="Describe cómo se vería o funcionaría...")
            _render_prototype_sketch(d["prototype"])
            st.caption("Preguntas abiertas que quieres resolver al probarlo")
            list_capture(d["prototype"]["questions"], "dt_proto_q", "Una pregunta abierta sobre tu prototipo...",
                         ai_label="Design Thinking — Prototipar: preguntas abiertas que el prototipo debería resolver al probarlo")
        elif idx == 4:
            st.markdown("#### Testear")
            st.caption("Comparte tu prototipo con alguien real y registra lo que aprendes.")
            st.markdown("**Qué funcionó**")
            list_capture(d["test"]["worked"], "dt_worked", "Algo que funcionó bien...")
            st.markdown("**Qué no funcionó**")
            list_capture(d["test"]["didnt_work"], "dt_notworked", "Algo que no funcionó...")
            st.markdown("**Ajustes o nuevas ideas**")
            list_capture(d["test"]["adjustments"], "dt_adjust", "Un ajuste a partir del feedback...",
                         ai_label="Design Thinking — Testear: posibles ajustes o mejoras a partir de feedback típico de usuarios probando este tipo de prototipo")

    nav_row(idx, len(DT_LABELS), "dt", ("design_thinking", "step"))


def _render_dt_summary(d):
    st.markdown("### Resumen Design Thinking")
    with st.expander("Empatizar", expanded=True):
        for it in d["empathize"] or []:
            st.markdown(f"- {it}")
        if not d["empathize"]:
            st.caption("Sin registros.")
    with st.expander("Definir", expanded=True):
        de = d["define"]
        if de["user"] or de["need"] or de["insight"]:
            st.info(f"{de['user'] or '[Persona]'} necesita {de['need'] or '[necesidad]'} porque {de['insight'] or '[insight]'}.")
        else:
            st.caption("Sin definir.")
    with st.expander(f"Idear ({len(d['ideate'])})"):
        for it in d["ideate"]:
            st.markdown(f"- {it}")
    with st.expander("Prototipar"):
        st.write(d["prototype"]["description"] or "Sin descripción.")
        if d["prototype"].get("sketch_svg"):
            st.markdown(
                f'<div style="max-width:400px;margin:0.5rem auto;">{d["prototype"]["sketch_svg"]}</div>',
                unsafe_allow_html=True,
            )
    with st.expander("Testear"):
        st.caption(f"{len(d['test']['worked'])} funcionó · {len(d['test']['didnt_work'])} no funcionó · {len(d['test']['adjustments'])} ajustes")
    render_export_button("design-thinking")


# ============================================================
# Double Diamond
# ============================================================

def render_double_diamond():
    m = method_by_id("double-diamond")
    d = st.session_state.data["double_diamond"]
    method_header(m)
    render_change_method_button()
    idx = d["step"]
    step_tabs(DD_LABELS, idx, "dd", ("double_diamond", "step"))

    if idx >= len(DD_LABELS):
        _render_dd_summary(d)
        return

    with st.container(border=True):
        if idx == 0:
            st.markdown("#### Descubrir")
            st.caption("Explora ampliamente antes de decidir nada. Este es el primer rombo: se abre.")
            list_capture(d["discover"], "dd_discover", "Un hallazgo, observación o pregunta...",
                         ai_label="Double Diamond — Descubrir: hallazgos, ángulos u observaciones a explorar sobre el problema, de forma amplia")
        elif idx == 1:
            st.markdown("#### Definir")
            st.caption("Cierra el primer rombo: sintetiza todo lo descubierto en una definición clara.")
            d["problem_statement"] = st.text_area("Declaración del problema", value=d["problem_statement"],
                                                    placeholder="En una o dos frases, ¿cuál es el problema real?")
            st.caption("Criterios de éxito")
            list_capture(d["success_criteria"], "dd_criteria", "¿Cómo sabrás que lo resolviste?",
                         ai_label="Double Diamond — Definir: criterios de éxito medibles para saber si el problema quedó resuelto")
        elif idx == 2:
            st.markdown("#### Desarrollar")
            st.caption("Segundo rombo, se abre de nuevo: genera y explora posibles soluciones sin elegir todavía.")
            list_capture(d["develop"], "dd_develop", "Una posible solución a explorar...",
                         ai_label="Double Diamond — Desarrollar: posibles soluciones a explorar para el problema ya definido")
        elif idx == 3:
            st.markdown("#### Entregar")
            st.caption("Cierra el segundo rombo: elige, refina y planea cómo entregarla.")
            d["chosen_solution"] = st.text_area("Solución elegida", value=d["chosen_solution"],
                                                 placeholder="Describe la solución final...")
            st.caption("Próximos pasos para entregarla")
            list_capture(d["next_steps"], "dd_next", "Un paso concreto para entregar la solución...",
                         ai_label="Double Diamond — Entregar: próximos pasos concretos para implementar la solución elegida")

    nav_row(idx, len(DD_LABELS), "dd", ("double_diamond", "step"))


def _render_dd_summary(d):
    st.markdown("### Resumen Double Diamond")
    with st.expander("Descubrir", expanded=True):
        for it in d["discover"]:
            st.markdown(f"- {it}")
        if not d["discover"]:
            st.caption("Sin registros.")
    with st.expander("Definir", expanded=True):
        st.write(d["problem_statement"] or "Sin definir.")
        for it in d["success_criteria"]:
            st.markdown(f"- {it}")
    with st.expander(f"Desarrollar ({len(d['develop'])})"):
        for it in d["develop"]:
            st.markdown(f"- {it}")
    with st.expander("Entregar"):
        st.write(d["chosen_solution"] or "Sin definir.")
        for it in d["next_steps"]:
            st.markdown(f"- {it}")
    render_export_button("double-diamond")


# ============================================================
# CPS
# ============================================================

def render_cps():
    m = method_by_id("cps")
    d = st.session_state.data["cps"]
    method_header(m)
    render_change_method_button()
    idx = d["step"]
    step_tabs(CPS_LABELS, idx, "cps", ("cps", "step"))

    if idx >= len(CPS_LABELS):
        _render_cps_summary(d)
        return

    with st.container(border=True):
        if idx == 0:
            st.markdown("#### Clarificar")
            st.caption("Nombra el reto como una pregunta abierta e invitante.")
            d["challenge"] = st.text_input("¿Cómo podríamos...?", value=d["challenge"],
                                            placeholder="¿Cómo podríamos reducir el tiempo de espera sin subir costos?")
            st.caption("Hechos y datos relevantes")
            list_capture(d["facts"], "cps_facts", "¿Qué sabemos con certeza? ¿Qué suposiciones hacemos?",
                         ai_label="CPS — Clarificar: hechos, datos o suposiciones relevantes sobre el reto")
        elif idx == 1:
            st.markdown("#### Idear")
            st.caption("Genera tantas alternativas como puedas para tu reto, sin filtrarlas todavía.")
            list_capture(d["ideate"], "cps_ideate", "Una alternativa para el reto...",
                         ai_label="CPS — Idear: alternativas de solución al reto, combinando pensamiento lógico e imaginativo")
        elif idx == 2:
            st.markdown("#### Desarrollar")
            st.caption("Elige la idea o ideas más prometedoras y fortalécelas.")
            d["best_idea"] = st.text_area("Idea(s) más prometedora(s)", value=d["best_idea"],
                                           placeholder="¿Cuál idea tiene más potencial?")
            st.caption("Cómo fortalecerla")
            list_capture(d["strengthen"], "cps_strengthen", "¿Qué la haría más viable? ¿Qué obstáculo resolver primero?",
                         ai_label="CPS — Desarrollar: formas de fortalecer o hacer más viable la idea elegida")
        elif idx == 3:
            st.markdown("#### Implementar")
            st.caption("Convierte la idea fortalecida en un plan de acción concreto.")
            st.caption("Plan de acción")
            list_capture(d["action_plan"], "cps_plan", "Un paso concreto: quién lo hace y para cuándo...",
                         ai_label="CPS — Implementar: pasos concretos de un plan de acción para ejecutar la idea")
            d["support"] = st.text_area("Apoyo y recursos necesarios", value=d["support"],
                                         placeholder="¿Qué o quién necesitas para lograrlo?")

    nav_row(idx, len(CPS_LABELS), "cps", ("cps", "step"))


def _render_cps_summary(d):
    st.markdown("### Resumen CPS")
    with st.expander("Clarificar", expanded=True):
        st.write(d["challenge"] or "Sin definir.")
        for it in d["facts"]:
            st.markdown(f"- {it}")
    with st.expander(f"Idear ({len(d['ideate'])})"):
        for it in d["ideate"]:
            st.markdown(f"- {it}")
    with st.expander("Desarrollar"):
        st.write(d["best_idea"] or "Sin definir.")
        for it in d["strengthen"]:
            st.markdown(f"- {it}")
    with st.expander("Implementar"):
        for it in d["action_plan"]:
            st.markdown(f"- {it}")
        st.write(d["support"] or "Sin apoyo/recursos definidos.")
    render_export_button("cps")


# ============================================================
# Seis Sombreros
# ============================================================

def render_six_hats():
    m = method_by_id("six-hats")
    d = st.session_state.data["six_hats"]
    method_header(m)
    render_change_method_button()
    idx = d["step"]
    labels = [h["name"] for h in SIX_HATS]
    step_tabs(labels, idx, "hats", ("six_hats", "step"))

    if idx < len(SIX_HATS):
        h = SIX_HATS[idx]
        with st.container(border=True):
            st.markdown(
                f'<span style="display:inline-block;width:14px;height:14px;border-radius:50%;'
                f'background:{h["color"]};border:1px solid #8886;margin-right:8px;"></span>'
                f'**Sombrero {h["name"]} — {h["label"]}**',
                unsafe_allow_html=True,
            )
            for p in h["prompts"]:
                st.markdown(f"— {p}")
            timer_widget(f"six-hats:{h['key']}", f"hats_{h['key']}")
            list_capture(d["hats"][h["key"]], f"hats_{h['key']}_list", f'Un pensamiento desde el sombrero {h["name"]}...',
                         ai_label=f"Seis Sombreros — {h['name']} ({h['label']}): {' '.join(h['prompts'])}")
        nav_row(idx, len(SIX_HATS), "hats", ("six_hats", "step"))
    else:
        _render_hats_summary(d)


def _render_hats_summary(d):
    st.markdown("### Resumen — Seis Sombreros")
    for h in SIX_HATS:
        items = d["hats"][h["key"]]
        with st.expander(f"{h['name']} — {h['label']} ({len(items)})", expanded=bool(items)):
            for it in items:
                st.markdown(f"- {it}")
            if not items:
                st.caption("Sin registros.")
    render_export_button("six-hats")


# ============================================================
# Brainstorming y variantes
# ============================================================

def render_brainstorming():
    m = method_by_id("brainstorming")
    d = st.session_state.data["brainstorming"]
    method_header(m)
    render_change_method_button()

    if not d["sub_mode"]:
        st.caption("Elige cómo quieres generar ideas:")
        cols = st.columns(3)
        for c, bm in zip(cols, BRAIN_MODES):
            with c:
                with st.container(border=True):
                    st.markdown(f"**{bm['name']}**")
                    st.caption(bm["desc"])
                    if st.button("Elegir", key=f"brain_mode_{bm['id']}", use_container_width=True):
                        d["sub_mode"] = bm["id"]
                        st.rerun()
        return

    if st.button("← Elegir otra variante", key="brain_change_mode"):
        d["sub_mode"] = None
        st.rerun()

    if d["sub_mode"] == "classic":
        _render_brain_classic(d)
    elif d["sub_mode"] == "brainwriting":
        _render_brainwriting(d)
    elif d["sub_mode"] == "mindmap":
        _render_mindmap(d)


def _render_brain_classic(d):
    with st.container(border=True):
        st.markdown("#### Brainstorming clásico")
        for i, r in enumerate(BRAIN_RULES):
            st.markdown(f"**{i + 1}.** {r}")
        timer_widget("classic", "brain_classic")
        list_capture(d["classic"]["ideas"], "brain_classic_list", "Escribe una idea, sin filtrarla...", starable=True,
                     ai_label="Brainstorming clásico: ideas rápidas y variadas para el reto, sin filtrar ni juzgar")
    render_export_button("brainstorming")


def _render_brainwriting(d):
    bw = d["brainwriting"]
    ri = bw["round"]
    with st.container(border=True):
        st.markdown("#### Brainwriting 6-3-5")
        st.caption("Tradicionalmente: 6 personas, 3 ideas cada una, 5 rondas de 5 minutos, pasando la hoja. "
                   "Aquí puedes simular las rondas tú solo o en equipo usando una sola pantalla.")
        st.markdown(f"**Ronda {ri + 1} de 5**")
        if ri > 0 and bw["rounds"][ri - 1]:
            with st.expander("Ideas de la ronda anterior (para inspirarte o evolucionar)", expanded=True):
                for it in bw["rounds"][ri - 1]:
                    st.markdown(f"- {it}")
        list_capture(bw["rounds"][ri], f"bw_round_{ri}", "Una idea nueva o evolucionada para esta ronda...",
                     ai_label=f"Brainwriting 6-3-5, ronda {ri + 1}: ideas nuevas o evoluciones de la ronda anterior")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Ronda anterior", disabled=ri <= 0, key="bw_prev"):
                bw["round"] = max(0, ri - 1)
                st.rerun()
        with c2:
            if ri < 4:
                if st.button("Siguiente ronda →", type="primary", key="bw_next", use_container_width=True):
                    bw["round"] = min(4, ri + 1)
                    st.rerun()
    render_export_button("brainstorming")


def _render_mindmap(d):
    mm = d["mindmap"]
    with st.container(border=True):
        st.markdown("#### Mapa mental")
        st.info(st.session_state.problem or "Tu problema")
        with st.form("mm_add_branch", clear_on_submit=True):
            name = st.text_input("Nombre de una rama principal (un tema o dirección)...", label_visibility="collapsed")
            if st.form_submit_button("Agregar rama") and name.strip():
                mm["branches"].append({"name": name.strip(), "ideas": []})
                st.rerun()

        if not mm["branches"]:
            st.caption("Agrega tu primera rama para empezar a ramificar el problema.")
        for bi, br in enumerate(mm["branches"]):
            with st.expander(f"🌿 {br['name']}", expanded=True):
                new_name = st.text_input("Nombre de la rama", value=br["name"], key=f"mm_branch_name_{bi}")
                br["name"] = new_name
                list_capture(br["ideas"], f"mm_branch_{bi}", "Una idea bajo esta rama...",
                             ai_label=f"Mapa mental — rama \"{br['name'] or 'sin nombre'}\": ideas específicas bajo este tema")
                if st.button("Eliminar rama", key=f"mm_del_branch_{bi}"):
                    mm["branches"].pop(bi)
                    st.rerun()
    render_export_button("brainstorming")


# ============================================================
# TRIZ
# ============================================================

def render_triz():
    m = method_by_id("triz")
    d = st.session_state.data["triz"]
    method_header(m)
    render_change_method_button()
    idx = d["step"]
    step_tabs(TRIZ_LABELS, idx, "triz", ("triz", "step"))

    if idx == 0:
        with st.container(border=True):
            st.markdown("#### ¿Qué es TRIZ?")
            st.write(
                "TRIZ es una metodología desarrollada a partir del análisis de miles de patentes. "
                "Su idea central: la mayoría de los problemas de diseño esconden una **contradicción** "
                "— mejorar algo empeora otra cosa — y esa contradicción ya fue resuelta antes, en otro "
                "contexto, con uno de 40 principios de inventiva reutilizables."
            )
            st.write(
                "Esta versión es un checklist exploratorio y simplificado, no la matriz de contradicciones "
                "completa: te ayuda a nombrar tu contradicción y navegar los 40 principios para encontrar "
                "inspiración aplicable."
            )
        nav_row(idx, len(TRIZ_LABELS), "triz", ("triz", "step"))
    elif idx == 1:
        with st.container(border=True):
            st.markdown("#### Nombra tu contradicción")
            d["improve"] = st.text_input("¿Qué característica quieres mejorar?", value=d["improve"],
                                          placeholder="Ej. la velocidad de entrega")
            d["worsen"] = st.text_input("¿Qué empeora cuando intentas mejorarla?", value=d["worsen"],
                                         placeholder="Ej. el costo de transporte")
            st.info(f"Mejorar {d['improve'] or '[característica]'} empeora {d['worsen'] or '[otra característica]'}.")
        nav_row(idx, len(TRIZ_LABELS), "triz", ("triz", "step"))
    elif idx == 2:
        _render_triz_principles(d)
        nav_row(idx, len(TRIZ_LABELS), "triz", ("triz", "step"))
    else:
        _render_triz_summary(d)


def _render_triz_ai_suggestions(d):
    store = st.session_state.setdefault("ai_suggestions", {})
    key = "triz_ai"
    c1, c2 = st.columns([3, 1])
    with c1:
        clicked = st.button("✨ Sugerir principios relevantes con IA", key=f"{key}_btn", use_container_width=True)
    with c2:
        if store.get(key):
            if st.button("Descartar", key=f"{key}_dismiss", use_container_width=True):
                store.pop(key, None)
                st.rerun()

    if clicked:
        if not has_api_key():
            store[key] = {"status": "unavailable"}
        else:
            with st.spinner("Analizando tu contradicción…"):
                store[key] = ask_triz_suggestions(d.get("improve", ""), d.get("worsen", ""))
        st.rerun()

    result = store.get(key)
    if not result:
        return
    if result.get("status") == "unavailable":
        st.caption("Agrega tu API key de Anthropic en la barra lateral para usar sugerencias con IA.")
    elif result.get("status") == "error":
        st.warning(result.get("error") or "Algo salió mal generando sugerencias.")
    elif result.get("status") == "done":
        principle_names = {n: name for n, name, _ in TRIZ_PRINCIPLES}
        with st.container(border=True):
            st.caption("La IA sugiere revisar estos principios para tu contradicción:")
            for s in result["suggestions"]:
                n = s["n"]
                already = d["selected"].get(str(n), {}).get("selected", False)
                ic1, ic2 = st.columns([10, 1])
                ic1.markdown(f"**#{n} — {principle_names.get(n, '')}**  \n{s['why']}")
                if already:
                    ic2.markdown("✓")
                elif ic2.button("+", key=f"{key}_add_{n}"):
                    sel = d["selected"].setdefault(str(n), {"selected": False, "note": ""})
                    sel["selected"] = True
                    st.rerun()
            st.caption("Al agregar uno se marca como seleccionado abajo — búscalo por número o palabra clave para anotar cómo aplicarlo.")


def _render_triz_principles(d):
    with st.container(border=True):
        st.markdown("#### Los 40 principios de inventiva")
        st.caption("Busca y selecciona los que podrían aplicar a tu contradicción; anota cómo lo harías.")
        _render_triz_ai_suggestions(d)
        query = st.text_input("Buscar por palabra clave", placeholder="ej. dividir, flexible, temperatura...",
                               label_visibility="collapsed", key="triz_search")
        q = query.strip().lower()
        cols = st.columns(2)
        i = 0
        for n, name, desc in TRIZ_PRINCIPLES:
            haystack = f"{name} {desc}".lower()
            if q and q not in haystack:
                continue
            sel_dict = d["selected"].setdefault(str(n), {"selected": False, "note": ""})
            with cols[i % 2]:
                with st.container(border=True):
                    st.markdown(f"**#{n} — {name}**")
                    st.caption(desc)
                    checked = st.checkbox("Seleccionar", value=sel_dict["selected"], key=f"triz_sel_{n}")
                    sel_dict["selected"] = checked
                    if checked:
                        sel_dict["note"] = st.text_area("¿Cómo aplicarías esto a tu problema?",
                                                         value=sel_dict["note"], key=f"triz_note_{n}", height=68)
            i += 1
        if i == 0:
            st.caption("Ningún principio coincide con tu búsqueda.")


def _render_triz_summary(d):
    st.markdown("### Resumen TRIZ")
    st.info(f"Mejorar {d['improve'] or '[característica]'} empeora {d['worsen'] or '[otra característica]'}.")
    any_sel = False
    for n, name, desc in TRIZ_PRINCIPLES:
        sel = d["selected"].get(str(n))
        if sel and sel.get("selected"):
            any_sel = True
            with st.expander(f"#{n} — {name}", expanded=True):
                st.write(sel.get("note") or "(sin nota de aplicación)")
    if not any_sel:
        st.caption("Aún no seleccionas principios.")
    render_export_button("triz")


# ============================================================
# Foresight · Previsión Estratégica
# ============================================================

def render_foresight():
    m = method_by_id("foresight")
    d = st.session_state.data["foresight"]
    method_header(m)
    render_change_method_button()

    if not d["sub_mode"]:
        st.caption("Elige cómo quieres anticipar el futuro de tu reto:")
        cols = st.columns(3)
        for c, fm in zip(cols, FORESIGHT_MODES):
            with c:
                with st.container(border=True):
                    st.markdown(f"**{fm['name']}**")
                    st.caption(fm["desc"])
                    if st.button("Elegir", key=f"foresight_mode_{fm['id']}", use_container_width=True):
                        d["sub_mode"] = fm["id"]
                        st.rerun()
        return

    if st.button("← Elegir otro enfoque", key="foresight_change_mode"):
        d["sub_mode"] = None
        st.rerun()

    if d["sub_mode"] == "scenarios":
        _render_foresight_scenarios(d)
    elif d["sub_mode"] == "backcasting":
        _render_foresight_backcasting(d)
    elif d["sub_mode"] == "pestel":
        _render_foresight_pestel(d)


def _render_foresight_scenarios(d):
    sc = d["scenarios"]
    idx = sc["step"]
    step_tabs(FORESIGHT_SCENARIOS_LABELS, idx, "fs_sc", ("foresight", "scenarios", "step"))

    if idx >= len(FORESIGHT_SCENARIOS_LABELS):
        _render_foresight_scenarios_summary(sc)
        return

    with st.container(border=True):
        if idx == 0:
            st.markdown("#### Señales y tendencias")
            st.caption("¿Qué cambios, señales débiles o tendencias ya están ocurriendo alrededor de tu reto? "
                       "No filtres todavía: incluye lo obvio y lo que apenas empieza a notarse.")
            list_capture(sc["signals"], "fs_signals", "Una señal, tendencia o cambio que estás notando...",
                         ai_label="Foresight — Señales y tendencias: cambios o señales débiles ya ocurriendo alrededor de este reto")
        elif idx == 1:
            st.markdown("#### Fuerzas motrices")
            st.caption("De esas señales, ¿cuáles son las 2-3 fuerzas más importantes **e inciertas** — las que "
                       "podrían cambiar el rumbo de tu reto según cómo evolucionen?")
            list_capture(sc["drivers"], "fs_drivers", "Una fuerza incierta e importante (ej. adopción de IA, regulación, clima)...",
                         ai_label="Foresight — Fuerzas motrices: fuerzas inciertas e importantes que podrían cambiar el rumbo de este reto")
        elif idx == 2:
            st.markdown("#### Construye 2-4 escenarios futuros")
            st.caption("Combina tus fuerzas motrices en futuros distintos y plausibles. Sugerencia: uno optimista, "
                       "uno pesimista, uno de continuidad y un \"wildcard\" inesperado.")
            for i, scen in enumerate(sc["scenario_list"]):
                st.markdown(f"**Escenario {i + 1}**")
                c1, c2 = st.columns([1, 2])
                with c1:
                    scen["name"] = st.text_input("Nombre corto", value=scen["name"], key=f"fs_scen_name_{i}",
                                                  placeholder="Ej. \"Todo se automatiza\"", label_visibility="collapsed")
                with c2:
                    scen["desc"] = st.text_area("Cómo se ve este futuro", value=scen["desc"], key=f"fs_scen_desc_{i}",
                                                 placeholder="Describe cómo se vería tu reto en este futuro...",
                                                 height=68, label_visibility="collapsed")
            if len(sc["scenario_list"]) < 4:
                if st.button("+ Agregar otro escenario", key="fs_add_scenario"):
                    sc["scenario_list"].append({"name": "", "desc": ""})
                    st.rerun()
        elif idx == 3:
            st.markdown("#### Implicaciones y acciones")
            st.caption("Mirando tus escenarios: ¿qué deberías empezar a hacer, dejar de hacer, o vigilar de cerca "
                       "desde ya, sin importar cuál futuro ocurra?")
            list_capture(sc["implications"], "fs_implications", "Una implicación o acción a partir de tus escenarios...",
                         ai_label="Foresight — Implicaciones: acciones a tomar o vigilar hoy, sin importar cuál escenario futuro ocurra")

    nav_row(idx, len(FORESIGHT_SCENARIOS_LABELS), "fs_sc", ("foresight", "scenarios", "step"))


def _render_foresight_scenarios_summary(sc):
    st.markdown("### Resumen — Tendencias + Escenarios")
    with st.expander(f"Señales ({len(sc['signals'])})", expanded=True):
        for it in sc["signals"]:
            st.markdown(f"- {it}")
        if not sc["signals"]:
            st.caption("Sin registros.")
    with st.expander(f"Fuerzas motrices ({len(sc['drivers'])})", expanded=True):
        for it in sc["drivers"]:
            st.markdown(f"- {it}")
        if not sc["drivers"]:
            st.caption("Sin registros.")
    with st.expander("Escenarios", expanded=True):
        any_scen = False
        for i, scen in enumerate(sc["scenario_list"]):
            if scen["name"] or scen["desc"]:
                any_scen = True
                st.markdown(f"**{scen['name'] or f'Escenario {i + 1}'}**  \n{scen['desc']}")
        if not any_scen:
            st.caption("Sin escenarios definidos.")
    with st.expander(f"Implicaciones ({len(sc['implications'])})", expanded=True):
        for it in sc["implications"]:
            st.markdown(f"- {it}")
        if not sc["implications"]:
            st.caption("Sin registros.")
    render_export_button("foresight")


def _render_foresight_backcasting(d):
    bc = d["backcasting"]
    idx = bc["step"]
    step_tabs(FORESIGHT_BACKCAST_LABELS, idx, "fs_bc", ("foresight", "backcasting", "step"))

    if idx >= len(FORESIGHT_BACKCAST_LABELS):
        _render_foresight_backcasting_summary(bc)
        return

    with st.container(border=True):
        if idx == 0:
            st.markdown("#### Futuro deseado")
            bc["horizon"] = st.text_input("¿A cuántos años/meses te proyectas?", value=bc["horizon"],
                                           placeholder="Ej. 3 años")
            st.caption("Describe ese futuro como si ya hubiera pasado y funcionara. Sé específico.")
            bc["vision"] = st.text_area("El futuro ideal ya logrado", value=bc["vision"], height=100,
                                         placeholder="Ej. Nuestra barra de café tiene fila los fines de semana porque...")
        elif idx == 1:
            st.markdown("#### Hitos intermedios")
            st.caption("Trabajando hacia atrás desde ese futuro: ¿qué tuvo que existir o suceder antes de llegar ahí?")
            list_capture(bc["milestones"], "fs_milestones", "Un hito intermedio necesario antes de llegar al futuro deseado...",
                         ai_label=f"Backcasting — Hitos: hitos intermedios necesarios para llegar al futuro deseado ({bc.get('vision', '')[:200]})")
        elif idx == 2:
            st.markdown("#### Obstáculos")
            st.caption("¿Qué podría bloquear o frenar el camino hacia ese futuro?")
            list_capture(bc["obstacles"], "fs_obstacles", "Un obstáculo o riesgo en el camino...",
                         ai_label="Backcasting — Obstáculos: posibles bloqueos o riesgos en el camino hacia el futuro deseado")
        elif idx == 3:
            st.markdown("#### Acciones desde ahora")
            st.caption("¿Qué puedes hacer hoy o esta semana para empezar a moverte hacia ese futuro?")
            list_capture(bc["actions"], "fs_actions", "Una acción concreta para empezar ahora...",
                         ai_label="Backcasting — Acciones ahora: acciones concretas para empezar a moverse hacia el futuro deseado desde hoy")

    nav_row(idx, len(FORESIGHT_BACKCAST_LABELS), "fs_bc", ("foresight", "backcasting", "step"))


def _render_foresight_backcasting_summary(bc):
    st.markdown("### Resumen — Backcasting")
    with st.expander("Futuro deseado", expanded=True):
        st.caption(f"Horizonte: {bc['horizon'] or '(sin definir)'}")
        st.write(bc["vision"] or "Sin definir.")
    with st.expander(f"Hitos ({len(bc['milestones'])})", expanded=True):
        for it in bc["milestones"]:
            st.markdown(f"- {it}")
        if not bc["milestones"]:
            st.caption("Sin registros.")
    with st.expander(f"Obstáculos ({len(bc['obstacles'])})"):
        for it in bc["obstacles"]:
            st.markdown(f"- {it}")
        if not bc["obstacles"]:
            st.caption("Sin registros.")
    with st.expander(f"Acciones ({len(bc['actions'])})", expanded=True):
        for it in bc["actions"]:
            st.markdown(f"- {it}")
        if not bc["actions"]:
            st.caption("Sin registros.")
    render_export_button("foresight")


def _render_foresight_pestel(d):
    pestel = d["pestel"]
    idx = pestel["step"]
    labels = [c["name"] for c in PESTEL_CATEGORIES]
    step_tabs(labels, idx, "fs_pestel", ("foresight", "pestel", "step"))

    if idx < len(PESTEL_CATEGORIES):
        cat = PESTEL_CATEGORIES[idx]
        with st.container(border=True):
            st.markdown(
                f'<span style="display:inline-block;width:14px;height:14px;border-radius:50%;'
                f'background:{cat["color"]};margin-right:8px;"></span>'
                f'**{cat["name"]}**',
                unsafe_allow_html=True,
            )
            for p in cat["prompts"]:
                st.markdown(f"— {p}")
            list_capture(pestel["categories"][cat["key"]], f"fs_pestel_{cat['key']}",
                         f'Un factor {cat["name"].lower()} relevante para tu reto...',
                         ai_label=f"PESTEL — {cat['name']}: {' '.join(cat['prompts'])}")
        nav_row(idx, len(PESTEL_CATEGORIES), "fs_pestel", ("foresight", "pestel", "step"))
    else:
        _render_foresight_pestel_summary(pestel)


def _render_foresight_pestel_summary(pestel):
    st.markdown("### Resumen — PESTEL")
    for cat in PESTEL_CATEGORIES:
        items = pestel["categories"][cat["key"]]
        with st.expander(f"{cat['name']} ({len(items)})", expanded=bool(items)):
            for it in items:
                st.markdown(f"- {it}")
            if not items:
                st.caption("Sin registros.")
    render_export_button("foresight")


# ============================================================
# Router
# ============================================================

METHOD_RENDERERS = {
    "scamper": render_scamper,
    "design-thinking": render_design_thinking,
    "double-diamond": render_double_diamond,
    "cps": render_cps,
    "six-hats": render_six_hats,
    "brainstorming": render_brainstorming,
    "triz": render_triz,
    "foresight": render_foresight,
}
