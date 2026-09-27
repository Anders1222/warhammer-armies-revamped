# Empire support diagram

[img-0198.svg](img-0198.svg) replaces the imported JPEG with an original vector
drawing in the rulebook's ivory, muted blue and oxblood style. It preserves the
formations, model counts and facings in the State Troop support example.

The editable geometry is in `redraw.py`, which reuses the drawing primitives
from `../rulebook/redraw.py`. Regenerate and compile from the repository root:

```sh
python assets/figures/empire/redraw.py
python build.py empire
```

Only the Python standard library is needed to generate the SVG. Commit the
generated asset alongside source edits; publishing uses the SVG directly.
