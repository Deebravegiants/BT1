# [M] GitPython blind local file inclusion

## Summary
Severity: Medium
Advisory: GHSA-cwvm-v4w8-q58c
CVE: CVE-2023-41040
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-08-30
Source: https://github.com/advisories/GHSA-cwvm-v4w8-q58c
Type: github-advisory

## Affected
- PyPI: `GitPython` — affected >=0 <3.1.37

## Details
### Summary

In order to resolve some git references, GitPython reads files from the `.git` directory, in some places the name of the file being read is provided by the user, GitPython doesn't check if this file is located outside the `.git` directory. This allows an attacker to make GitPython read any file from the system.

### Details

This vulnerability is present in

https://github.com/gitpython-developers/GitPython/blob/1c8310d7cae144f74a671cbe17e51f63a830adbf/git/refs/symbolic.py#L174-L175

That code joins the base directory with a user given string without checking if the final path is located outside the base directory.

I was able to exploit it from three places, but there may be more code paths that lead to it:

https://github.com/gitpython-developers/GitPython/blob/1c8310d7cae144f74a671cbe17e51f63a830adbf/git/repo/base.py#L605

https://github.com/gitpython-developers/GitPython/blob/1c8310d7cae144f74a671cbe17e51f63a830adbf/git/repo/base.py#L620

https://github.com/gitpython-developers/GitPython/blob/1c8310d7cae144f74a671cbe17e51f63a830adbf/git/index/base.py#L1353

### PoC

Running GitPython within any repo should work, here is an example with the GitPython repo.

```python
import git

r = git.Repo(".")

# This will make GitPython read the README.md file from the root of the repo
r.commit("../README.md")
r.tree("../README.md")
r.index.diff("../README.md")

# Reading /etc/random
# WARNING: this will probably halt your system, run with caution
# r.commit("../../../../../../../../../dev/random")
```

### Impact

I wasn't able to show the contents of the files (that's why "blind" local file inclusion), depending on how GitPython is being used, this can be used by an attacker for something _inoffensive_ as checking if a file exits, or cause a DoS by making GitPython read a big/infinite file (like `/dev/random` on Linux systems).

### Possible solutions

A solution would be to check that the final path isn't located outside the `repodir` path (maybe even after resolving symlinks). Maybe there could be other checks in place to make sure that the reference names are valid.

## References
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-cwvm-v4w8-q58c
- https://nvd.nist.gov/vuln/detail/CVE-2023-41040
- https://github.com/gitpython-developers/GitPython/pull/1672
- https://github.com/gitpython-developers/GitPython/commit/74e55ee4544867e1bd976b7df5a45869ee397b0b
- https://github.com/gitpython-developers/GitPython/commit/e98f57b81f792f0f5e18d33ee658ae395f9aa3c4
- https://github.com/gitpython-developers/GitPython
- https://github.com/gitpython-developers/GitPython/blob/1c8310d7cae144f74a671cbe17e51f63a830adbf/git/refs/symbolic.py#L174-L175
- https://github.com/gitpython-developers/GitPython/releases/tag/3.1.37
- https://github.com/pypa/advisory-database/tree/main/vulns/gitpython/PYSEC-2023-165.yaml
- https://lists.debian.org/debian-lts-announce/2023/09/msg00036.html
- https://lists.debian.org/debian-lts-announce/2024/10/msg00030.html
