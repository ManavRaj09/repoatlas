"""Read a git repo's history and boil it down to JSON for the map renderer."""
import os, subprocess, tempfile
from collections import Counter, defaultdict
from itertools import combinations


def _git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True,
                          errors="replace", check=True).stdout


def clone_if_url(src):
    if "://" in src or src.startswith("git@"):
        tmp = tempfile.mkdtemp(prefix="repoatlas_")
        subprocess.run(["git", "clone", "--quiet", src, tmp], check=True)
        return tmp
    return src


def folder_of(path):
    return path.split("/")[0] if "/" in path else "(root)"


def collect(repo, max_files=300, max_regions=14):
    fmt = "@@%H%x1f%an%x1f%at%x1f%P%x1f%s"
    raw = _git(repo, "log", "--name-only", f"--pretty=format:{fmt}")
    commits, cur = [], None
    for line in raw.splitlines():
        if line.startswith("@@"):
            h, an, at, parents, subj = line[2:].split("\x1f")
            cur = dict(h=h, a=an, t=int(at), merge=len(parents.split()) > 1, s=subj, f=[])
            commits.append(cur)
        elif line.strip() and cur is not None:
            cur["f"].append(line.strip())
    if not commits:
        raise SystemExit("No commits found.")

    authors = [a for a, _ in Counter(c["a"] for c in commits).most_common(12)]
    aidx = {a: i for i, a in enumerate(authors)}
    files = defaultdict(lambda: dict(c=0, fix=0, first=10**12, last=0, au=Counter()))
    pairs = Counter()
    for c in commits:
        regs = set()
        for p in c["f"]:
            f = files[p]
            f["c"] += 1
            f["first"], f["last"] = min(f["first"], c["t"]), max(f["last"], c["t"])
            f["au"][c["a"]] += 1
            if "fix" in c["s"].lower() or "bug" in c["s"].lower():
                f["fix"] += 1
            regs.add(folder_of(p))
        if len(regs) > 1 and len(regs) < 8:
            for a, b in combinations(sorted(regs), 2):
                pairs[(a, b)] += 1

    alive = set(_git(repo, "ls-files").splitlines())
    out = []
    for p, f in files.items():
        loc = 0
        if p in alive:
            try:
                fp = os.path.join(repo, p)
                if os.path.getsize(fp) < 1_000_000:
                    with open(fp, "rb") as fh:
                        loc = fh.read().count(b"\n") + 1
            except OSError:
                pass
        top = f["au"].most_common(1)[0][0]
        out.append(dict(p=p, r=folder_of(p), loc=loc, c=f["c"], fix=f["fix"], first=f["first"],
                        last=f["last"], a=aidx.get(top, len(authors) - 1), dead=p not in alive))
    # keep the most interesting files: alive + busiest
    out.sort(key=lambda x: (x["dead"], -x["c"]))
    out = sorted(out[:max_files], key=lambda x: x["p"])

    # collapse tiny regions into "(misc)"
    size = Counter()
    for f in out:
        size[f["r"]] += f["loc"] + 50 * f["c"]
    keep = {r for r, _ in size.most_common(max_regions)}
    for f in out:
        if f["r"] not in keep:
            f["r"] = "(misc)"
    bridges = [[a, b, n] for (a, b), n in pairs.most_common(12) if a in keep and b in keep]

    return dict(
        name=os.path.basename(os.path.abspath(repo)),
        seed=commits[-1]["h"],  # root commit hash => same repo, same world
        now=max(c["t"] for c in commits), start=min(c["t"] for c in commits),
        authors=authors, files=out, bridges=bridges,
        stats=dict(commits=len(commits), merges=sum(c["merge"] for c in commits), files=len(files)),
    )
