# Changelog

## The army builder's per-army files — 2026-10-01

The export writes what the army builder reads: a game system as a folder of
per-army files, not one bundle. The formatVersion 2 bundle stays what the
export builds and the gate checks against the source, and every file the
builder gets is mapped from it. `docs/faction-files.md` describes the
layout and the mapping.

Added:

- `build/war/`, written by `python export.py` (or into `--out DIR`):
  `manifest.json`, `composition.json`, `common-magic-items.json`, and
  `factions/{key}.json` with `factions/{key}-extras.json` for each of the 30
  armies. The Empire and the Orcs & Goblins take the builder's keys,
  `the-empire` and `orcs-and-goblins`. The builder's own `core-rules.json`
  and `troop-types.json` are left alone.
- `exporter/builder.py`, the mapping: a generic character entry split into
  one unit per priced profile with the options that apply to it, categories
  and item categories in the builder's names, option groups as the builder's
  typed options, at most one option per upgrade family in a unit, lores with
  their attribute lifted out and integer levels and casting values, costs as
  the builder's strings.
- `schema/builder.schema.json`, one entry per kind of file, in the
  builder's types.
- Gate checks on the files: each conforms to its schema entry; every unit,
  item, army rule, upgrade and spell of the bundle is in them; every printed
  option line reaches an option; every upgrade family a unit names is defined
  and named once; the builder's own data tests pass (magic-item lines are
  allowances, every allowance resolves above 0); a split names no two units
  alike.
- The build report says, per army, the builder units, the entries split and
  the options by type, the unit names the source repeats, and the units the
  builder would file as Character Mounts.

Changed:

- The formatVersion 2 bundle is written only with `--bundle path.json`, and
  is byte-identical to before. The release copy is
  `python export.py --check --out ../Warhammer_Calculator_Edition/Warhammer/wwwroot/data/war`.

## war.json formatVersion 2 — 2026-09-15

The army-builder bundle becomes self-describing, so the list builder needs
no per-edition code. Every formatVersion 1 field keeps its exact value; the
new data is in new fields beside it. `docs/format.md` describes the format
with two worked examples.

Added:

- `formatVersion: 2` at the top level.
- `composition`: CHOOSING YOUR ARMY as data - the percentage limits per
  category, the single-unit cost limit, the duplicate-choice chart as bands,
  the general, battle standard and special-character rules - each value with
  the sentence it was read from. Per faction, `composition.unitConstraints`
  parsed from unit NOTES: army maximums, "1-2 as a single choice",
  unit ratios, Army General rules, handler ratios. The vocabulary also
  defines "0-1 per N points" limits and "must include" minimums, which no
  WAR book prints, so that the same rule engine can read another edition.
- Ids: `id` on every faction, rule, item, upgrade, lore, unit, profile row,
  option group and choice, minted from the source names on every export -
  the slug of the printed name, a numeric suffix where two names in one
  parent collide. A name corrected in the source changes its id; keeping
  saved lists working across that is the builder's job at release time.
- `optionGroups` on every unit: the typed view of the printed OPTIONS. Each
  line becomes a group with a `kind` (`equipment`, `mount`, `command`,
  `magicStandard`, `magicItems`, `battleStandard`, `wizardLevel`,
  `factionUpgrade`, `specialRule`, `upgrade`), a `select` rule (`one`, `any`,
  `count`), `min`/`max`, `appliesTo`, and typed choices; nested options sit
  on the choice they depend on. A line the classifier cannot place is emitted
  as `upgrade` with `unclassified: true`. Nothing is dropped.
- `section`, `tier`, `named` on every unit; `unitSizeParsed`; `equipmentList`
  and `specialRulesList`.
- `schema/war.schema.json`, validated by `--check`.
- A build report printed by `--check`: units, groups, choices and
  unclassified lines per faction, unparsed unit sizes, suffixed ids.

Changed:

- `export.py` grew a helper package, `exporter/`: `ids.py`, `options.py`,
  `composition.py`, `schema.py`.
- The gate also checks that every option line is in `optionGroups` exactly
  once and in the source, that every constraint is a note of its unit, and
  that the file conforms to the schema.
