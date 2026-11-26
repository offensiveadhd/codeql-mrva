# The recorded session, in full

Every command behind [`docs/media/session.svg`](../media/session.svg), with its complete output, as recorded on
2026-11-26 on Windows (Git Bash, Python 3.14, CodeQL 2.27.3, gh-mrva 1.0.8) with
`S=skills/codeql-mrva/scripts`. Absolute paths are shortened: the working folder to `.`, the temporary
folder to `%TEMP%`, the home folder to `~`; nothing else is changed. The animation shows the same lines
with some left out.

The query is [`pack/NaiveUtcCalls.ql`](pack/NaiveUtcCalls.ql): every call to `datetime.utcnow()` or
`datetime.utcfromtimestamp()`, both deprecated since Python 3.12. It is a harmless pattern, chosen so the
whole loop can be shown on real repositories without pointing at anyone's vulnerability. The lists the
run used and produced are in [`databases.json`](databases.json).

```console
$ python $S/mrva_list.py top --language python --limit 20 --name py-top20 --out databases.json
wrote py-top20: 20 repositories -> databases.json (gh-mrva)
```

<sub>exit 0, 2.6 s</sub>

```console
$ python $S/mrva_dbs.py --file databases.json --list py-top20 --language python --max-db-mb 100 --write-list demo --out databases.json
repository                                  python     stars     size    age  commit
public-apis/public-apis                     yes       501431    0.2MB     0d  9fb3bdb62643
EbookFoundation/free-programming-books      yes       402285    0.2MB    12d  10e33dd516cc
donnemartin/system-design-primer            yes       379238    0.1MB    71d  ae9bbd7b02d9
vinta/awesome-python                        yes       337136    4.4MB     7d  4c3cb15dc695
practical-tutorials/project-based-learning  yes       290488    0.2MB     3d  f99ea242247b
NousResearch/hermes-agent                   yes       266094   66.1MB   180d  5e7c2ffa9ff5
TheAlgorithms/Python                        yes       226466    6.1MB     8d  30507bbe4139
yt-dlp/yt-dlp                               yes       210708   69.0MB     1d  da452a569fb3
anthropics/skills                           yes       200485    1.2MB     5d  e4bb5d960d87
microsoft/markitdown                        yes       198455    8.2MB     3d  ed178952a667
521xueweihan/HelloGitHub                    yes       191248    0.1MB    21d  d65699c2892f
Significant-Gravitas/AutoGPT                yes       188190  336.1MB     3d  dd0b5f73266e
huggingface/transformers                    yes       169322   74.2MB     1d  d8f10a82213a
AUTOMATIC1111/stable-diffusion-webui        yes       165381    2.9MB   267d  82a973c04367
langgenius/dify                             yes       161900  393.2MB     0d  fce5d308298f
langflow-ai/langflow                        yes       156943  289.9MB     1d  6c9aea6f5d5f
nextlevelbuilder/ui-ux-pro-max-skill        yes       154177    1.7MB     5d  2de1134dc4d1
Graphify-Labs/graphify                      yes       153350   16.5MB     1d  013a6461c31d
github/spec-kit                             yes       151373   20.8MB     0d  f2010547121b
langchain-ai/langchain                      yes       149992   23.2MB     0d  a2d98c255a70
20/20 repositories have a python database; 17 selected after --min-stars/--max-db-mb/--top and rename resolution
wrote demo: 17 repositories -> databases.json (gh-mrva)
```

<sub>exit 0, 4.5 s</sub>

```console
$ codeql pack install docs/demo/pack
Package install location: ~\.codeql\packages
Installed fresh codeql/concepts@0.0.37 (library)
Installed fresh codeql/controlflow@2.0.47 (library)
Installed fresh codeql/dataflow@2.1.19 (library)
Installed fresh codeql/mad@1.0.63 (library)
Installed fresh codeql/python-all@7.2.11 (library)
Installed fresh codeql/regex@1.0.63 (library)
Installed fresh codeql/ssa@2.0.39 (library)
Installed fresh codeql/threat-models@1.1.3 (library)
Installed fresh codeql/tutorial@1.0.63 (library)
Installed fresh codeql/typetracking@2.0.47 (library)
Installed fresh codeql/util@2.0.50 (library)
Installed fresh codeql/xml@1.0.63 (library)
Installed fresh codeql/yaml@1.0.63 (library)
Dependencies resolved. Installing packages...
Install location: ~\.codeql\packages
```

<sub>exit 0, 19.9 s</sub>

```console
$ python $S/mrva_dbs.py AUTOMATIC1111/stable-diffusion-webui --language python --download dbs/ --extract
repository                            python     stars     size    age  commit
AUTOMATIC1111/stable-diffusion-webui  yes       165381    2.9MB   267d  82a973c04367
1/1 repositories have a python database
AUTOMATIC1111/stable-diffusion-webui: dbs\AUTOMATIC1111__stable-diffusion-webui__python
```

<sub>exit 0, 5.1 s</sub>

```console
$ codeql database analyze dbs/AUTOMATIC1111__stable-diffusion-webui__python docs/demo/pack/NaiveUtcCalls.ql --format=sarif-latest --output=one.sarif
Running queries.
Resolving data extensions.
Finished resolving data extensions.
Merging data extensions.
Finished merging data extensions.
WARNING: Not caching stages during query-loading, since max heap size is only 1800 MB.
Compiling query plan for docs\demo\pack\NaiveUtcCalls.ql.
[1/1] Found in cache: docs\demo\pack\NaiveUtcCalls.ql.
Starting evaluation of offensiveadhd\mrva-demo\NaiveUtcCalls.ql.
[1/1 eval 19.2s] Evaluation done; writing results to offensiveadhd\mrva-demo\NaiveUtcCalls.bqrs.
Shutting down query evaluator.
Interpreting results.
```

<sub>exit 0, 27.3 s</sub>

```console
$ python $S/mrva_sarif.py one.sarif
# MRVA triage

- SARIF files: 1 with findings, repositories analysed: 1, with findings: 1, findings: 3

## Repositories

| repository | findings | rules |
|---|---:|---|
| one | 3 | py/demo/naive-utc-datetime |

## Rules

| rule | findings | repositories |
|---|---:|---:|
| py/demo/naive-utc-datetime | 3 | 1 |

## Findings

### one (3)

| location | rule | level | path | message |
|---|---|---|---:|---|
| extensions-builtin/Lora/ui_edit_user_metadata.py:89 | py/demo/naive-utc-datetime | note |  | datetime.utcfromtimestamp() is deprecated since Python 3.12. |
| modules/launch_utils.py:477 | py/demo/naive-utc-datetime | note |  | datetime.utcnow() is deprecated since Python 3.12. |
| modules/ui.py:1227 | py/demo/naive-utc-datetime | note |  | datetime.utcnow() is deprecated since Python 3.12. |
```

<sub>exit 0, 0.7 s</sub>

```console
$ gh mrva submit --language python --session readme-demo --list demo --list-file databases.json --query docs/demo/pack/NaiveUtcCalls.ql
Resolving demo repositories from databases.json
Submitting 1 queries for 17 repositories
Generating query pack for docs/demo/pack/NaiveUtcCalls.ql
Resolving query id for docs\demo\pack\NaiveUtcCalls.ql
Metadata: {
  "name" : "Naive UTC datetime calls",
  "description" : "Every call to datetime.utcnow() or datetime.utcfromtimestamp(). Both are deprecated since Python 3.12 and return a naive datetime. The demo query for the README recording: a harmless pattern, so the whole MRVA loop can be shown on real repositories.",
  "kind" : "problem",
  "problem.severity" : "recommendation",
  "precision" : "high",
  "id" : "py/demo/naive-utc-datetime",
  "tags" : "maintainability"
}

QLPack exists, stripping all other queries from docs\demo\pack
Preparing stripped QLPack in %TEMP%\query-pack-NNN
Fixing QLPack in %TEMP%\query-pack-NNN
Installing QLPack dependencies
Compiling and bundling the QLPack (This may take a while)
Generated encoded bundle for docs/demo/pack/NaiveUtcCalls.ql (py/demo/naive-utc-datetime)
Done!
```

<sub>exit 0, 143.5 s</sub>

```console
$ gh mrva status --session readme-demo
Run name: readme-demo
Status: succeeded
Total runs: 1
Total successful scans: 17
Total failed scans: 0
Total skipped repositories: 0
Total skipped repositories due to access mismatch: 0
Total skipped repositories due to not found: 0
Total skipped repositories due to no database: 0
Total skipped repositories due to over limit: 0
Total repositories with findings: 3
Total findings: 11
Repositories with findings:
  huggingface/transformers (py/demo/naive-utc-datetime): 4
  AUTOMATIC1111/stable-diffusion-webui (py/demo/naive-utc-datetime): 3
  NousResearch/hermes-agent (py/demo/naive-utc-datetime): 4
```

<sub>exit 0, 1.9 s</sub>

```console
$ gh mrva download --session readme-demo --output-dir results/readme-demo
Downloading artifacts for huggingface_transformers_29410
Downloading artifacts for AUTOMATIC1111_stable-diffusion-webui_29410
Downloading artifacts for NousResearch_hermes-agent_29410
Downloaded [results\readme-demo\AUTOMATIC1111_stable-diffusion-webui_29410.sarif results\readme-demo\AUTOMATIC1111_stable-diffusion-webui_29410.bqrs]
Downloaded artifact for AUTOMATIC1111/stable-diffusion-webui (1/3)
Downloaded [results\readme-demo\NousResearch_hermes-agent_29410.sarif results\readme-demo\NousResearch_hermes-agent_29410.bqrs]
Downloaded artifact for NousResearch/hermes-agent (2/3)
Downloaded [results\readme-demo\huggingface_transformers_29410.sarif results\readme-demo\huggingface_transformers_29410.bqrs]
Downloaded artifact for huggingface/transformers (3/3)
3 artifacts downloaded
```

<sub>exit 0, 4.4 s</sub>

```console
$ python $S/mrva_sarif.py results/readme-demo --repo-list hits --out databases.json
# MRVA triage

- SARIF files: 3 with findings, repositories analysed: 3, with findings: 3, findings: 11

## Repositories

| repository | findings | rules |
|---|---:|---|
| huggingface/transformers | 4 | py/demo/naive-utc-datetime |
| NousResearch/hermes-agent | 4 | py/demo/naive-utc-datetime |
| AUTOMATIC1111/stable-diffusion-webui | 3 | py/demo/naive-utc-datetime |

## Rules

| rule | findings | repositories |
|---|---:|---:|
| py/demo/naive-utc-datetime | 11 | 3 |

## Findings

### huggingface/transformers (4)

| location | rule | level | path | message |
|---|---|---|---:|---|
| scripts/stale.py:48 | py/demo/naive-utc-datetime | note |  | datetime.utcnow() is deprecated since Python 3.12. |
| scripts/stale.py:49 | py/demo/naive-utc-datetime | note |  | datetime.utcnow() is deprecated since Python 3.12. |
| scripts/stale.py:58 | py/demo/naive-utc-datetime | note |  | datetime.utcnow() is deprecated since Python 3.12. |
| scripts/stale.py:59 | py/demo/naive-utc-datetime | note |  | datetime.utcnow() is deprecated since Python 3.12. |

### NousResearch/hermes-agent (4)

| location | rule | level | path | message |
|---|---|---|---:|---|
| gateway/platforms/bluebubbles.py:396 | py/demo/naive-utc-datetime | note |  | datetime.utcnow() is deprecated since Python 3.12. |
| gateway/platforms/bluebubbles.py:452 | py/demo/naive-utc-datetime | note |  | datetime.utcnow() is deprecated since Python 3.12. |
| optional-skills/blockchain/hyperliquid/scripts/hyperliquid_client.py:174 | py/demo/naive-utc-datetime | note |  | datetime.utcfromtimestamp() is deprecated since Python 3.12. |
| tui_gateway/server.py:3195 | py/demo/naive-utc-datetime | note |  | datetime.utcfromtimestamp() is deprecated since Python 3.12. |

### AUTOMATIC1111/stable-diffusion-webui (3)

| location | rule | level | path | message |
|---|---|---|---:|---|
| extensions-builtin/Lora/ui_edit_user_metadata.py:89 | py/demo/naive-utc-datetime | note |  | datetime.utcfromtimestamp() is deprecated since Python 3.12. |
| modules/launch_utils.py:477 | py/demo/naive-utc-datetime | note |  | datetime.utcnow() is deprecated since Python 3.12. |
| modules/ui.py:1227 | py/demo/naive-utc-datetime | note |  | datetime.utcnow() is deprecated since Python 3.12. |
wrote hits: 3 repositories -> databases.json (gh-mrva)
```

<sub>exit 0, 1.4 s</sub>
