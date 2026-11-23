"""Build the safari route page.

Reads data/route.json, data/spawns.json, data/landmarks.json and src/page.html, then writes:
  index.html         – full document for GitHub Pages (maps/ next to it)
  dist/artifact.html – the same page without <html>/<head>/<body> for a claude.ai artifact

Usage: python3 tools/build.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLACEHOLDER = "/*__DATA__*/null"
HEAD_END = "<!-- /head -->"


def main():
    route = json.loads((ROOT / "data/route.json").read_text(encoding="utf-8"))
    spawns = json.loads((ROOT / "data/spawns.json").read_text(encoding="utf-8"))
    landmarks = json.loads((ROOT / "data/landmarks.json").read_text(encoding="utf-8"))

    known = set(route["species"])
    for area in route["areas"]:
        for stop in area["stops"]:
            for key in stop["targets"] + stop.get("extra", []):
                if key not in known:
                    raise SystemExit(f"stop {stop['n']}: unknown species {key}")
    covered = {k for a in route["areas"] for s in a["stops"] for k in s["targets"]}
    if covered != known:
        raise SystemExit(f"species without a stop: {sorted(known - covered)}")

    data = dict(route)
    data["spawns"] = spawns
    data["landmarks"] = landmarks
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    page = (ROOT / "src/page.html").read_text(encoding="utf-8")
    if PLACEHOLDER not in page or HEAD_END not in page:
        raise SystemExit("src/page.html lost its placeholder or head marker")
    page = page.replace(PLACEHOLDER, blob)

    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    (dist / "artifact.html").write_text(page, encoding="utf-8")

    head, body = page.split(HEAD_END, 1)
    full = (
        "<!doctype html>\n<html lang=\"ru\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
        + head.strip() + "\n</head>\n<body>\n" + body.strip() + "\n</body>\n</html>\n"
    )
    (ROOT / "index.html").write_text(full, encoding="utf-8")
    print(f"ok: {len(covered)} species, {sum(len(a['stops']) for a in route['areas'])} stops, "
          f"index.html {len(full) // 1024} KB")


if __name__ == "__main__":
    main()
