import argparse, json, pathlib, shutil, sys
from . import __version__
from .gitdata import clone_if_url, collect


def main(argv=None):
    ap = argparse.ArgumentParser(prog="repoatlas",
                                 description="Turn a git repo's history into a fantasy world map.")
    ap.add_argument("repo", nargs="?", default=".", help="local path or git URL")
    ap.add_argument("-o", "--out", default="atlas.html", help="output HTML file")
    ap.add_argument("--json", action="store_true", help="also dump the raw data as atlas.json")
    ap.add_argument("--max-files", type=int, default=300)
    ap.add_argument("--version", action="version", version=__version__)
    a = ap.parse_args(argv)

    path = clone_if_url(a.repo)
    data = collect(path, max_files=a.max_files)
    tpl = (pathlib.Path(__file__).parent / "template.html").read_text(encoding="utf-8")
    payload = json.dumps(data).replace("</", "<\\/")
    pathlib.Path(a.out).write_text(tpl.replace("__DATA__", payload), encoding="utf-8")
    if a.json:
        pathlib.Path("atlas.json").write_text(json.dumps(data, indent=2))
    if path != a.repo:
        shutil.rmtree(path, ignore_errors=True)
    s = data["stats"]
    print(f"🗺️  {data['name']}: {s['files']} files, {s['commits']} commits -> {a.out}")


if __name__ == "__main__":
    sys.exit(main())
