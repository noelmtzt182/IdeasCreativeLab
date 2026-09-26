"""Genera el texto Markdown exportable de una sesión."""
import datetime
import re
from data import SCAMPER_STEPS, SIX_HATS, TRIZ_PRINCIPLES, PESTEL_CATEGORIES, method_by_id


def _list_or_dash(items, map_fn=None):
    if not items:
        return "_Sin ideas registradas._"
    return "\n".join("- " + (map_fn(it) if map_fn else it) for it in items)


def build_export_text(problem, method, data):
    m = method_by_id(method)
    lines = [
        f"# Taller de Ideas — {m['name'] if m else 'Sesión'}",
        "",
        f"**Problema:** {problem or '(sin definir)'}",
        f"**Fecha:** {datetime.date.today().strftime('%d de %B de %Y')}",
        "",
    ]

    if method == "scamper":
        sc = data["scamper"]
        for st_ in SCAMPER_STEPS:
            lines.append(f"## {st_['key']} — {st_['title']}")
            lines.append(_list_or_dash(sc[st_["key"]]))
            lines.append("")

    elif method == "design-thinking":
        dt = data["design_thinking"]
        lines.append("## Empatizar")
        lines.append(_list_or_dash(dt["empathize"]))
        lines.append("")
        lines.append("## Definir")
        de = dt["define"]
        if de["user"] or de["need"] or de["insight"]:
            lines.append(f"{de['user'] or '(usuario)'} necesita {de['need'] or '(necesidad)'} porque {de['insight'] or '(insight)'}.")
        else:
            lines.append("_Sin definir._")
        lines.append("")
        lines.append("## Idear")
        lines.append(_list_or_dash(dt["ideate"]))
        lines.append("")
        lines.append("## Prototipar")
        lines.append(dt["prototype"]["description"] or "_Sin descripción._")
        lines.append(_list_or_dash(dt["prototype"]["questions"]))
        lines.append("")
        lines.append("## Testear")
        lines.append("**Qué funcionó:**")
        lines.append(_list_or_dash(dt["test"]["worked"]))
        lines.append("**Qué no funcionó:**")
        lines.append(_list_or_dash(dt["test"]["didnt_work"]))
        lines.append("**Ajustes / nuevas ideas:**")
        lines.append(_list_or_dash(dt["test"]["adjustments"]))

    elif method == "double-diamond":
        dd = data["double_diamond"]
        lines.append("## Descubrir")
        lines.append(_list_or_dash(dd["discover"]))
        lines.append("")
        lines.append("## Definir")
        lines.append(f"**Declaración del problema:** {dd['problem_statement'] or '(sin definir)'}")
        lines.append("**Criterios de éxito:**")
        lines.append(_list_or_dash(dd["success_criteria"]))
        lines.append("")
        lines.append("## Desarrollar")
        lines.append(_list_or_dash(dd["develop"]))
        lines.append("")
        lines.append("## Entregar")
        lines.append(f"**Solución elegida:** {dd['chosen_solution'] or '(sin definir)'}")
        lines.append("**Próximos pasos:**")
        lines.append(_list_or_dash(dd["next_steps"]))

    elif method == "cps":
        cps = data["cps"]
        lines.append("## Clarificar")
        lines.append(f"**Reto:** {cps['challenge'] or '(sin definir)'}")
        lines.append("**Hechos y datos:**")
        lines.append(_list_or_dash(cps["facts"]))
        lines.append("")
        lines.append("## Idear")
        lines.append(_list_or_dash(cps["ideate"]))
        lines.append("")
        lines.append("## Desarrollar")
        lines.append(f"**Idea(s) más prometedora(s):** {cps['best_idea'] or '(sin definir)'}")
        lines.append("**Cómo fortalecerla:**")
        lines.append(_list_or_dash(cps["strengthen"]))
        lines.append("")
        lines.append("## Implementar")
        lines.append("**Plan de acción:**")
        lines.append(_list_or_dash(cps["action_plan"]))
        lines.append(f"**Apoyo y recursos:** {cps['support'] or '(sin definir)'}")

    elif method == "six-hats":
        hats = data["six_hats"]["hats"]
        for h in SIX_HATS:
            lines.append(f"## Sombrero {h['name']} — {h['label']}")
            lines.append(_list_or_dash(hats[h["key"]]))
            lines.append("")

    elif method == "brainstorming":
        b = data["brainstorming"]
        if b["sub_mode"] == "classic":
            lines.append("## Brainstorming clásico")
            lines.append(_list_or_dash(b["classic"]["ideas"], lambda it: ("⭑ " if it.get("starred") else "") + it["text"]))
        elif b["sub_mode"] == "brainwriting":
            lines.append("## Brainwriting 6-3-5")
            for i, r in enumerate(b["brainwriting"]["rounds"]):
                lines.append(f"### Ronda {i + 1}")
                lines.append(_list_or_dash(r))
        elif b["sub_mode"] == "mindmap":
            lines.append("## Mapa mental")
            for br in b["mindmap"]["branches"]:
                lines.append(f"### Rama: {br['name'] or '(sin nombre)'}")
                lines.append(_list_or_dash(br["ideas"]))
        else:
            lines.append("_Aún no se eligió una variante._")

    elif method == "triz":
        t = data["triz"]
        lines.append("## Contradicción")
        lines.append(f"**Quiero mejorar:** {t['improve'] or '(sin definir)'}")
        lines.append(f"**Pero empeora:** {t['worsen'] or '(sin definir)'}")
        lines.append("")
        lines.append("## Principios seleccionados")
        any_sel = False
        for n, name, desc in TRIZ_PRINCIPLES:
            sel = t["selected"].get(str(n)) or t["selected"].get(n)
            if sel and sel.get("selected"):
                any_sel = True
                lines.append(f"### {n}. {name}")
                lines.append(desc)
                if sel.get("note"):
                    lines.append(f"**Aplicación:** {sel['note']}")
                lines.append("")
        if not any_sel:
            lines.append("_Sin principios seleccionados aún._")

    elif method == "foresight":
        f = data["foresight"]
        if f["sub_mode"] == "scenarios":
            sc = f["scenarios"]
            lines.append("## Señales y tendencias")
            lines.append(_list_or_dash(sc["signals"]))
            lines.append("")
            lines.append("## Fuerzas motrices")
            lines.append(_list_or_dash(sc["drivers"]))
            lines.append("")
            lines.append("## Escenarios")
            any_scen = False
            for i, scen in enumerate(sc["scenario_list"]):
                if scen["name"] or scen["desc"]:
                    any_scen = True
                    lines.append(f"### {scen['name'] or f'Escenario {i + 1}'}")
                    lines.append(scen["desc"] or "_Sin descripción._")
            if not any_scen:
                lines.append("_Sin escenarios definidos._")
            lines.append("")
            lines.append("## Implicaciones")
            lines.append(_list_or_dash(sc["implications"]))
        elif f["sub_mode"] == "backcasting":
            bc = f["backcasting"]
            lines.append(f"## Futuro deseado (horizonte: {bc['horizon'] or '(sin definir)'})")
            lines.append(bc["vision"] or "_Sin definir._")
            lines.append("")
            lines.append("## Hitos intermedios")
            lines.append(_list_or_dash(bc["milestones"]))
            lines.append("")
            lines.append("## Obstáculos")
            lines.append(_list_or_dash(bc["obstacles"]))
            lines.append("")
            lines.append("## Acciones desde ahora")
            lines.append(_list_or_dash(bc["actions"]))
        elif f["sub_mode"] == "pestel":
            cats = f["pestel"]["categories"]
            for c in PESTEL_CATEGORIES:
                lines.append(f"## {c['name']}")
                lines.append(_list_or_dash(cats[c["key"]]))
                lines.append("")
        else:
            lines.append("_Aún no se eligió un enfoque de Foresight._")

    lines.append("---")
    lines.append("_Generado con Taller de Ideas (Streamlit)._")
    return "\n".join(lines)


def slugify(text):
    text = (text or "sesion").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:40] or "sesion"
