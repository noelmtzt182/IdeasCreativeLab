"""Asistente de IA que recomienda un método/técnica usando la API de Anthropic.

Requiere que el usuario proporcione su propia API key de Anthropic (barra lateral,
o variable de entorno / st.secrets con el nombre ANTHROPIC_API_KEY).
"""
import json
import re

import streamlit as st

from data import METHODS, TRIZ_PRINCIPLES


def _get_api_key():
    if st.session_state.get("api_key"):
        return st.session_state["api_key"]
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
    import os
    return os.environ.get("ANTHROPIC_API_KEY")


def has_api_key():
    """True si hay una API key disponible por cualquier vía (barra lateral, secreto o env var)."""
    return bool(_get_api_key())


def _friendly_error(exc):
    msg = str(exc).lower()
    if "401" in msg or "auth" in msg:
        return "Tu API key no parece válida o no tiene acceso. Revísala en la barra lateral."
    if "429" in msg or "rate" in msg:
        return "Se alcanzó el límite de solicitudes a la API. Intenta de nuevo en un momento."
    if "model" in msg and ("not_found" in msg or "invalid" in msg):
        return ("El modelo configurado no existe o ya no está disponible. Revisa el nombre del "
                "modelo en la barra lateral (ver docs.claude.com/en/docs/about-claude/models).")
    return f"Algo salió mal al consultar al asistente: {exc}"


def ask_advisor(user_text):
    """Devuelve un dict: {status: 'unavailable'|'error'|'done', id?, reason?, error?}."""
    api_key = _get_api_key()
    if not api_key:
        return {"status": "unavailable"}

    try:
        import anthropic
    except ImportError:
        return {"status": "error", "error": "Falta instalar el paquete 'anthropic' (pip install anthropic)."}

    context = "\n".join(
        f'- id:"{m["id"]}" ({m["name"]}): {m["tagline"]} Ideal para: {m["best_for"]}'
        for m in METHODS
    )
    prompt = (
        "Eres un asesor experto en metodologías de creatividad e innovación dentro de la app "
        '"Taller de Ideas". Estos son los ÚNICOS métodos y técnicas disponibles '
        '(usa siempre el "id" exacto entre comillas):\n' + context +
        '\n\nUn usuario describe su situación:\n"' + user_text.replace('"', "'") + '"\n\n'
        "Elige el id de UN solo método o técnica de la lista que mejor se ajuste. "
        'Responde SOLO con JSON válido de la forma {"id":"...","reason":"..."}, donde "reason" '
        "son 2-3 frases en español, tono cercano, explicando por qué ese es el mejor ajuste."
    )

    try:
        client = anthropic.Anthropic(api_key=api_key)
        model_id = st.session_state.get("model_id") or "claude-haiku-4-5"
        resp = client.messages.create(
            model=model_id,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in resp.content if hasattr(block, "text"))
        match = re.search(r"\{.*\}", text, re.DOTALL)
        payload = json.loads(match.group(0)) if match else json.loads(text)
        valid_ids = {m["id"] for m in METHODS}
        if payload.get("id") in valid_ids:
            return {"status": "done", "id": payload["id"], "reason": payload.get("reason", "")}
        return {"status": "error", "error": "No obtuvimos una recomendación válida. Intenta con más detalle."}
    except Exception as exc:  # noqa: BLE001 - queremos capturar cualquier falla de red/API y mostrarla amable
        return {"status": "error", "error": _friendly_error(exc)}


def ask_idea_suggestions(label, existing_items, n=5):
    """Genera sugerencias (ideas, preguntas, factores, etc. según el contexto) para un paso
    específico de un método. Devuelve {"status": "unavailable"|"error"|"done", "ideas"?, "error"?}."""
    api_key = _get_api_key()
    if not api_key:
        return {"status": "unavailable"}

    try:
        import anthropic
    except ImportError:
        return {"status": "error", "error": "Falta instalar el paquete 'anthropic' (pip install anthropic)."}

    problem = st.session_state.get("problem", "") or "(el usuario no describió su reto todavía)"
    existing_text = "\n".join(f"- {it}" for it in existing_items[-15:]) if existing_items else "(ninguna todavía)"

    prompt = (
        "Eres un facilitador experto en creatividad e innovación dentro de la app \"Taller de Ideas\". "
        f'Un usuario está trabajando en este reto: "{problem.replace(chr(34), chr(39))}"\n\n'
        f"Está en este paso específico: {label}\n\n"
        f"Esto es lo que ya tiene registrado en este paso (no lo repitas):\n{existing_text}\n\n"
        f"Genera {n} sugerencias NUEVAS, concretas y variadas entre sí para este paso — cortas "
        "(una frase cada una), en español, sin numerarlas ni explicarlas. "
        'Responde SOLO con JSON válido: una lista de strings, como ["sugerencia 1", "sugerencia 2", ...].'
    )

    try:
        client = anthropic.Anthropic(api_key=api_key)
        model_id = st.session_state.get("model_id") or "claude-haiku-4-5"
        resp = client.messages.create(
            model=model_id,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in resp.content if hasattr(block, "text"))
        match = re.search(r"\[.*\]", text, re.DOTALL)
        ideas = json.loads(match.group(0)) if match else json.loads(text)
        ideas = [str(i).strip() for i in ideas if str(i).strip()][:n]
        if not ideas:
            return {"status": "error", "error": "No se generaron sugerencias válidas. Intenta de nuevo."}
        return {"status": "done", "ideas": ideas}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": _friendly_error(exc)}


def ask_triz_suggestions(improve, worsen, n=5):
    """Sugiere cuáles de los 40 principios TRIZ podrían aplicar a una contradicción dada.
    Devuelve {"status": ..., "suggestions": [{"n": int, "why": str}, ...]}."""
    api_key = _get_api_key()
    if not api_key:
        return {"status": "unavailable"}
    try:
        import anthropic
    except ImportError:
        return {"status": "error", "error": "Falta instalar el paquete 'anthropic' (pip install anthropic)."}

    principles_list = "\n".join(f"{n_}. {name}" for n_, name, _ in TRIZ_PRINCIPLES)
    prompt = (
        "Eres un experto en TRIZ. Un usuario definió esta contradicción técnica:\n"
        f'Quiere mejorar: "{(improve or "(sin definir)").replace(chr(34), chr(39))}"\n'
        f'Pero empeora: "{(worsen or "(sin definir)").replace(chr(34), chr(39))}"\n\n'
        f"Estos son los 40 principios de inventiva de TRIZ (número y nombre):\n{principles_list}\n\n"
        f"Elige los {n} principios que más probablemente ayuden a resolver esta contradicción. "
        'Responde SOLO con JSON válido: una lista de objetos como '
        '[{"n": 1, "why": "por qué aplicaría, en una frase"}, ...], usando el número exacto de la lista.'
    )
    try:
        client = anthropic.Anthropic(api_key=api_key)
        model_id = st.session_state.get("model_id") or "claude-haiku-4-5"
        resp = client.messages.create(model=model_id, max_tokens=600, messages=[{"role": "user", "content": prompt}])
        text = "".join(block.text for block in resp.content if hasattr(block, "text"))
        match = re.search(r"\[.*\]", text, re.DOTALL)
        raw = json.loads(match.group(0)) if match else json.loads(text)
        valid_ns = {n_ for n_, _, _ in TRIZ_PRINCIPLES}
        suggestions = [{"n": int(it["n"]), "why": str(it.get("why", ""))} for it in raw if int(it.get("n", -1)) in valid_ns]
        if not suggestions:
            return {"status": "error", "error": "No se generaron sugerencias válidas. Intenta de nuevo."}
        return {"status": "done", "suggestions": suggestions[:n]}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": _friendly_error(exc)}
