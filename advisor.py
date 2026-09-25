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


def _parse_json_loose(text, bracket_pattern):
    """Extrae y parsea JSON de la respuesta del modelo, tolerando los dos problemas más comunes:
    texto extra alrededor (saludos, ```json ... ```) y caracteres de control sin escapar (saltos de
    línea reales dentro de un string) que json.loads normal rechaza con "Unterminated string"."""
    match = re.search(bracket_pattern, text, re.DOTALL)
    candidate = match.group(0) if match else text
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass
    # strict=False permite caracteres de control literales (\n, \t) dentro de strings JSON,
    # que es la causa más común de "Unterminated string" cuando el modelo no escapa saltos de línea.
    return json.loads(candidate, strict=False)


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

    valid_ids = {m["id"] for m in METHODS}
    text = None
    try:
        client = anthropic.Anthropic(api_key=api_key)
        model_id = st.session_state.get("model_id") or "claude-haiku-4-5"
        resp = client.messages.create(
            model=model_id,
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in resp.content if hasattr(block, "text"))
        payload = _parse_json_loose(text, r"\{.*\}")
        if payload.get("id") in valid_ids:
            return {"status": "done", "id": payload["id"], "reason": payload.get("reason", "")}
        return {"status": "error", "error": "No obtuvimos una recomendación válida. Intenta con más detalle."}
    except json.JSONDecodeError:
        # Último recurso: el JSON venía mal formado (comillas o saltos de línea sin escapar
        # dentro de "reason"). Sacamos "id" y "reason" directamente con regex en vez de fallar.
        id_match = re.search(r'"id"\s*:\s*"([^"]+)"', text or "")
        reason_match = re.search(r'"reason"\s*:\s*"(.*?)"\s*[,}]', text or "", re.DOTALL)
        if id_match and id_match.group(1) in valid_ids:
            return {"status": "done", "id": id_match.group(1), "reason": reason_match.group(1) if reason_match else ""}
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

    text = None
    try:
        client = anthropic.Anthropic(api_key=api_key)
        model_id = st.session_state.get("model_id") or "claude-haiku-4-5"
        resp = client.messages.create(
            model=model_id,
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in resp.content if hasattr(block, "text"))
        raw_ideas = _parse_json_loose(text, r"\[.*\]")
    except json.JSONDecodeError:
        # Último recurso: sacamos cada string entre comillas directamente, sin depender de que
        # el arreglo JSON completo sea válido (por ejemplo si una idea trae un salto de línea real).
        raw_ideas = re.findall(r'"((?:[^"\\]|\\.)*)"', text or "", re.DOTALL)
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": _friendly_error(exc)}

    ideas = [str(i).strip() for i in raw_ideas if str(i).strip()][:n]
    if not ideas:
        return {"status": "error", "error": "No se generaron sugerencias válidas. Intenta de nuevo."}
    return {"status": "done", "ideas": ideas}


def _sanitize_svg(svg):
    """Limpieza defensiva antes de renderizar un SVG generado por el modelo con
    unsafe_allow_html=True: quita <script>, manejadores de eventos on*=... y URIs
    javascript:, que no deberían aparecer en un wireframe pero no cuesta nada filtrar."""
    svg = re.sub(r"<script[\s\S]*?</script>", "", svg, flags=re.IGNORECASE)
    svg = re.sub(r'\son\w+\s*=\s*"[^"]*"', "", svg, flags=re.IGNORECASE)
    svg = re.sub(r"\son\w+\s*=\s*'[^']*'", "", svg, flags=re.IGNORECASE)
    svg = re.sub(r"javascript:", "", svg, flags=re.IGNORECASE)
    return svg


def ask_prototype_sketch(description, problem):
    """Genera un boceto/wireframe simple en SVG a partir de la descripción de un prototipo
    (paso Prototipar de Design Thinking). Devuelve {"status": ..., "svg"?, "error"?}."""
    api_key = _get_api_key()
    if not api_key:
        return {"status": "unavailable"}
    if not (description or "").strip():
        return {"status": "error", "error": "Escribe primero una descripción del prototipo."}
    try:
        import anthropic
    except ImportError:
        return {"status": "error", "error": "Falta instalar el paquete 'anthropic' (pip install anthropic)."}

    prompt = (
        "Eres un diseñador UX que dibuja bocetos rápidos (wireframes) en SVG puro para comunicar una idea "
        "— no un diseño final ni pulido.\n\n"
        f'Reto: "{(problem or "").replace(chr(34), chr(39))}"\n'
        f'Prototipo a bocetar: "{description.replace(chr(34), chr(39))}"\n\n'
        "Dibuja un wireframe simple y claro que represente esta pantalla, objeto o concepto: usa solo formas "
        "básicas (rect, line, circle, path, text), trazos delgados en gris oscuro (#4B4B63) sobre fondo blanco, "
        "estilo boceto/wireframe de baja fidelidad (NO uses colores vistosos ni gradientes ni sombras). "
        'Usa viewBox="0 0 480 340" y width="100%" height="100%". Etiqueta las partes clave con texto corto '
        "dentro del SVG (font-size 11-13, font-family sans-serif).\n\n"
        "Responde ÚNICAMENTE con el código SVG completo, empezando en <svg y terminando en </svg>. "
        "Sin explicación, sin markdown, sin backticks, sin texto antes o después."
    )
    try:
        client = anthropic.Anthropic(api_key=api_key)
        model_id = st.session_state.get("model_id") or "claude-haiku-4-5"
        resp = client.messages.create(model=model_id, max_tokens=1500, messages=[{"role": "user", "content": prompt}])
        text = "".join(block.text for block in resp.content if hasattr(block, "text"))
        match = re.search(r"<svg[\s\S]*?</svg>", text, re.IGNORECASE)
        if not match:
            return {"status": "error", "error": "La IA no devolvió un boceto válido. Intenta de nuevo."}
        return {"status": "done", "svg": _sanitize_svg(match.group(0))}
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
    valid_ns = {n_ for n_, _, _ in TRIZ_PRINCIPLES}
    text = None
    try:
        client = anthropic.Anthropic(api_key=api_key)
        model_id = st.session_state.get("model_id") or "claude-haiku-4-5"
        resp = client.messages.create(model=model_id, max_tokens=700, messages=[{"role": "user", "content": prompt}])
        text = "".join(block.text for block in resp.content if hasattr(block, "text"))
        raw = _parse_json_loose(text, r"\[.*\]")
        suggestions = [{"n": int(it["n"]), "why": str(it.get("why", ""))} for it in raw if int(it.get("n", -1)) in valid_ns]
    except json.JSONDecodeError:
        # Último recurso: sacamos cada par número+motivo con regex, objeto por objeto.
        suggestions = []
        for chunk in re.findall(r"\{[^{}]*\}", text or "", re.DOTALL):
            n_match = re.search(r'"n"\s*:\s*(\d+)', chunk)
            why_match = re.search(r'"why"\s*:\s*"(.*?)"\s*[,}]?\s*$', chunk, re.DOTALL)
            if n_match and int(n_match.group(1)) in valid_ns:
                suggestions.append({"n": int(n_match.group(1)), "why": why_match.group(1) if why_match else ""})
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": _friendly_error(exc)}

    if not suggestions:
        return {"status": "error", "error": "No se generaron sugerencias válidas. Intenta de nuevo."}
    return {"status": "done", "suggestions": suggestions[:n]}
