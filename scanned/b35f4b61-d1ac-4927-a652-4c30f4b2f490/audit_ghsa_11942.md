# [M] SFTPGo improperly sanitizes placeholders in group home directories/key prefixes

## Summary
Severity: Medium
Advisory: GHSA-m83q-5wr4-4gfp
CVE: CVE-2026-30915
CWE: CWE-20, CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-m83q-5wr4-4gfp
Type: github-advisory

## Affected
- Go: `github.com/drakkan/sftpgo/v2` — affected >=2.3.0 <2.7.1

## Details
### Impact

SFTPGo versions before v2.7.1 contain an input validation issue in the handling of dynamic group paths, for example, home directories or key prefixes.

When a group is configured with a dynamic home directory or key prefix using placeholders like `%username%`, the value replacing the placeholder is not strictly sanitized against relative path components. Consequently, if a user is created with a specially crafted username the resulting path may resolve to a parent directory instead of the intended sub-directory.

### Patches

This issue is fixed in version v2.7.1

## References
- https://github.com/drakkan/sftpgo/security/advisories/GHSA-m83q-5wr4-4gfp
- https://nvd.nist.gov/vuln/detail/CVE-2026-30915
- https://github.com/drakkan/sftpgo
- https://pkg.go.dev/vuln/GO-2026-4697
