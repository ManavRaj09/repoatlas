# 🗺️ RepoAtlas

**Turn any git repo's history into a procedurally generated fantasy world map.**

Folders become kingdoms. Files become cities. Bugs become battles. Abandoned code disappears into fog.
The same repo always generates the same world (the root commit hash is the random seed).

> 📸 *Add your hero GIF of the timeline replay here: `docs/hero.gif`*

## Quick start

```bash
pip install repoatlas          # or: pip install .  from this folder
repoatlas .                    # map the current repo -> atlas.html
repoatlas https://github.com/pallets/flask -o flask.html
```

Open the HTML file in a browser. **No dependencies, no server**: just Python 3.8+ and `git`.

## What the map means

| Repo data | On the map |
|---|---|
| Top-level folder | Kingdom (area ∝ code size + activity) |
| File | City (size ∝ lines of code) |
| Commits in last 90 days | Glowing city |
| Untouched for 18+ months | Fog |
| Deleted file | Ruins |
| Top contributor | Faction: kingdom color |
| Commit message with "fix"/"bug" | ⚔ battle marker (3+ per file) |
| Top 8% most-changed files | ⛈ storm (Repo Weather) |
| Regions edited in the same commits | Golden bridges |

## Interactions
- **Scroll** to zoom, **drag** to pan, **hover** a city for stats (`auth.py: 42 commits, last touched 8 months ago`)
- **Timeline slider / ▶ Replay** watches the world grow commit by commit
- **⬇ PNG** exports a 2400×1600 image to share

## How it works
1. `gitdata.py` runs `git log --name-only` once and aggregates per-file commits, authors, fix-counts, first/last touch, plus co-change pairs between folders.
2. `cli.py` injects that JSON into `template.html`, producing one portable file.
3. The viewer seeds a PRNG from the root commit, builds an island with fractal value noise, assigns land to the nearest *weighted* kingdom seed through a noise-warped distance field (organic borders, a cheap Voronoi), then scatters cities by Poisson-style rejection sampling and connects them with nearest-neighbor roads.

**Design decisions:** zero dependencies for instant install; determinism for shareable, comparable maps; capped at 300 files / 14 regions so the map stays readable.

## Keep a map in your repo
Copy `.github/workflows/atlas.yml`. It regenerates `docs/atlas.html` on every push; enable GitHub Pages on `/docs` to host it live.

## Roadmap
- [ ] Headless PNG export for README badges (`--png`)
- [ ] Real Voronoi/Delaunay rendering, rivers along import graphs
- [ ] Seasons (commit time-of-year), day/night
- [ ] Gallery: React, Linux, Django maps

Topics: `git` `visualization` `procedural-generation` `developer-tools` `python` `cli`

MIT licensed. PRs welcome.
