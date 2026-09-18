"""The ids for the records of one book, minted from the source names.

An id is kebab-case ASCII derived from the record's printed name, unique
within its parent: a unit within its faction, a group within its unit, a
choice within its group, a profile row within its unit. The first name to
claim a slug keeps it; a later collision gets a numeric suffix, by the order
the names are encountered in the source.

Nothing is read from or written to disk: an id is a function of the names
in the book as it stands, minted fresh on every run. So a name corrected in
the source changes its id, and keeping saved army lists working across that
is the army builder's job at release time, not this repository's.
"""

from __future__ import annotations

import re
import unicodedata

TABLES = ("units", "profiles", "groups", "choices", "rules", "items", "upgrades", "lores")


def slug(name: str) -> str:
    """kebab-case ASCII: diacritics folded, '&' read as 'and', the rest dropped."""
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("&", " and ").replace("'", "")
    s = re.sub(r"[^A-Za-z0-9]+", "-", s.lower()).strip("-")
    return s or "x"


class Ids:
    def __init__(self) -> None:
        self.data: dict = {t: {} for t in TABLES}
        self.suffixed: list[str] = []   # ids that needed a numeric suffix

    def _table(self, scope: tuple[str, ...]) -> dict:
        d = self.data[scope[0]]
        for s in scope[1:]:
            d = d.setdefault(s, {})
        return d

    def assign(self, scope: tuple[str, ...], name: str, base: str | None = None) -> str:
        """The id for `name` in the table `scope` names, minting one if new."""
        table = self._table(scope)
        if name in table:
            return table[name]
        base = slug(base if base is not None else name)
        taken = set(table.values())
        id_, n = base, 2
        while id_ in taken:
            id_ = f"{base}-{n}"
            n += 1
        table[name] = id_
        if id_ != base:
            self.suffixed.append(f"{'/'.join(scope)}: {name!r} -> {id_}")
        return id_
