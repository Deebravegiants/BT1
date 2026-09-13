# [M] uutils coreutils has a UNIX Symbolic Link (Symlink) Following issue

## Summary
Severity: Medium
Advisory: GHSA-wq63-vh5h-pr5p
CVE: CVE-2026-35372
CWE: CWE-61
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-wq63-vh5h-pr5p
Type: github-advisory

## Affected
- crates.io: `coreutils` — affected >=0 <0.8.0

## Details
A logic error in the ln utility of uutils coreutils allows the utility to dereference a symbolic link target even when the --no-dereference (or -n) flag is explicitly provided. The implementation previously only honored the "no-dereference" intent if the --force (overwrite) mode was also enabled. This flaw causes ln to follow a symbolic link that points to a directory and create new links inside that target directory instead of treating the symbolic link itself as the destination. In environments where a privileged user or system script uses ln -n to update a symlink, a local attacker could manipulate existing symbolic links to redirect file creation into sensitive directories, potentially leading to unauthorized file creation or system misconfiguration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-35372
- https://github.com/uutils/coreutils/pull/11253
- https://github.com/uutils/coreutils/commit/394c4b17f2f382b4be9f54389bcb79028de02f39
- https://github.com/uutils/coreutils
- https://github.com/uutils/coreutils/releases/tag/0.8.0
