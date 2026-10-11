# Rulebook diagrams

The 46 SVGs in this directory are original vector drawings for **Warhammer
Armies Revamped**. They replace the imported JPEG rule diagrams, keeping the
same examples, measurements, opposing forces and numbered sequences. The
existing numeric filenames preserve the mapping to the rulebook references.

Open [gallery.html](gallery.html) to browse the complete set. The compiled
book is `out/rulebook.pdf` after running `python build.py rulebook`.

## Design

- Warm ivory panels, dark brown ink, muted blue and oxblood forces, and gold
  character crowns complement the book's parchment and Libertinus typography.
- Facing chevrons, crossed casualties, solid/dotted attack outlines and dashed
  previous positions retain meaning independently of colour.
- Text and geometry remain vector content in the PDF. No raster images or
  external resources are embedded in the SVGs.
- Scenario maps retain the deployment dimensions. They are schematic rather
  than measuring templates.

## Editing

`redraw.py` contains the editable geometry and the shared drawing primitives.
It uses only the Python standard library. Regenerate the SVGs, gallery and
inventory from the repository root with:

```sh
python assets/figures/rulebook/redraw.py
python build.py
```

`manifest.json` lists all 46 filenames, titles and canvas dimensions. Commit
the generated SVGs alongside source changes: publishing only needs Typst and
does not run this drawing script. The SVG labels use Libertinus Serif, also
used by the book, with serif fallbacks for browser previews.

When changing a diagram, check its surrounding rule and caption in
`src/rulebook.typ`, then inspect the compiled page. Base counts, base sizes,
facing, contact edges, arc boundaries, casualties and measurements carry rules
information and must be reviewed along with appearance.
