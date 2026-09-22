# [M] tuf has platform-dependent delegation path matching

## Summary
Severity: Medium
Advisory: GHSA-qp9x-wp8f-qgjj
CWE: CWE-178
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-qp9x-wp8f-qgjj
Type: github-advisory

## Affected
- PyPI: `tuf` — affected >=0 <7.0.0

## Details
`DelegatedRole._is_target_in_pathpattern` uses `fnmatch.fnmatch` to decide whether a given target path is authorized by a delegation's glob pattern.

Python's `fnmatch.fnmatch` calls `os.path.normcase()` on both arguments before matching. On POSIX hosts `normcase` is the identity function; on Windows hosts `os.path` resolves to `ntpath`, whose `normcase` lowercases its input and replaces `/` with `\`.

As a result, python-tuf's delegation *path pattern* matching is case-sensitive on Linux/macOS but case-INSENSITIVE on Windows. This makes the authorization decision for a target dependent on the host operating system of the client running the updater.

The result on Windows is a TUF specification violation in the python-tuf `ngclient` implementation.

## Vulnerable code

`tuf/api/_payload.py` (HEAD `7ecb67d`):

```python
1183  @staticmethod
1184  def _is_target_in_pathpattern(targetpath: str, pathpattern: str) -> bool:
1185      """Determine whether ``targetpath`` matches the ``pathpattern``."""
1186      # We need to make sure that targetpath and pathpattern are pointing to
1187      # the same directory as fnmatch doesn't threat "/" as a special symbol.
1188      target_parts = targetpath.split("/")
1189      pattern_parts = pathpattern.split("/")
1190      if len(target_parts) != len(pattern_parts):
1191          return False
1192
1193      # Every part in the pathpattern could include a glob pattern, that's why
1194      # each of the target and pathpattern parts should match.
1195      for target, pattern in zip(target_parts, pattern_parts, strict=True):
1196          if not fnmatch.fnmatch(target, pattern):
1197              return False
1198      return True
```

`fnmatch.fnmatch` source (Python 3.12, unchanged in current mainline):

```python
def fnmatch(name, pat):
    ...
    name = os.path.normcase(name)
    pat = os.path.normcase(pat)
    return fnmatchcase(name, pat)
```

## Fix

Replace `fnmatch.fnmatch` with `fnmatch.fnmatchcase`, which is explicitly documented as "not applying case normalization", so it behaves identically across platforms.

## Attack

1. A TUF repository with two path-based delegations whose patterns differ only in case — for example, `Foo/*` and `foo/*`.
2. The "attacker" delegation is listed BEFORE the "legit" delegation in the delegation order.
3. The client searches for `foo/something`: on Windows, it will find the "attacker" provided target "Foo/something".


## Exploitability caveats 

* The attack needs a repository configuration with case-colliding delegation path patterns. The attacker must control one of the delegated roles.
* Delegation ordering matters: the attacker-controlled role must be visited BEFORE the legit role in the pre-order walk.
* The client must run on Windows. No effect on Linux/macOS.

## Credit

Reporter: Koda Reef @kodareef5 
Advisory edits: Jussi Kukkonen @jku

## References
- https://github.com/theupdateframework/python-tuf/security/advisories/GHSA-qp9x-wp8f-qgjj
- https://github.com/theupdateframework/python-tuf
- https://github.com/theupdateframework/python-tuf/releases/tag/v7.0.0
