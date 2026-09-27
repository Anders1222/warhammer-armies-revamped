"""Redraw the Empire support diagram using the rulebook's shared SVG style.

Run from any working directory; only the Python standard library is required.
"""
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parent
Diagram = runpy.run_path(str(ROOT.parent / 'rulebook' / 'redraw.py'))['Diagram']


def main():
    d = Diagram(198, 'State Troop support')
    # Preserve the original example: twenty enemy models face twenty State
    # Troops, ten supporters contact the enemy's left flank, and a second
    # ten-model supporting unit faces the combat from the right.
    d.unit(215, 215, 5, 4, 'red', 30, facing='down')
    d.unit(215, 335, 5, 4, cell=30)
    d.unit(155, 185, 2, 5, cell=30, facing='right')
    d.unit(400, 425, 5, 2, cell=30, angle=-30)

    d.text(290, 191, 'Enemy', 26)
    d.text(127, 271, 'Support Charge', 26, rotate=-90)
    d.text(290, 490, 'State Troops', 26)
    d.text(476, 520, 'Support Fire', 26)
    d.save(ROOT)
    print('Wrote assets/figures/empire/img-0198.svg')


if __name__ == '__main__':
    main()
