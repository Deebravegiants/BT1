# [M] SFTPGo Vulnerable to Path Traversal and Permission Bypass via Path Normalization Discrepancy

## Summary
Severity: Medium
Advisory: GHSA-x8qh-7475-c5mp
CVE: CVE-2026-30914
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-x8qh-7475-c5mp
Type: github-advisory

## Affected
- Go: `github.com/drakkan/sftpgo/v2` — affected >=0 <2.7.1
- Go: `github.com/drakkan/sftpgo` — affected >=0

## Details
### Impact

In SFTPGo versions prior to 2.7.1, a path normalization discrepancy between the protocol handlers and the internal Virtual Filesystem routing can lead to an authorization bypass. An authenticated attacker can craft specific file paths to bypass folder-level permissions or escape the boundaries of a configured Virtual Folder.


### Patches

This issue has been addressed in SFTPGo version 2.7.1. The fix introduces strict edge-level path normalization, ensuring that all protocol inputs are fully sanitized and resolved to canonical POSIX paths before any routing or permission evaluations occur.

## References
- https://github.com/drakkan/sftpgo/security/advisories/GHSA-x8qh-7475-c5mp
- https://nvd.nist.gov/vuln/detail/CVE-2026-30914
- https://github.com/drakkan/sftpgo/commit/2f092d128917e2c059520a2ce3e22c3b5ea7ffd6
- https://github.com/drakkan/sftpgo
- https://pkg.go.dev/vuln/GO-2026-4699
