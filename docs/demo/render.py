"""Render the recorded session (session.json) as an animated terminal SVG and a Markdown transcript.

    python docs/demo/render.py

Writes docs/media/session.svg and docs/demo/session.md. Every line shown is real output
from session.json; lines left out are replaced by a dim "... N lines" marker, blank lines are
dropped, and long lines are cut at the right edge of the window. Standard library only.
"""
import html
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAST = json.loads((HERE / "session.json").read_text(encoding="utf-8"))
SVG_OUT = HERE.parent / "media" / "session.svg"
MD_OUT = HERE / "session.md"

W, H = 1280, 720
X, Y0, LH, FS, CW = 36, 96, 22, 16, 9.92    # CW: generous monospace advance, for the typing clip
TYPE_CPS, LINE_DT = 60.0, 0.035             # typing speed, delay between output lines
INK, DIM, MUTED = "#e6e6ee", "#6e6f80", "#a3a4b5"
TEAL, AMBER, GREEN = "#4fd1c5", "#f5a524", "#4ade80"

# One screen per step. cmd: how the command is shown (wrapped with a trailing backslash);
# keep: regexes for the output lines to show (None = all); color: (regex, colour) per line.
SCREENS = [
    {"step": "1/4  build the list",
     "cmds": [
         {"i": 0, "show": ["python $S/mrva_list.py top --language python --limit 20 --name py-top20 --out databases.json"]},
         {"i": 1, "show": ["python $S/mrva_dbs.py --file databases.json --list py-top20 --language python \\",
                           "    --max-db-mb 100 --write-list demo --out databases.json"],
          "color": [(r"\b(336|393|289)\.\dMB", AMBER), (r"^wrote ", GREEN)]},
     ], "hold": 4.5},
    {"step": "2/4  test on one database",
     "cmds": [
         {"i": 2, "show": ["codeql pack install docs/demo/pack"],
          "keep": [r"python-all", r"^Dependencies resolved"]},
         {"i": 3, "show": ["python $S/mrva_dbs.py AUTOMATIC1111/stable-diffusion-webui --language python --download dbs/ --extract"]},
         {"i": 4, "show": ["codeql database analyze dbs/AUTOMATIC1111__stable-diffusion-webui__python \\",
                           "    docs/demo/pack/NaiveUtcCalls.ql --format=sarif-latest --output=one.sarif"],
          "keep": [r"^Running queries", r"Evaluation done", r"^Interpreting results"]},
         {"i": 5, "show": ["python $S/mrva_sarif.py one.sarif"],
          "keep": [r"^- SARIF files", (r"^\| location", None)],
          "color": [(r"\.py:\d+ \|", AMBER)]},
     ], "hold": 4.5},
    {"step": "3/4  submit, wait, check",
     "cmds": [
         {"i": 6, "show": ["gh mrva submit --language python --session readme-demo --list demo \\",
                           "    --list-file databases.json --query docs/demo/pack/NaiveUtcCalls.ql"],
          "keep": [r"^Resolving demo", r"^Submitting", r"^Generating query pack", r"^Compiling and bundling",
                   r"^Generated encoded bundle", r"^Done!"],
          "color": [(r"^Done!", GREEN)],
          "after": "4 min 33 s later: 17 jobs finished on the controller repository"},
         {"i": 7, "show": ["gh mrva status --session readme-demo"],
          "color": [(r"^Status: succeeded", GREEN), (r"with findings: [1-9]|^Total findings: [1-9]|^  \S+ \(py/", AMBER)]},
     ], "hold": 5.0},
    {"step": "4/4  download and triage",
     "cmds": [
         {"i": 8, "show": ["gh mrva download --session readme-demo --output-dir results/readme-demo"],
          "keep": [r"^Downloading artifacts for", r"artifacts downloaded"]},
         {"i": 9, "show": ["python $S/mrva_sarif.py results/readme-demo --repo-list hits --out databases.json"],
          "keep": [r"^# MRVA triage", r"^- SARIF files", (r"^## Repositories", r"^## Rules"),
                   (r"^### NousResearch", r"^###"), r"^wrote hits"],
          "color": [(r"^\| \S+/\S+ \| \d+ \||\.py:\d+ \|", AMBER), (r"^wrote ", GREEN), (r"^#", TEAL)]},
     ], "hold": 6.0},
]


def output_lines(cmd):
    """Real output of a cast entry, filtered: list of (text, colour) with elision markers."""
    lines = [l.rstrip() for l in CAST[cmd["i"]]["out"].splitlines()]
    lines = [l for l in lines if l.strip()]
    keep, colors, out, skipped = cmd.get("keep"), cmd.get("color", []), [], 0
    spans = [k for k in (keep or []) if isinstance(k, tuple)]   # (start, stop): keep a whole block
    inside = None
    for line in lines:
        if inside and inside[1] and re.search(inside[1], line):
            inside = None
        if inside is None:
            inside = next((s for s in spans if re.search(s[0], line)), None)
        if keep and inside is None and not any(re.search(k, line) for k in keep if isinstance(k, str)):
            skipped += 1
            continue
        if skipped:
            out.append((f"⋯ {skipped} line{'s' if skipped > 1 else ''}", DIM))
            skipped = 0
        col = next((c for rx, c in colors if re.search(rx, line)), INK)
        out.append((line, col))
    if skipped:
        out.append((f"⋯ {skipped} line{'s' if skipped > 1 else ''}", DIM))
    if cmd.get("after"):
        out.append((f"⋯ {cmd['after']}", DIM))
    return out


def esc(s):
    return html.escape(s, quote=False)


def k(t, total):
    return f"{t / total:.4f}".rstrip("0").rstrip(".") if 0 < t < total else ("0" if t <= 0 else "1")


# --- timeline -------------------------------------------------------------------------------
items, t = [], 0.0          # items: dicts with kind, screen, t_on, ...
spans = []                  # (t_start, t_end) per screen
for si, sc in enumerate(SCREENS):
    start, row = t, 0
    t += 0.4
    for cmd in sc["cmds"]:
        for j, shown in enumerate(cmd["show"]):
            text = ("$ " if j == 0 else "  ") + shown
            dur = len(shown) / TYPE_CPS
            items.append({"kind": "cmd", "screen": si, "row": row, "text": text, "t0": t, "t1": t + dur})
            t += dur + 0.05
            row += 1
        t += 0.35
        for text, col in output_lines(cmd):
            items.append({"kind": "out", "screen": si, "row": row, "text": text, "col": col, "t0": t})
            t += LINE_DT
            row += 1
        t += 0.9
    t += sc["hold"]
    spans.append((start, t))
    assert row <= 27, f"screen {si + 1} has {row} rows; the window holds 27"
TOTAL = round(t, 2)


def visible(t_on, t_off):
    if t_off >= TOTAL:
        return (f'<animate attributeName="opacity" dur="{TOTAL}s" repeatCount="indefinite" calcMode="discrete" '
                f'values="0;1" keyTimes="0;{k(t_on, TOTAL)}"/>')
    return (f'<animate attributeName="opacity" dur="{TOTAL}s" repeatCount="indefinite" calcMode="discrete" '
            f'values="0;1;0" keyTimes="0;{k(t_on, TOTAL)};{k(t_off, TOTAL)}"/>')


# --- svg ------------------------------------------------------------------------------------
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" viewBox="0 0 {W} {H}" role="img" aria-labelledby="st sd">',
       '<title id="st">codeql-mrva: a real session</title>',
       '<desc id="sd">A real terminal session with the codeql-mrva scripts, recorded on 2026-11-26. It builds a list of '
       'the top 20 Python repositories, keeps the 17 whose CodeQL database is under 100 MB, tests a demo query that '
       'finds deprecated datetime.utcnow() and utcfromtimestamp() calls on one database (3 results in '
       'stable-diffusion-webui), submits it with gh mrva to 17 repositories, and after 4 minutes 33 seconds gets 11 '
       'results in 3 repositories, which mrva_sarif.py turns into a triage table and a hits list.</desc>',
       '<style>text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;'
       f'font-size:{FS}px;white-space:pre}}.u{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}</style>',
       '<defs><clipPath id="body"><rect x="20" y="58" width="1240" height="650"/></clipPath>']
for n, it in enumerate(i for i in items if i["kind"] == "cmd"):
    it["clip"] = f"c{n}"
    y = Y0 + it["row"] * LH
    full = len(it["text"]) * CW + 6
    svg.append(f'<clipPath id="c{n}"><rect x="{X}" y="{y - 17}" height="{LH}" width="0">'
               f'<animate attributeName="width" dur="{TOTAL}s" repeatCount="indefinite" '
               f'values="{2 * CW:.0f};{2 * CW:.0f};{full:.0f};{full:.0f}" '
               f'keyTimes="0;{k(it["t0"], TOTAL)};{k(it["t1"], TOTAL)};1"/></rect></clipPath>')
svg.append('</defs>')
svg.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="24" fill="#16161d" stroke="#ffffff" stroke-opacity=".1" stroke-width="2"/>')
svg.append('<path d="M2 56H1278" stroke="#ffffff" stroke-opacity=".08" stroke-width="2"/>')
svg.append('<circle cx="34" cy="29" r="7" fill="#3a3a48"/><circle cx="58" cy="29" r="7" fill="#3a3a48"/><circle cx="82" cy="29" r="7" fill="#3a3a48"/>')
svg.append(f'<text class="u" x="640" y="35" font-size="17" fill="{MUTED}" text-anchor="middle">codeql-mrva, a real session (2026-11-26)</text>')
for si, sc in enumerate(SCREENS):
    a, b = spans[si]
    svg.append(f'<text class="u" x="1248" y="35" font-size="17" font-weight="600" fill="{TEAL}" text-anchor="end" opacity="0">'
               f'{esc(sc["step"])}{visible(a, b)}</text>')
for si in range(len(SCREENS)):
    a, b = spans[si]
    svg.append(f'<g clip-path="url(#body)" opacity="0">{visible(a, b)}')
    for it in (i for i in items if i["screen"] == si):
        y = Y0 + it["row"] * LH
        if it["kind"] == "cmd":
            prompt, rest = it["text"][:2], it["text"][2:]
            svg.append(f'<text x="{X}" y="{y}" clip-path="url(#{it["clip"]})"><tspan fill="{TEAL}">{esc(prompt)}</tspan>'
                       f'<tspan fill="{INK}" font-weight="600">{esc(rest)}</tspan></text>')
        else:
            style = ' font-style="italic"' if it["col"] == DIM else ""
            svg.append(f'<text x="{X}" y="{y}" fill="{it["col"]}"{style} opacity="0">{esc(it["text"])}{visible(it["t0"], TOTAL)}</text>')
    svg.append('</g>')
svg.append('</svg>')
SVG_OUT.write_text("\n".join(svg) + "\n", encoding="utf-8", newline="\n")

# --- markdown transcript --------------------------------------------------------------------
md = ["# The recorded session, in full", "",
      "Every command behind [`docs/media/session.svg`](../media/session.svg), with its complete output, as recorded on",
      "2026-11-26 on Windows (Git Bash, Python 3.14, CodeQL 2.27.3, gh-mrva 1.0.8) with",
      "`S=skills/codeql-mrva/scripts`. Absolute paths are shortened: the working folder to `.`, the temporary",
      "folder to `%TEMP%`, the home folder to `~`; nothing else is changed. The animation shows the same lines",
      "with some left out.", "",
      "The query is [`pack/NaiveUtcCalls.ql`](pack/NaiveUtcCalls.ql): every call to `datetime.utcnow()` or",
      "`datetime.utcfromtimestamp()`, both deprecated since Python 3.12. It is a harmless pattern, chosen so the",
      "whole loop can be shown on real repositories without pointing at anyone's vulnerability. The lists the",
      "run used and produced are in [`databases.json`](databases.json).", ""]
for e in CAST:
    md += ["```console", f"$ {e['cmd']}", e["out"].rstrip("\n"), "```", "",
           f"<sub>exit {e['exit']}, {e['secs']} s</sub>", ""]
MD_OUT.write_text("\n".join(md), encoding="utf-8", newline="\n")
print(f"{SVG_OUT.name}: {TOTAL}s loop, {SVG_OUT.stat().st_size} bytes; {MD_OUT.name}: {len(CAST)} commands")
