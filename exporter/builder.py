"""The army builder's per-army layout, mapped from the formatVersion 2 data.

The builder (Warhammer_Calculator_Edition) reads a game system as a folder of
files: `manifest.json`, `composition.json`, `common-magic-items.json`, and per
army `factions/{key}.json` (the units) and `factions/{key}-extras.json` (army
rules, magic items, lores, faction upgrades). `layout` maps the bundle
export.py builds onto that folder, file by file, and docs/faction-files.md
describes the mapping. The builder's own `core-rules.json` and
`troop-types.json` are not ours to write.

Nothing here reads Typst or touches the disk: the bundle in, a dict of
relative path -> JSON value out.
"""

from __future__ import annotations

import re

from .ids import slug

SYSTEM = "war"

# The builder's own keys for the armies it already knows by another name.
KEYS = {"empire": "the-empire", "orcs-goblins": "orcs-and-goblins"}

CATEGORIES = {"Characters": "Characters", "Lords": "Lords", "Heroes": "Heroes",
              "Special Characters": "Named Characters", "Mounts": "Character Mounts",
              "Core": "Core", "Special": "Special", "Rare": "Rare"}

ITEM_CATEGORIES = {"weapon": "magic_weapon", "armour": "magic_armour", "talisman": "talisman",
                   "arcane": "arcane_item", "enchanted": "enchanted_item",
                   "standard": "magic_standard"}

ROLES = {"champion": "Leader", "musician": "Musician", "standardBearer": "Standard Bearer"}

STATS = ("name", "M", "WS", "BS", "S", "T", "W", "I", "A", "Ld", "points")

# A UnitEntry's text fields, every one emitted, null when the entry has none.
TEXT_FIELDS = ("troopType", "baseSize", "equipment", "magic", "specialRules", "upgrades",
               "notes", "unitSize", "crew", "mount", "drawnBy")

UNIT_KEYS = ("name", "category", "profiles", "troopType", "baseSize", "equipment", "magic",
             "options", "specialRules", "upgrades", "notes", "unitSize", "crew", "mount",
             "drawnBy", "pointsCost")


def numeric(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def faction_key(fid: str) -> str:
    return KEYS.get(fid, fid)


def family_key(fid: str) -> str:
    """A faction upgrade family as the builder keys it: "blessed-spawnings" -> "blessed_spawnings"."""
    return fid.replace("-", "_")


def cost_text(cost) -> str:
    """A cost as the builder's string: 45 -> "45", (5, 35, 55) -> "5/35/55", pairs one a line."""
    if cost is None:
        return "0"
    if numeric(cost):
        return str(int(cost)) if float(cost).is_integer() else str(cost)
    if isinstance(cost, list):
        if all(numeric(c) for c in cost):
            return "/".join(cost_text(c) for c in cost)
        return "\n".join(f"{who} {price}" for who, price in cost)
    return str(cost)


# --- units --------------------------------------------------------------------

def split_profiles(unit: dict) -> list[dict] | None:
    """The priced profiles a generic character entry splits into, or None if it stays whole."""
    priced = [p for p in unit["profiles"] if numeric(p["points"])]
    # A Mixed Unit's priced profiles are one unit's models (a Beastmaster and his Tigers).
    mixed = "mixed unit" in text_field("specialRules", unit.get("specialRules") or "").casefold()
    if unit["section"] == "characters" and not unit["named"] and len(priced) >= 2 and not mixed:
        return priced
    return None


def text_field(key: str, value):
    if value is None or isinstance(value, str):
        return value
    if isinstance(value, list):
        if value and all(isinstance(v, dict) for v in value):
            if key == "specialRules":
                return ", ".join(r["name"] for r in value)
            return "\n".join(f"{r['name']}: {r['text']}" for r in value)
        return "\n".join(v if isinstance(v, str) else f"{v['name']}: {v['text']}" for v in value)
    return value


def profile(row: dict) -> dict:
    out = {k: row.get(k) for k in STATS}
    if not numeric(out["points"]):
        out["points"] = None
    return out


def keep(groups: list[dict], pid: str) -> list[dict]:
    """The groups and choices that apply to the profile `pid`, at every depth."""
    out = []
    for g in groups:
        if g.get("appliesTo") not in (None, pid):
            continue
        choices = [dict(c, options=keep(c.get("options") or [], pid))
                   for c in g["choices"] if c.get("appliesTo") in (None, pid)]
        if choices:
            out.append(dict(g, choices=choices))
    return out


def unit_entry(unit: dict, name: str, rows: list[dict], pid: str | None) -> dict:
    names = {p["id"]: p["name"] for p in unit["profiles"]}
    groups = unit["optionGroups"] if pid is None else keep(unit["optionGroups"], pid)
    options = one_per_family(options_of(groups, names), set())
    profiles = [profile(r) for r in rows]
    entry = {"name": name, "category": CATEGORIES.get(unit["category"], unit["category"]),
             "profiles": profiles, "options": options or None,
             "pointsCost": next((p["points"] for p in profiles if numeric(p["points"])), None)}
    for key in TEXT_FIELDS:
        entry[key] = text_field(key, unit.get(key))
    return {k: entry[k] for k in UNIT_KEYS}


def units_of(unit: dict) -> list[dict]:
    """The builder units one entry becomes: one, or one per priced profile."""
    priced = split_profiles(unit)
    if priced is None:
        return [unit_entry(unit, unit["name"], unit["profiles"], None)]
    rest = [p for p in unit["profiles"] if not numeric(p["points"])]
    return [unit_entry(unit, p["name"], [p] + rest, p["id"]) for p in priced]


# --- options ------------------------------------------------------------------

def choice(ch: dict) -> dict:
    out = {"name": ch["name"], "points": ch["points"] if numeric(ch["points"]) else None,
           "perModel": bool(ch.get("perModel"))}
    if "replaces" in ch:
        out["replaces"] = ch["replaces"]
    return out


def nested(ch: dict, names: dict[str, str]) -> list[dict]:
    return options_of(ch.get("options") or [], names)


def upgrade(ch: dict, raw: str, names: dict[str, str]) -> dict:
    return {"type": "upgrade", "upgrade": ch["name"],
            "points": ch["points"] if numeric(ch["points"]) else None,
            "perModel": bool(ch.get("perModel")), "raw": raw,
            "subOptions": nested(ch, names) or None}


def head_of(raw: str) -> str:
    """A menu's label: its first line without the trailing colon."""
    return raw.split("\n")[0].strip().removesuffix(":").strip()


def group_options(g: dict, names: dict[str, str]) -> list[dict]:
    """One formatVersion 2 group as builder options, by kind."""
    kind, raw, chs = g["kind"], g["raw"], g["choices"]
    own = lambda c: raw if len(chs) == 1 else c["raw"]
    pts = lambda v: v if numeric(v) else None
    if kind == "equipment":
        reps = [c.get("replaces") for c in chs]
        action = ("replace" if any(r is not None for r in reps)
                  else "choose" if len(chs) > 1 else "add")
        opt: dict = {"type": "equipment", "action": action}
        if reps and reps[0] is not None and all(r == reps[0] for r in reps):
            opt["replaces"] = reps[0]
        opt.update(choices=[choice(c) for c in chs], raw=raw,
                   subOptions=[o for c in chs for o in nested(c, names)] or None)
        return [opt]
    if kind == "mount":
        return [{"type": "mount", "action": "choose", "choices": [choice(c) for c in chs],
                 "raw": raw, "subOptions": [o for c in chs for o in nested(c, names)] or None}]
    if kind == "command":
        return [{"type": "command", "role": ROLES.get(g.get("role"), g.get("role")),
                 "points": pts(c["points"]), "raw": own(c),
                 "subOptions": nested(c, names) or None} for c in chs]
    if kind == "magicStandard":
        return [{"type": "magic_standard", "pointsLimit": g.get("pointsLimit"), "raw": raw}]
    if kind == "magicItems":
        out = [{"type": "magic_items", "pointsLimit": g.get("pointsLimit"),
                "appliesTo": names.get(g.get("appliesTo")), "raw": raw}]
        out += [{"type": "faction_upgrade", "factionUpgrade": family_key(f), "raw": raw}
                for f in g.get("families") or []]
        return out
    if kind == "battleStandard":
        p = g.get("points") if g.get("points") is not None else (chs[0]["points"] if chs else None)
        return [{"type": "battle_standard", "points": pts(p), "raw": raw}]
    if kind == "wizardLevel":
        return [{"type": "wizard_upgrade", "upgrade": c["name"], "points": pts(c["points"]),
                 "perModel": bool(c.get("perModel")), "raw": own(c)} for c in chs]
    if kind == "factionUpgrade":
        # One priced choice prices the option; otherwise the builder sums the picks.
        one = len(chs) == 1 and numeric(chs[0]["points"])
        return [{"type": "faction_upgrade", "factionUpgrade": family_key(g["family"]),
                 "pointsLimit": g.get("pointsLimit"),
                 "points": chs[0]["points"] if one else None,
                 "perModel": bool(chs[0].get("perModel")) if one else None, "raw": raw}]
    # specialRule, upgrade (unclassified included) and any other kind.
    if len(chs) == 1:
        return [upgrade(chs[0], raw, names)]
    if g.get("select") == "one":
        return [{"type": "upgrade", "upgrade": head_of(raw), "raw": raw,
                 "subOptions": [{"type": "upgrade", "upgrade": c["name"], "choices": [choice(c)],
                                 "raw": c["raw"]} for c in chs] or None}]
    return [upgrade(c, c["raw"], names) for c in chs]


def options_of(groups: list[dict], names: dict[str, str]) -> list[dict]:
    return [o for g in groups for o in group_options(g, names)]


def one_per_family(opts: list[dict], seen: set[str]) -> list[dict]:
    """At most one option per upgrade family in a unit, the first met; two double-charge."""
    out = []
    for o in opts:
        if o["type"] == "faction_upgrade":
            if o["factionUpgrade"] in seen:
                continue
            seen.add(o["factionUpgrade"])
        if o.get("subOptions"):
            o["subOptions"] = one_per_family(o["subOptions"], seen) or None
        out.append(o)
    return out


# --- extras -------------------------------------------------------------------

def item(it: dict) -> dict:
    return {"name": it["name"], "points": cost_text(it["cost"]),
            "category": ITEM_CATEGORIES.get(it["category"], it["category"]),
            "description": it["text"], "restriction": it.get("only")}


def lore(lo: dict) -> dict:
    """A lore: its attribute lifted out of the spell list, levels and casting values as integers."""
    attribute = None
    spells = []
    for sp in lo["spells"]:
        if sp["level"] == "Lore Attribute":
            attribute = sp["text"]
            continue
        cast = re.match(r"\s*(\d+)", sp.get("cast") or "")
        spells.append({"name": sp["name"],
                       "level": 0 if sp["level"] == "Signature Spell" else sp["level"],
                       "castValue": int(cast.group(1)) if cast else 0,
                       "description": sp["text"], "type": None})
    return {"name": lo["name"], "attribute": attribute, "spells": spells}


def upgrade_family(up: dict) -> str:
    """The family an upgrade belongs to: its chapter's id, as optionGroups' `family` holds it."""
    return family_key(slug(up["chapter"]))


def extras(fac: dict) -> dict:
    families: dict[str, list[dict]] = {}
    for up in fac["upgrades"]:
        families.setdefault(upgrade_family(up), []).append(
            {"name": up["name"], "points": cost_text(up["cost"]), "description": up["text"]})
    return {"factionName": fac["name"],
            "armySpecialRules": [{"name": r["name"], "description": r["text"]}
                                 for r in fac["rules"]],
            "magicItems": [item(it) for it in fac["items"]],
            "loresOfMagic": [lore(lo) for lo in fac["lores"]],
            "factionUpgrades": families}


# --- the system files -----------------------------------------------------------

def composition(comp: dict) -> dict:
    cats = comp.get("pointsCategories", {})
    return {"system": SYSTEM,
            "charactersCombinedMaxPercent": cats.get("characters", {}).get("maxPercent"),
            "singleUnitMaxPercent": comp.get("singleUnitMaxPercent"),
            "categories": {k: {f: cats[k][f] for f in ("minPercent", "maxPercent")
                               if cats[k].get(f) is not None}
                           for k in ("core", "special", "rare", "lords", "heroes") if k in cats}}


def layout(data: dict) -> dict[str, object]:
    """The builder's files for the bundle, keyed by path relative to the system folder."""
    factions = sorted(data["factions"].values(), key=lambda f: faction_key(f["id"]))
    files: dict[str, object] = {
        "manifest.json": {"system": SYSTEM,
                          "factions": [faction_key(f["id"]) for f in factions]},
        "composition.json": composition(data["composition"]),
        "common-magic-items.json": [item(it) for it in data["rulebook"]["items"]],
    }
    for fac in factions:
        key = faction_key(fac["id"])
        files[f"factions/{key}.json"] = {
            "factionName": fac["name"],
            "units": [u for unit in fac["units"] for u in units_of(unit)]}
        files[f"factions/{key}-extras.json"] = extras(fac)
    return files
