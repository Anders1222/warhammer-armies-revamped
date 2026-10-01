# The army builder's files

The army builder
([Warhammer_Calculator_Edition](https://github.com/dkma26709/Warhammer_Calculator_Edition))
reads a game system as a folder of JSON files. `python export.py` writes that
folder for the edition, into `build/war/` or the folder `--out` names. The
files are mapped from the formatVersion 2 bundle (`docs/format.md`) by
`exporter/builder.py`; nothing edits them by hand. `python export.py --check`
is the gate, and `schema/builder.schema.json` is the JSON Schema it validates
each file against.

The mapping takes the builder's types as they are: a profile's `points` is a
number or `null`, a magic item's or upgrade's `points` a string, a spell's
`level` and `castValue` integers, a choice's `perModel` never `null`. The
builder reads with System.Text.Json, which throws on a string where it wants
a number and on `null` where it wants a bool, so a wrong type is not a
display fault but a faction that does not load.

## Layout

```
manifest.json
composition.json
common-magic-items.json
factions/
  albion.json
  albion-extras.json
  ...
  zombie-pirates.json
  zombie-pirates-extras.json
```

Every file is UTF-8 with LF line endings, `indent=1`, non-ASCII kept. The
export overwrites the files it writes and touches nothing else in the
folder, which in the builder also holds files it owns (below).

| file | shape |
|---|---|
| `manifest.json` | `{"system": "war", "factions": [<key>, ..]}`, the keys sorted |
| `composition.json` | `{system, charactersCombinedMaxPercent, singleUnitMaxPercent, categories}` |
| `common-magic-items.json` | an array of the rulebook's magic items, each as a faction's are |
| `factions/{key}.json` | `{factionName, units}` |
| `factions/{key}-extras.json` | `{factionName, armySpecialRules, magicItems, loresOfMagic, factionUpgrades}` |

`factionName` in both faction files is the faction's `name`.

`composition.json` is read from the bundle's `composition`:
`charactersCombinedMaxPercent` is `pointsCategories.characters.maxPercent`,
`singleUnitMaxPercent` is `singleUnitMaxPercent`, and `categories` holds
`core`, `special`, `rare` (and `lords`, `heroes` where present) with their
`minPercent` and `maxPercent`, a `null` left out. A faction's own
`unitConstraints` have no place in the file and are not written.

## Faction keys

An army's key is its slug in the bundle, except two, which take the key the
builder already has for them:

| slug | key |
|---|---|
| `empire` | `the-empire` |
| `orcs-goblins` | `orcs-and-goblins` |

## Units

Each formatVersion 2 unit becomes one builder unit, keeping its printed
`name` and all its profiles, with one exception: a **generic character
entry is split**. A unit whose `section` is `characters`, that is not
`named`, that does not have the Mixed Unit special rule, and that has two or
more profiles with numeric `points` becomes one builder unit per priced
profile, in profile order. (A Mixed Unit's priced profiles are models of one
unit, not alternatives: Kingdoms of Ind's Beastmaster and his Tigers.) Each takes that profile's
printed name; its `profiles` are that profile, then every profile whose
points are not numeric (a mount, a crew) in source order; and its options
are only the groups, at every depth, whose `appliesTo` is `null` or that
profile, and within them only the choices whose own `appliesTo` is `null` or
that profile. A group left with no choices is dropped. Every other field is
copied to each. The Empire's COMMANDERS is the builder's General (with the
Griffons, which are General only) and Captain (with the Battle Standard,
which a Captain carries).

A unit has every key, `null` when the entry has none, in this order:
`name`, `category`, `profiles`, `troopType`, `baseSize`, `equipment`,
`magic`, `options`, `specialRules`, `upgrades`, `notes`, `unitSize`, `crew`,
`mount`, `drawnBy`, `pointsCost`.

| category | builder category |
|---|---|
| Characters, Lords, Heroes | unchanged |
| Special Characters | Named Characters |
| Mounts | Character Mounts |
| Core, Special, Rare | unchanged |

A category outside the table fails the gate.

- `profiles`: `{name, M, WS, BS, S, T, W, I, A, Ld, points}`, stats as the
  bundle has them (an integer or a string such as "D6"). `points` is the
  number, or `null` for anything else ("-", none). No `id`.
- `pointsCost`: the first numeric `points` among the unit's profiles, else
  `null`.
- The text fields - `troopType`, `baseSize`, `equipment`, `magic`,
  `specialRules`, `upgrades`, `notes`, `unitSize`, `crew`, `mount`, `drawnBy`
  - are strings. A string stays as it is; a list of strings is joined one a
  line; a list of named rules is the names joined with ", " for
  `specialRules`, and `name: text` one a line for the others.
- Nothing else is written: not the `*Body` companions, not `chapter`,
  `subtitle`, `solo`, `compact`, `id`, `section`, `tier`, `named`,
  `unitSizeParsed`, `equipmentList`, `specialRulesList`, the formatVersion 1
  `options`, the handlers, `magicItems` or the gift lists.

## Options

`options` maps `optionGroups`, and is `null` when that yields nothing. A
choice is `{name, points, perModel}`, with `replaces` when the choice has
one; `points` is a number or `null`, and `perModel` is always a bool (a price
per Crew or per Genie counts as `false`). A choice's nested groups map, the
same way, into the option's `subOptions`; for equipment and mounts the
nested groups of all the choices are joined. `subOptions` is `null` when
empty, never `[]`, which the builder would render as nothing.

| kind | builder option |
|---|---|
| `equipment` | `{type: "equipment", action, replaces?, choices, raw, subOptions}`. `action` is `replace` if any choice replaces something, else `choose` for several choices, else `add`. `replaces` is set when every choice replaces the same thing |
| `mount` | `{type: "mount", action: "choose", choices, raw, subOptions}` |
| `command` | one per choice: `{type: "command", role, points, raw, subOptions}`. `role` is `Leader`, `Musician` or `Standard Bearer`; `raw` is the group's line for one choice, else the choice's; `subOptions` are the choice's nested groups |
| `magicStandard` | `{type: "magic_standard", pointsLimit, raw}` |
| `magicItems` | `{type: "magic_items", pointsLimit, appliesTo, raw}`, `appliesTo` the printed name of the profile the line names, else `null`; then for each family in `families`, `{type: "faction_upgrade", factionUpgrade, raw}` |
| `battleStandard` | `{type: "battle_standard", points, raw}`, the group's points or else its first choice's |
| `wizardLevel` | one per choice: `{type: "wizard_upgrade", upgrade, points, perModel, raw}`, `raw` as for `command` |
| `factionUpgrade` | `{type: "faction_upgrade", factionUpgrade, pointsLimit, points, perModel, raw}`. `points` and `perModel` only when the group is one priced choice; otherwise `null`, and the builder sums the entries picked |
| `specialRule`, `upgrade`, any other | one choice: `{type: "upgrade", upgrade, points, perModel, raw, subOptions}`. Several with `select: "one"`: `{type: "upgrade", upgrade, raw, subOptions}`, labelled with the menu line's first line without its colon, a sub-option `{type: "upgrade", upgrade, choices: [choice], raw}` per choice. Several with `any` or `count`: one flat upgrade per choice, `raw` the choice's |

`factionUpgrade` is the family id with "-" read as "_": `blessed-spawnings`
is `blessed_spawnings`, the key of the family in the extras. A unit carries
at most one option per family, at any depth, the first met: the builder
charges each option naming a family, so a second would charge twice.

The builder compares a `magic_items` option's `appliesTo` to the unit's
name, then falls back to the option with no `appliesTo`, then to the
smallest `pointsLimit`. A split unit's allowance therefore names it; an
unsplit unit whose line names a profile ("A Champion may take ...") gets
one of the fallbacks.

## Extras

- `armySpecialRules`: the faction's `rules`, `{name, description}`.
- `magicItems`: the faction's `items`, `{name, points, category,
  description, restriction}`, `restriction` the item's `only` or `null`.
- `loresOfMagic`: `{name, attribute, spells}`. The spell whose level is "Lore
  Attribute" is not a spell: its text is the lore's `attribute`, `null` when
  the lore has none. A spell is `{name, level, castValue, description, type:
  null}`; `level` is 0 for the "Signature Spell" and the number otherwise,
  any other level failing the gate; `castValue` is the leading integer of
  the casting value ("7+" is 7), else 0. `spells` is always a list.
- `factionUpgrades`: `{family: [{name, points, description}]}`, the family
  the id of the upgrade's chapter as `factionUpgrade` writes it, `{}` when the
  faction has none. The Dwarfs' runes are one family, `runic_items`, here;
  filing them under the builder's rune item categories is still to do.

| item category | builder category |
|---|---|
| `weapon` | `magic_weapon` |
| `armour` | `magic_armour` |
| `talisman` | `talisman` |
| `arcane` | `arcane_item` |
| `enchanted` | `enchanted_item` |
| `standard` | `magic_standard` |

A category outside the table fails the gate.

A cost is written as a string: a number as itself (`45` is "45"), no cost as
"0", a tiered cost joined with "/" ("25/50/100"), and a per-model price list
one `who price` pair a line ("Characters free", "Cavalry/Infantry 1 point
per model"). The builder parses the string as a number and counts anything
else as 0.

## What is not written

`core-rules.json` and `troop-types.json` are in the builder's system folder
too, but the builder owns them, and the export neither writes nor deletes
them. The builder has to register the `war` system, and its `FactionKey`
enum knows 15 armies: a manifest key outside it is skipped with a warning,
so the other 15 WAR armies (Albion, Amazons, Araby, Chaos Dwarfs, Dogs of
War, Estalia, Grand Cathay, Halflings, Hobgoblins, Kingdoms of Ind, Kislev,
Nippon, Norsca, Pirates of Sartosa, Zombie Pirates) need members added on
the builder's side.

## The gate

After the checks `docs/format.md` lists, `python export.py --check` holds
the builder's files to the bundle they were mapped from, and fails when:

1. a file does not conform to its entry in `schema/builder.schema.json`
   (`manifest`, `composition`, `commonMagicItems`, `faction`, `extras`): an
   unknown option type or unit category, a unit with no profiles, a string
   where the builder wants a number or the reverse, a `null` `perModel`;
2. a record is missing: a unit that does not yield its builder units, in
   order (one, or one per priced profile); an item, army rule, upgrade or
   spell that is not in the extras by name; a common item; a manifest key
   with no files, or files with no key, or a `system` other than "war";
3. a printed option line does not reach the builder: for every group, its
   line or every one of its choices' lines is the `raw` of some option, at
   any depth, in the units its entry yields;
4. a `faction_upgrade` names a family the extras do not define, or a unit
   names one family twice;
5. the builder's own data tests would fail: a line pricing "Magic Items ...
   N points" on an option that is not `magic_items` or `faction_upgrade`, or a
   unit with a `magic_items` option that resolves to no allowance;
6. a split gives two units of a faction one name, which the builder keys
   saved lists by.

The build report then adds, per army, the builder units, the entries split
and the options by type; the names the source itself repeats within an army;
and the units with no `pointsCost` and no `unitSize` that are not Character
Mounts, which the builder files as Character Mounts whatever their category.
