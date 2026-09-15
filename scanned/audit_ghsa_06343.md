# [H] GitPython: Unguarded git option forwarding in Repo.init enables arbitrary command execution via --template clone hooks

## Summary
Severity: High
Advisory: GHSA-9rj7-rf2p-w77r
CWE: CWE-88, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-9rj7-rf2p-w77r
Type: github-advisory

## Affected
- PyPI: `GitPython` — affected >=0 <3.1.58

## Details
## Summary
`Repo.init()` forwards `**kwargs` verbatim to `git init` with no unsafe-option guard and no `allow_unsafe_options` parameter. `git init --template=<dir>` copies `<dir>/hooks/*` into the new repo's `.git/hooks`, so an attacker-controlled `template` kwarg plants a hook that executes on the next git operation → arbitrary code execution. `--template` is already recognized as unsafe for clone (it is on `unsafe_git_clone_options`, and GHSA-6p8h-3wgx-97gf covers the clone path), but `Repo.init` is a distinct method that never received a guard and needs an independent fix.

## Root Cause
`Repo.init(path, mkdir, odbt, expand_vars, **kwargs)` is a bare `git.init(**kwargs)` (git/repo/base.py:1435) with no `check_unsafe_options` and no `allow_unsafe_options`.

## Impact
Arbitrary code execution (hook fires on next git op) at the privileges of the host process. Two preconditions raise attack complexity (AC:H): the app must forward a `template=` kwarg (KEY control) AND the attacker must stage an executable hook directory at a known path — the same profile GHSA-6p8h-3wgx-97gf accepted as HIGH for the clone path. Default `allow_unsafe_options` is irrelevant here because `Repo.init` has no guard at all.

## Proof of Concept
```python
# attacker stages /evil/hooks/post-commit (executable)
from git import Repo
Repo.init(path, template="/evil")
# next commit runs /evil/hooks/post-commit -> ACE
```

## Attack Chain
1. Entry: attacker stages `/evil/hooks/post-commit` (executable) and gets the app to call `Repo.init(path, template='/evil')`.
2. Check: NONE on `Repo.init`. Bypass proof: base.py:1435 is a bare `git.init(**kwargs)`. argv (observed): `['git','init','--template=/evil']`.
3. Sink: git copies `/evil/hooks/post-commit` → `<repo>/.git/hooks/post-commit`.
4. Impact: next commit runs the hook → arbitrary code execution.

## Bypass Evidence
Independently reproduced (gate harness): `Repo.init(dst, template='<evil>')` → argv `['git','init','--template=<evil>']` unguarded; hook copied into `.git/hooks/post-commit`; after `git commit` the `INIT_ACE` marker was created. `--separate-git-dir=<path>` is a parallel arbitrary-redirect vector through the same unguarded sink (value control only).

## Affected Versions
`GitPython <= 3.1.57` (unguarded `git.init(**kwargs)` present verbatim on the latest release tag).

## Suggested Fix
Add a `check_unsafe_options` guard (with an `allow_unsafe_options` parameter) to `Repo.init`, consulting a denylist that includes `--template` and `--separate-git-dir` (path-taking / hook-installing options).

---
Reported by **zx (Jace)** — GitHub: @manus-use

## References
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-9rj7-rf2p-w77r
- https://github.com/gitpython-developers/GitPython/pull/2204
- https://github.com/gitpython-developers/GitPython/commit/d9ddb55bdc66
- https://github.com/gitpython-developers/GitPython
- https://github.com/gitpython-developers/GitPython/releases/tag/3.1.58
