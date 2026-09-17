# [H] GitPython: Arbitrary file overwrite via git diff --output argument injection in Diffable.diff (key- and value-controlled)

## Summary
Severity: High
Advisory: GHSA-fjr4-x663-mwxc
CWE: CWE-88
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-fjr4-x663-mwxc
Type: github-advisory

## Affected
- PyPI: `GitPython` — affected >=0 <3.1.54

## Details
## Summary
`Diffable.diff()` forwards `**kwargs` straight into `diff`/`diff_tree` with **no** `check_unsafe_options` guard. `Diffable` is mixed into `Commit`, `Tree`, `IndexFile`, and `Submodule`, giving a broad surface. `git diff --output=<path>` writes real patch content to an attacker-chosen path, enabling arbitrary file overwrite.

## Root Cause
`diff.py:188-283` builds and runs the diff command with no `check_unsafe_options` anywhere in the method (grep-confirmed). Additionally `diff.py:265` does `args.insert(0, other)`, placing the caller-supplied `other` ref BEFORE the `--` separator, so a value of `--output=/path` is parsed by git as an option — a value-only control path requiring no kwarg key.

## Impact
Overwrite/corrupt any file at process privilege with attacker-chosen path (e.g. `~/.ssh/authorized_keys`, configs, lockfiles). Content is real diff/patch bytes (attacker-influenced). Per the skill's rule, controlling WHICH file is overwritten = I:H regardless of content constraints.

## Proof of Concept
```python
# Key-control:
commit.diff(other_commit, output='/home/app/.ssh/authorized_keys')   # victim overwritten with diff (105 bytes verified)
# Value-control (attacker controls only the ref string):
commit.diff(other='--output=/home/app/.ssh/authorized_keys')          # 14-byte victim -> 146 bytes of diff-tree output
```

## Attack Chain
1. Entry (value-control): `commit.diff(other=<user ref>)` with `other = "--output=/home/app/.ssh/authorized_keys"`. Guard: none in `Diffable.diff`. Bypass proof: no `check_unsafe_options` in the method body (grep); `other` inserted pre-`--` at diff.py:265.
2. Sink: `git diff-tree <sha> --output=/home/app/.ssh/authorized_keys -r ...` -> git opens+truncates the target then writes diff content. Impact: overwrite/corrupt any file at process privilege (attacker chooses the path). Verified argv and victim overwrite live.

## Bypass Evidence
Live-verified on HEAD (tag 3.1.53): both key-control (`output=`) and value-control (`other='--output=...'`) overwrote a victim file with real diff-tree content; argv confirmed `['git','diff-tree','<sha>','--output=/victim','-r',...]`. This is the same value-control model GHSA-956x deemed fix-worthy for `iter_commits(rev='--output=')` — but `diff` is a distinct, unguarded sink NOT touched by that fix.

## Affected Versions
`<= 3.1.53`

## Suggested Fix
Add `check_unsafe_options` to `Diffable.diff` (mirroring `iter_commits`/`archive`), and/or place `--end-of-options` before the `other` ref so it cannot be parsed as an option.

---
Reported by **zx (Jace)** — GitHub: @manus-use

## References
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-fjr4-x663-mwxc
- https://github.com/gitpython-developers/GitPython/pull/2180
- https://github.com/gitpython-developers/GitPython/commit/1d51b891d7f236044a6aa17498ec682b63dad6e6
- https://github.com/gitpython-developers/GitPython
- https://github.com/gitpython-developers/GitPython/releases/tag/3.1.54
