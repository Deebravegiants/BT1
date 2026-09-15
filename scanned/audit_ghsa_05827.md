# [H] GitPython: Unguarded git read-tree option forwarding in IndexFile.from_tree/reset/merge_tree enables arbitrary file overwrite

## Summary
Severity: High
Advisory: GHSA-4gmw-gg2m-w46p
CWE: CWE-88
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-4gmw-gg2m-w46p
Type: github-advisory

## Affected
- PyPI: `GitPython` — affected >=0 <3.1.58

## Details
## Summary
`IndexFile.from_tree`, `IndexFile.reset` (→ from_tree) and `IndexFile.merge_tree` append caller-influenced treeish strings positionally to `git read-tree` with no unsafe-option guard, no `allow_unsafe_options` parameter, and no `--` separator. `git read-tree --index-output=<file>` writes the resulting index to an arbitrary path, and last-occurrence-wins lets an injected `--index-output` override the method's internal temp path — clobbering an arbitrary file with a valid git-index blob. This is a distinct, never-guarded sink: commit `3af0c251` (GHSA-3f7w-8rr8-f37f) guarded only `checkout_index` and `tag`; `read_tree` was left unprotected (it is among the acknowledged unguarded call sites in that advisory's sweep but was never reported or fixed).

## Root Cause
`from_tree` (index/base.py:388), `reset` (delegates to from_tree), and `merge_tree` (index/base.py:291) call `repo.git.read_tree(*arg_list)` with no `check_unsafe_options` and no `--`. The treeish is caller-influenced and positional.

## Impact
Arbitrary file overwrite / destruction at the privileges of the host process. Content is constrained to a git-index blob (not attacker-chosen, so not RCE), but the target path is fully attacker-controlled — corrupting/truncating configs or destroying files at attacker-chosen writable locations = I:H + A:H (per the skill's "overwrite-any-path = I:H" rule). Pure VALUE control (positional treeish). Default configuration.

## Proof of Concept
```python
IndexFile.from_tree(repo, "--index-output=/home/victim/.bashrc")
# target overwritten with a valid git-index blob (DIRC...)
```

## Attack Chain
1. Entry: app calls `IndexFile.from_tree(repo, treeish)` / `reset(commit=…)` / `merge_tree(base=…, rhs=…)` with attacker `treeish="--index-output=/home/victim/.bashrc"`.
2. Check: NONE — the methods have no `allow_unsafe_options` and never call `check_unsafe_options`.
3. Sink: `repo.git.read_tree(*arg_list)` — no `--`. argv (from_tree, observed): `['git','read-tree','--index-output=<tmp>','--index-output=/…/victim']` (last-wins).
4. Impact: target path created/overwritten with a valid git-index blob; existing content destroyed.

## Bypass Evidence
Independently reproduced (gate harness): `IndexFile.from_tree(repo,'--index-output=<victim>')` → victim overwritten; before=`IMPORTANT ORIGINAL CONTENT`, after starts `DIRC\x00\x00\x00\x02…` (destructive clobber, valid index blob). `reset(commit=…)` and both `merge_tree` positionals verified. Fix-commit read: `3af0c251` touched only `checkout_index`+`tag`; `read_tree` untouched on HEAD.

## Affected Versions
`GitPython <= 3.1.57` (sinks present verbatim on the latest release tag).

## Suggested Fix
Add a `check_unsafe_options` guard (with an `allow_unsafe_options` parameter) to `from_tree`/`reset`/`merge_tree`, and/or place a `--` separator before the positional treeish arguments; block `--index-output` (a path-taking option) on this sink.

---
Reported by **zx (Jace)** — GitHub: @manus-use

## References
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-4gmw-gg2m-w46p
- https://github.com/gitpython-developers/GitPython/pull/2204
- https://github.com/gitpython-developers/GitPython/commit/9b5dcaf85da5946dbf69dcd53f9edba08f760b32
- https://github.com/gitpython-developers/GitPython
- https://github.com/gitpython-developers/GitPython/releases/tag/3.1.58
