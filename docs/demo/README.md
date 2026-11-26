# The demo behind the README

`docs/media/session.svg` is one real session with this skill's scripts and `gh mrva`, recorded on
2026-11-26. This folder holds everything it was made from.

| File | What it is |
|---|---|
| [`pack/`](pack) | The demo query pack: [`NaiveUtcCalls.ql`](pack/NaiveUtcCalls.ql) finds every call to `datetime.utcnow()` or `datetime.utcfromtimestamp()`, both deprecated since Python 3.12. A harmless pattern, so the whole loop can run on real repositories without pointing at anyone's vulnerability. |
| [`databases.json`](databases.json) | The lists the run used and wrote: `py-top20`, `demo` (the 17 under 100 MB) and `hits` (the 3 with results). |
| [`session.json`](session.json) | The raw recording: each command, its complete output, exit code and wall time. |
| [`session.md`](session.md) | The same session as a readable transcript. |
| [`record.py`](record.py) | Runs one command and appends it to `session.json`. |
| [`render.py`](render.py) | Turns `session.json` into `docs/media/session.svg` and `session.md`. |

## Record it again

Work in a scratch folder that holds a copy of `skills/` and `docs/demo/pack/`, so the commands run
exactly as they are shown. Move the old `session.json` away first, then, from the repository root:

```bash
W=/path/to/scratch
python docs/demo/record.py $W 'python $S/mrva_list.py top --language python --limit 20 --name py-top20 --out databases.json'
python docs/demo/record.py $W 'python $S/mrva_dbs.py --file databases.json --list py-top20 --language python --max-db-mb 100 --write-list demo --out databases.json'
# ... one call per command, in the order of the session
python docs/demo/render.py
```

`render.py` picks lines from `session.json` by command index, so a new recording with the same ten
commands in the same order renders as is; anything else means editing its `SCREENS` table. A screen
holds 27 lines, and the script stops if one would overflow. On Windows, set `CODEQL_DIST` to the folder
that holds `codeql.exe` (gh-codeql's `dist/release/v<version>`), because `gh mrva` cannot run the
`codeql` shell wrapper.

The submit step runs a real variant analysis from your controller repository. On a public
controller its Actions logs are public, query name and per-repository result counts included, so
keep anything unpublished off it.
