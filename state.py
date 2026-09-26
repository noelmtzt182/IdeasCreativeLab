"""Manejo de st.session_state: estructura de datos por método y progreso."""
import streamlit as st

from data import PESTEL_CATEGORIES


def ensure_session_state():
    ss = st.session_state
    ss.setdefault("started", False)
    ss.setdefault("problem", "")
    ss.setdefault("method", None)
    ss.setdefault("data", {})
    ss.setdefault("advisor", {"status": "idle", "input": "", "id": None, "reason": None, "error": None})
    ss.setdefault("timers", {})
    ss.setdefault("api_key", "")
    ss.setdefault("model_id", "claude-haiku-4-5")
    ensure_method_data()


def ensure_method_data():
    d = st.session_state.data
    d.setdefault("scamper", {**{k: [] for k in ["S", "C", "A", "M", "P", "E", "R"]}, "step": 0})
    d.setdefault("design_thinking", {
        "empathize": [], "define": {"user": "", "need": "", "insight": ""},
        "ideate": [], "prototype": {"description": "", "questions": []},
        "test": {"worked": [], "didnt_work": [], "adjustments": []}, "step": 0,
    })
    d.setdefault("double_diamond", {
        "discover": [], "problem_statement": "", "success_criteria": [],
        "develop": [], "chosen_solution": "", "next_steps": [], "step": 0,
    })
    d.setdefault("cps", {
        "challenge": "", "facts": [], "ideate": [], "best_idea": "",
        "strengthen": [], "action_plan": [], "support": "", "step": 0,
    })
    d.setdefault("six_hats", {"hats": {k: [] for k in ["white", "red", "black", "yellow", "green", "blue"]}, "step": 0})
    d.setdefault("triz", {"improve": "", "worsen": "", "selected": {}, "step": 0})
    d.setdefault("brainstorming", {
        "sub_mode": None,
        "classic": {"ideas": []},
        "brainwriting": {"round": 0, "rounds": [[], [], [], [], []]},
        "mindmap": {"branches": []},
    })
    d.setdefault("foresight", {
        "sub_mode": None,
        "scenarios": {
            "signals": [], "drivers": [],
            "scenario_list": [{"name": "", "desc": ""} for _ in range(3)],
            "implications": [], "step": 0,
        },
        "backcasting": {
            "horizon": "", "vision": "", "milestones": [], "obstacles": [], "actions": [], "step": 0,
        },
        "pestel": {"categories": {c["key"]: [] for c in PESTEL_CATEGORIES}, "step": 0},
    })


def reset_session():
    for key in ["started", "problem", "method", "data", "advisor", "timers", "ai_suggestions"]:
        if key in st.session_state:
            del st.session_state[key]
    ensure_session_state()


def compute_progress(method):
    d = st.session_state.data
    if method == "scamper":
        keys = ["S", "C", "A", "M", "P", "E", "R"]
        filled = sum(1 for k in keys if d["scamper"][k])
        return round(filled / len(keys) * 100)
    if method == "design-thinking":
        dt = d["design_thinking"]
        total, filled = 5, 0
        if dt["empathize"]:
            filled += 1
        if dt["define"]["user"] or dt["define"]["need"] or dt["define"]["insight"]:
            filled += 1
        if dt["ideate"]:
            filled += 1
        if dt["prototype"]["description"]:
            filled += 1
        if dt["test"]["worked"] or dt["test"]["didnt_work"] or dt["test"]["adjustments"]:
            filled += 1
        return round(filled / total * 100)
    if method == "double-diamond":
        dd = d["double_diamond"]
        total, filled = 4, 0
        if dd["discover"]:
            filled += 1
        if dd["problem_statement"] or dd["success_criteria"]:
            filled += 1
        if dd["develop"]:
            filled += 1
        if dd["chosen_solution"] or dd["next_steps"]:
            filled += 1
        return round(filled / total * 100)
    if method == "cps":
        cps = d["cps"]
        total, filled = 4, 0
        if cps["challenge"] or cps["facts"]:
            filled += 1
        if cps["ideate"]:
            filled += 1
        if cps["best_idea"] or cps["strengthen"]:
            filled += 1
        if cps["action_plan"] or cps["support"]:
            filled += 1
        return round(filled / total * 100)
    if method == "six-hats":
        keys = ["white", "red", "black", "yellow", "green", "blue"]
        filled = sum(1 for k in keys if d["six_hats"]["hats"][k])
        return round(filled / len(keys) * 100)
    if method == "triz":
        count = sum(1 for v in d["triz"]["selected"].values() if v.get("selected"))
        base = 20 if (d["triz"]["improve"] or d["triz"]["worsen"]) else 0
        return min(100, base + count * 15)
    if method == "brainstorming":
        b = d["brainstorming"]
        if b["sub_mode"] == "classic":
            return 100 if b["classic"]["ideas"] else 20
        if b["sub_mode"] == "brainwriting":
            filled_rounds = sum(1 for r in b["brainwriting"]["rounds"] if r)
            return round(filled_rounds / 5 * 100)
        if b["sub_mode"] == "mindmap":
            return 100 if b["mindmap"]["branches"] else 20
        return 0
    if method == "foresight":
        f = d["foresight"]
        if f["sub_mode"] == "scenarios":
            sc = f["scenarios"]
            total, filled = 4, 0
            if sc["signals"]:
                filled += 1
            if sc["drivers"]:
                filled += 1
            if any(s["name"] or s["desc"] for s in sc["scenario_list"]):
                filled += 1
            if sc["implications"]:
                filled += 1
            return round(filled / total * 100)
        if f["sub_mode"] == "backcasting":
            bc = f["backcasting"]
            total, filled = 4, 0
            if bc["vision"]:
                filled += 1
            if bc["milestones"]:
                filled += 1
            if bc["obstacles"]:
                filled += 1
            if bc["actions"]:
                filled += 1
            return round(filled / total * 100)
        if f["sub_mode"] == "pestel":
            cats = f["pestel"]["categories"]
            filled = sum(1 for v in cats.values() if v)
            return round(filled / len(cats) * 100)
        return 0
    return 0
