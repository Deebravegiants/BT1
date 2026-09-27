# [H] GitPython: Unsafe git option guard bypass via single-character kwarg value token smuggling enables arbitrary command execution

## Summary
Severity: High
Advisory: GHSA-r9mr-m37c-5fr3
CWE: CWE-78, CWE-88
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-r9mr-m37c-5fr3
Type: github-advisory

## Affected
- PyPI: `GitPython` — affected >=0 <3.1.54

## Details
## Summary
GitPython's `check_unsafe_options` guard (the control introduced by CVE-2026-42215 / GHSA-2f96 and hardened since) can be bypassed for **every** guarded method (`clone`/`clone_from`, `fetch`/`pull`/`push`, `ls_remote`, `iter_commits`, `blame`, `archive`) by smuggling an option token inside the VALUE of a single-character kwarg. In the default `allow_unsafe_options=False` configuration this yields arbitrary command execution via `--upload-pack`.

## Root Cause
The guard builds its candidate option list from kwarg KEYS only: `_option_candidates([], {"n":"--upload-pack=<cmd>"})` returns `['-n']` (cmd.py:1042-1046 derives the candidate from the key, never the value). `-n` is not on the denylist, so `check_unsafe_options` passes. But `transform_kwarg('n', value, split_single_char_options=True)` (cmd.py:1600-1606) emits **two** argv tokens `['-n', '--upload-pack=<cmd>']`. git then parses the second token as `--upload-pack` and executes the attacker-supplied command. The guard never inspects the value that becomes a separate argv token.

## Impact
Arbitrary OS command execution as the host process (via `--upload-pack`) in the default configuration, affecting all guarded methods since they all build candidates through the name-only `_option_candidates`.

## Proof of Concept
```python
from git import Repo
Repo.clone_from(bare_repo, out_dir, n="--upload-pack=touch /tmp/ACE;git-upload-pack")
# /tmp/ACE created -> ACE. Direct-name form upload_pack="..." is correctly BLOCKED.
```
File-write variant on a guarded revision command: `iter_commits('HEAD', g='--output=/path')` -> candidate `['-g']` passes, argv `['-g','--output=/path']`, victim file truncated.

## Attack Chain
1. Entry: app forwards a user-supplied options dict -> `Repo.clone_from(url, path, n="--upload-pack=touch /tmp/ACE;git-upload-pack")`. Guard: `check_unsafe_options(options=_option_candidates([], kwargs), unsafe=unsafe_git_clone_options)` at base.py. Bypass proof: `_option_candidates([], {"n":"--upload-pack=..."})` -> `['-n']` (key-only), not on denylist -> no UnsafeOptionError (verified live).
2. Transform: `transform_kwarg('n', value, split_single_char_options=True)` -> `['-n', '--upload-pack=touch /tmp/ACE;git-upload-pack']`. Guard: none (guard already passed on name-only candidate). Bypass proof: verified transform emits two tokens.
3. Sink: `git clone -n --upload-pack='touch ...;git-upload-pack' -- <src> <dst>`; git parses and runs the second token. Impact: ACE (marker created, verified end-to-end).

## Bypass Evidence
Live-verified on HEAD (tag 3.1.53): `_option_candidates` returns key-only candidate `['-n']`; `transform_kwargs` emits the smuggled `--upload-pack=` token; clone_from with the payload created the marker file; the direct-name `upload_pack=` form raised UnsafeOptionError. All prior bypasses (GHSA-rpm5 underscore key, GHSA-2f96 long-option abbreviation, GHSA-v396 joined short option, GHSA-x2qx multi-before-split) are BLOCKED on HEAD — this is a distinct kwarg-value->separate-token vector.

## Affected Versions
`<= 3.1.53`

## Suggested Fix
Make `_option_candidates` also emit candidates derived from single-character kwarg VALUES when `split_single_char_options` is in effect, OR run `check_unsafe_options` over the fully-transformed argv rather than the reconstructed name-only candidate list.

---
Reported by **zx (Jace)** — GitHub: @manus-use

## References
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-r9mr-m37c-5fr3
- https://github.com/gitpython-developers/GitPython/pull/2180
- https://github.com/gitpython-developers/GitPython/commit/e8d0fbf774d1f6baa3b481adfe48bd262e43b453
- https://github.com/gitpython-developers/GitPython
- https://github.com/gitpython-developers/GitPython/releases/tag/3.1.54
