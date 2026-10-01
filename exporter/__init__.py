"""Helpers for export.py: the formatVersion 2 additions to the bundle, and
the army builder's files mapped from it.

  ids.py           kebab-case ids, minted from the source names on every run
  options.py       the typed view of a unit's OPTIONS (optionGroups)
  composition.py   army composition as data, from the rulebook and unit notes
  schema.py        a JSON Schema validator for the --check gate
  builder.py       the bundle as the army builder's per-army files

Nothing here reads Typst source. Everything works on the records export.py
already has, and adds fields beside the existing ones without changing them.
"""
