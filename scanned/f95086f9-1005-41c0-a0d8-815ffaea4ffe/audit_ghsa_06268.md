# [M] GitPython: Arbitrary file truncation via git rev-list --output argument injection in unguarded Commit.count

## Summary
Severity: Medium
Advisory: GHSA-p538-c434-8v24
CWE: CWE-88
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-p538-c434-8v24
Type: github-advisory

## Affected
- PyPI: `GitPython` — affected >=0 <3.1.56

## Details
## Summary
`Commit.count()` forwards `**kwargs` into `rev_list` with **no** `check_unsafe_options` guard (the guard exists only in the sibling `iter_items`, commit.py:341). `git rev-list --output=<path>` opens and truncates the target file to 0 bytes before revision parsing, so `count(output='/victim')` destroys/blanks an arbitrary file.

## Root Cause
`commit.py:290-291` calls `self.repo.git.rev_list(self.hexsha, **kwargs)` with no `check_unsafe_options` and no `allow_unsafe_options` parameter. The sibling `iter_items` (commit.py:341) is guarded; `count` is not. This is a distinct, uncovered sink — GHSA-956x-8gvw-wg5v fixed `iter_commits`/`blame`, not `count`.

## Impact
Destroy/blank an arbitrary file at process privilege (integrity/availability). Reachability is key-control only (`count` uses `self.hexsha`, not a user ref), and the write is a 0-byte truncation (no content control), so MEDIUM.

## Proof of Concept
```python
commit.count(output='/path/to/victim')   # victim truncated to 0 bytes (verified)
# control: commit.iter_commits(output=...) raises UnsafeOptionError
```

## Attack Chain
1. Entry: app forwards user options -> `commit.count(output='/victim')`. Guard: none. Bypass proof: `iter_commits(output=)` raises UnsafeOptionError; `count(output=)` does not — verified side-by-side.
2. Sink: `git rev-list <sha> --output=/victim` -> file truncated to 0 bytes. Impact: destroy/blank arbitrary file.

## Bypass Evidence
Live-verified on HEAD (tag 3.1.53): `count(output=<victim>)` truncated a pre-existing file to 0 bytes; guarded `iter_commits(output=)` raised UnsafeOptionError. Same CNA-accepted "app forwards user options dict" model as GHSA-956x-8gvw-wg5v's `archive(**kwargs)`. Uncovered sink, not a duplicate.

## Affected Versions
`<= 3.1.53`

## Suggested Fix
Add `check_unsafe_options` to `Commit.count` (mirroring `iter_items`).

---
Reported by **zx (Jace)** — GitHub: @manus-use

## References
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-p538-c434-8v24
- https://github.com/gitpython-developers/GitPython/pull/2184
- https://github.com/gitpython-developers/GitPython/commit/38553b6fddc7f6a667cdb45a6762343a08fc72b2
- https://github.com/gitpython-developers/GitPython
- https://github.com/gitpython-developers/GitPython/releases/tag/3.1.56
