# [M] uutils coreutils doesn't preserve file ownership during moves across different filesystem boundaries

## Summary
Severity: Medium
Advisory: GHSA-957r-r8gc-vv3h
CVE: CVE-2026-35351
CWE: CWE-281
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-957r-r8gc-vv3h
Type: github-advisory

## Affected
- crates.io: `coreutils` — affected >=0

## Details
The mv utility in uutils coreutils fails to preserve file ownership during moves across different filesystem boundaries. The utility falls back to a copy-and-delete routine that creates the destination file using the caller's UID/GID rather than the source's metadata. This flaw breaks backups and migrations, causing files moved by a privileged user (e.g., root) to become root-owned unexpectedly, which can lead to information disclosure or restricted access for the intended owners.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-35351
- https://github.com/uutils/coreutils/issues/9714
- https://github.com/uutils/coreutils
