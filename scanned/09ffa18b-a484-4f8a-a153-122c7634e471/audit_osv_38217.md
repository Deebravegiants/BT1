# [M] uutils coreutils install Arbitrary File Overwrite with -D via Path Component Symlink Race

## Summary
Severity: Medium
Advisory: CVE-2026-35356
Aliases: GHSA-gwm6-q8ch-hcfr
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-35356
Type: osv

## Details
A Time-of-Check to Time-of-Use (TOCTOU) vulnerability exists in the install utility of uutils coreutils when using the -D flag. The command creates parent directories and subsequently performs a second path resolution to create the target file, neither of which is anchored to a directory file descriptor. An attacker with concurrent write access can replace a path component with a symbolic link between these operations, redirecting the privileged write to an arbitrary file system location.

## References
- https://github.com/uutils
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35356.json
- https://github.com/uutils/coreutils/releases/tag/0.7.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-35356
- https://github.com/uutils/coreutils/pull/10140
- https://github.com/uutils/coreutils
