"""Run one command exactly as shown and append it, with its real output, to session.json.

    python docs/demo/record.py WORKDIR "python $S/mrva_list.py top --language python --limit 20 ..."

The command runs in bash inside WORKDIR with S=skills/codeql-mrva/scripts, so WORKDIR needs a copy
of skills/ and docs/demo/pack/. Absolute paths are shortened before anything is saved: WORKDIR
becomes '.', the temporary folder '%TEMP%', the home folder '~'. On Windows, gh-mrva needs codeql.exe itself on PATH (not a
shell wrapper): set CODEQL_DIST to the folder that holds it. Standard library only.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

CAST = Path(__file__).resolve().parent / "session.json"


def bash():
    git_bash = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Git" / "usr" / "bin" / "bash.exe"
    return str(git_bash) if os.name == "nt" and git_bash.exists() else shutil.which("bash")


def shorten(text, workdir):
    home = str(Path.home())
    for p in (workdir, workdir.replace("\\", "/")):
        text = text.replace(p + "\\", "").replace(p + "/", "").replace(p, ".")
    text = re.sub(r"query-pack-\d+", "query-pack-NNN", text)
    temp = tempfile.gettempdir()
    for p in (temp, temp.replace("\\", "/")):
        text = text.replace(p, "%TEMP%")
    for p in (home, home.replace("\\", "/")):
        text = text.replace(p, "~")
    return text


def main():
    workdir, cmd = str(Path(sys.argv[1]).resolve()), sys.argv[2]
    env = dict(os.environ, S="skills/codeql-mrva/scripts", PYTHONIOENCODING="utf-8", NO_COLOR="1")
    if os.environ.get("CODEQL_DIST"):
        env["PATH"] = os.environ["CODEQL_DIST"] + os.pathsep + env["PATH"]
    t0 = time.time()
    p = subprocess.run([bash(), "-lc", cmd], cwd=workdir, env=env, capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    secs = round(time.time() - t0, 1)
    out = shorten((p.stdout or "") + (p.stderr or ""), workdir)
    print(out, f"\n[exit {p.returncode}, {secs} s]", sep="")
    cast = json.loads(CAST.read_text(encoding="utf-8")) if CAST.exists() else []
    cast.append({"cmd": shorten(cmd, workdir), "out": out, "exit": p.returncode, "secs": secs,
                 "at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    CAST.write_text(json.dumps(cast, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
