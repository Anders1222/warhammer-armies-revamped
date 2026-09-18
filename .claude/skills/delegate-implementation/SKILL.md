---
name: delegate-implementation
description: Delegate a specified change in this repository to the implementer agent and review it — locate touchpoints with scout, write the self-contained brief, spawn the implementer, review the diff against the brief (at most two fix rounds), run the reserved verification, deliver the result as a pull request into main for the user to review and merge. Use when a plan or spec exists for a change that the build or export gate can check and is more than a one-file fix, so the implement-and-check loop runs off the session's model; not for diagnosis, exploration or math.
---

# delegate-implementation

Three phases, two models: this session plans, briefs and reviews; the
`implementer` agent (Opus) edits, builds and checks in a fresh context;
`scout` (Haiku) locates touchpoints so neither this session nor the
implementer reads the tree to find them.

## Fit test

Delegate a change whose scope is known, that has a mechanical oracle
(`python build.py`, `python export.py --check`, `python emit.py`), and
that is more than a one-file fix. Keep in this session: diagnosis and
investigation where the plan emerges from exploring, analysis and math,
changes nothing can verify mechanically, one-file fixes. Changes to a
book's prose are checkable only by the render comparisons, which need a
baseline render this session makes before the branch is cut.

## Phase A — locate and brief

1. Spawn `scout` (in parallel if several areas) with the search terms
   the change implies: field names, `UNIT_FIELDS` keys, template
   functions, exporter symbols, schema properties, unit names. Its
   `path:line` lines become the brief's scope; the session reads a file
   itself only when a design call needs it.
2. If the reserved verification is a render comparison (`render-text`,
   `render-glyphs`), build the baseline now: `python build.py` on the
   branch of record and copy `out/` aside, before any edit.
3. Create the feature branch from the branch of record
   (`git switch -c <slug> main`; branch names here are plain slugs, no
   `feat/` prefix) — the implementer may not switch branches itself.
4. Write the brief into the implementer prompt, in this order:

| Item | What goes in |
|---|---|
| Goal | One paragraph: the change and why, as a PR body would say it |
| Repository, branch | Absolute path of the clone; the feature branch to work on (created, checked out) and `main` as the branch the PR will target |
| Orientation | `CLAUDE.md`, the relevant section of `src/template.typ`, `docs/format.md` for export changes, plus the files the change depends on |
| Scope | Files or areas to change, one line each (from the scout hits); everything else is out of scope |
| Acceptance criteria | Observable, checkable statements: build exit 0, `check: ok`, no new `unclassified` line |
| Verification the implementer runs | Exact commands: `python build.py` (whole corpus for a template change), `python export.py --check`, `python emit.py` when a book or its meta changed |
| Verification reserved for the session | `render-text`/`render-glyphs` against the baseline, `check-site`, the `extract/` gates that need the source PDFs |
| Decisions already taken | Design choices from the planning phase, so the implementer does not re-derive them differently |
| Constraints | Do-not-touch list; `site/index.html` is generated, never hand-edited; smart quotes stay off; no `to_book.py` on an existing slug |

State the two subagent adaptations in the brief: "ask, don't assume"
becomes implement the unambiguous part and report every open question;
"ask before committing" becomes never commit.

## Phase B — implement

One `implementer` per change. It returns its report; it never commits or
exports into the builder repo. Long build logs or export build reports
it names go through `log-summarizer`, not into this session.

## Phase C — review

Read the diff (`git diff`), not the implementer's narrative, and check:

1. Completeness — every scope line and acceptance criterion covered;
   nothing outside the scope changed.
2. Correctness against the sources the brief cited.
3. Verification evidence — the named commands ran and their result
   lines are in the report; an error line or a missing `check: ok` is a
   finding. Read the export build report for new ids and `unclassified`
   lines: the gate does not fail on them.
4. Deviations and open questions — each accepted (recorded in the
   commit message) or sent back.
5. Conventions — one line per comment, no unrelated edits, generated
   files (`site/index.html`, `build/render.json`) regenerated not
   edited.

Findings go back to the same implementer (SendMessage keeps its
context) as a delta brief, at most two rounds; then finish the change in
this session instead of a third round. Then run the reserved
verification.

## Phase D — deliver as a pull request

The reviewed change always reaches the user as a pull request into
`main`; the user reviews and merges it there. Merging publishes: CI
compiles every book on `build/render.json` to GitHub Pages on push to
`main`.

1. Commit on the feature branch (accepted deviations go in the message;
   a plain declarative sentence, as `CLAUDE.md` says) and push it. The
   implementer never commits — this session does, after Phase C and the
   reserved verification.
2. Open the PR with `gh pr create --base main --head <feature branch>`.
   Title: the goal in one line, in the commit-message voice. Body: the
   goal, per-file changes, the verification result lines (the
   implementer's checks and the reserved ones), accepted deviations,
   open questions for the reviewer.
3. Report the PR link and the verification summary. Merging, and
   pushing to `main`, stay with the user.

Committing and pushing on the feature branch to open the PR is the one
exception to the ask-before-committing rule. Revisions the reviewer asks
for go on the same branch as new commits, through Phase C as a delta
brief when delegated.

## Safety boundaries

The implementer writes only inside this repository and never commits.
This session pushes only the feature branch, only to open the PR;
merging and pushing to `main` are the user's, and so is the release
export into the builder repo. A report claiming the checks pass without
result lines counts as not verified. A brief whose acceptance criteria
cannot be written means the change does not fit this skill.
