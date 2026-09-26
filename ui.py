"""Widgets reutilizables de Streamlit para todas las vistas de método."""
import time

import streamlit as st


def badge(text, color, text_on="white", size=40):
    ink = "#FFFFFF" if text_on == "white" else "#1B1B2F"
    st.markdown(
        f'<span style="display:inline-flex;align-items:center;justify-content:center;'
        f'width:{size}px;height:{size}px;border-radius:12px;background:{color};color:{ink};'
        f'font-family:\'Fredoka\',sans-serif;font-weight:600;font-size:{max(11, size // 3)}px;'
        f'box-shadow:0 3px 8px {color}55;">{text}</span>',
        unsafe_allow_html=True,
    )


def method_header(m):
    cols = st.columns([1, 9])
    with cols[0]:
        badge(m["code"], m["color"], m.get("text_on", "white"), size=48)
    with cols[1]:
        st.markdown(f"### {m['name']}")
        st.caption(m["tagline"])


def _set_step(step_state_key, value):
    """step_state_key: tupla de claves anidadas dentro de st.session_state.data,
    p.ej. ("scamper", "step") o ("foresight", "scenarios", "step")."""
    obj = st.session_state.data
    for k in step_state_key[:-1]:
        obj = obj[k]
    obj[step_state_key[-1]] = value


def step_tabs(labels, current_index, key_prefix, step_state_key, include_summary=True):
    all_labels = list(labels) + (["Resumen"] if include_summary else [])
    total = len(all_labels)
    cols = st.columns(total)
    for i, lbl in enumerate(all_labels):
        prefix = "✓ " if i < current_index else ""
        kind = "primary" if i == current_index else "secondary"
        if cols[i].button(prefix + lbl, key=f"{key_prefix}_tab_{i}", use_container_width=True, type=kind):
            _set_step(step_state_key, i)
            st.rerun()
    denom = total - 1 if total > 1 else 1
    st.progress(min(1.0, current_index / denom))


def nav_row(current_index, total_steps, key_prefix, step_state_key):
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Anterior", key=f"{key_prefix}_prev", disabled=current_index <= 0):
            _set_step(step_state_key, max(0, current_index - 1))
            st.rerun()
    with c2:
        label = "Ver resumen →" if current_index >= total_steps - 1 else "Siguiente →"
        if st.button(label, key=f"{key_prefix}_next", type="primary", use_container_width=True):
            _set_step(step_state_key, min(total_steps, current_index + 1))
            st.rerun()


def list_capture(items, key_prefix, placeholder, starable=False, ai_label=None):
    """items: lista mutable de strings, o de dicts {"text":..,"starred":..} si starable=True.
    ai_label: si se da, describe el paso actual para la IA (ej. "SCAMPER — Sustituir") y
    activa el botón "Sugerir con IA" que propone ideas nuevas para este paso específico."""
    for i, item in enumerate(items):
        text = item["text"] if starable else item
        cols = st.columns([1, 10, 1]) if starable else st.columns([11, 1])
        if starable:
            star_label = "★" if item.get("starred") else "☆"
            if cols[0].button(star_label, key=f"{key_prefix}_star_{i}"):
                item["starred"] = not item.get("starred")
                st.rerun()
            cols[1].markdown(text)
            del_col = cols[2]
        else:
            cols[0].markdown(f"- {text}")
            del_col = cols[1]
        if del_col.button("✕", key=f"{key_prefix}_del_{i}"):
            items.pop(i)
            st.rerun()
    if items:
        st.caption(f"{len(items)} idea{'s' if len(items) != 1 else ''}")
    else:
        st.caption("Todavía no hay ideas aquí. Escribe una y presiona Agregar.")
    with st.form(key=f"{key_prefix}_form", clear_on_submit=True):
        new_text = st.text_area("Nueva idea", placeholder=placeholder, label_visibility="collapsed",
                                 key=f"{key_prefix}_input", height=70)
        submitted = st.form_submit_button("Agregar")
        if submitted and new_text.strip():
            if starable:
                items.append({"text": new_text.strip(), "starred": False})
            else:
                items.append(new_text.strip())
            st.rerun()

    if ai_label:
        _render_ai_suggestions(items, key_prefix, ai_label, starable)


def _render_ai_suggestions(items, key_prefix, ai_label, starable):
    from advisor import ask_idea_suggestions, has_api_key

    store = st.session_state.setdefault("ai_suggestions", {})
    current_texts = {(it["text"] if starable else it) for it in items}

    c1, c2 = st.columns([3, 1])
    with c1:
        clicked = st.button("✨ Sugerir con IA", key=f"{key_prefix}_ai_btn", use_container_width=True)
    with c2:
        if store.get(key_prefix):
            if st.button("Descartar", key=f"{key_prefix}_ai_dismiss", use_container_width=True):
                store.pop(key_prefix, None)
                st.rerun()

    if clicked:
        if not has_api_key():
            store[key_prefix] = {"status": "unavailable"}
        else:
            with st.spinner("Generando sugerencias…"):
                existing = [it["text"] if starable else it for it in items]
                result = ask_idea_suggestions(ai_label, existing)
            store[key_prefix] = result
        st.rerun()

    result = store.get(key_prefix)
    if not result:
        return
    if result.get("status") == "unavailable":
        st.caption("Agrega tu API key de Anthropic en la barra lateral para usar sugerencias con IA.")
    elif result.get("status") == "error":
        st.warning(result.get("error") or "Algo salió mal generando sugerencias.")
    elif result.get("status") == "done":
        with st.container(border=True):
            st.caption("Sugerencias de la IA — agrega las que te sirvan:")
            remaining = []
            for i, idea in enumerate(result["ideas"]):
                if idea in current_texts:
                    continue
                ic1, ic2 = st.columns([10, 1])
                ic1.markdown(f"— {idea}")
                if ic2.button("+", key=f"{key_prefix}_ai_add_{i}"):
                    if starable:
                        items.append({"text": idea, "starred": False})
                    else:
                        items.append(idea)
                    result["ideas"].remove(idea)
                    st.rerun()
                remaining.append(idea)
            if not remaining:
                st.caption("Ya agregaste todas. Presiona \"Sugerir con IA\" de nuevo para más.")


def timer_widget(context_key, timer_key_prefix):
    timers = st.session_state.timers
    t = timers.setdefault(context_key, {"start": None, "duration": 300, "running": False})
    remaining = t["duration"]
    if t["running"] and t["start"]:
        elapsed = time.time() - t["start"]
        remaining = max(0, t["duration"] - elapsed)
        if remaining <= 0:
            t["running"] = False
            remaining = 0
    mm, ss = divmod(int(remaining), 60)

    cols = st.columns([2, 1, 1, 1, 2])
    cols[0].markdown(f"## `{mm:02d}:{ss:02d}`")
    for i, secs in enumerate([180, 300, 600]):
        if cols[i + 1].button(f"{secs // 60} min", key=f"{timer_key_prefix}_preset_{secs}"):
            t["duration"] = secs
            t["start"] = None
            t["running"] = False
            st.rerun()
    with cols[4]:
        if not t["running"]:
            if st.button("▶ Iniciar", key=f"{timer_key_prefix}_start"):
                t["start"] = time.time()
                t["running"] = True
                st.rerun()
        else:
            if st.button("❚❚ Pausar", key=f"{timer_key_prefix}_pause"):
                t["duration"] = remaining
                t["running"] = False
                t["start"] = None
                st.rerun()
    if t["running"]:
        st.caption("El cronómetro corre con el reloj real: cualquier clic en la página actualiza el número mostrado.")
