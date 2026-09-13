# [M] Soft Serve vulnerable to path traversal attacks

## Summary
Severity: Medium
Advisory: GHSA-j4jw-m6xr-fv6c
CVE: CVE-2025-22130
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-01-08
Source: https://github.com/advisories/GHSA-j4jw-m6xr-fv6c
Type: github-advisory

## Affected
- Go: `github.com/charmbracelet/soft-serve` — affected >=0 <0.8.2

## Details
### Impact

Path traversal attack gives access to existing non-admin users to access and take over other user's repositories. A malicious user then can modify, delete, and arbitrarily repositories as if they were an admin user without explicitly giving them permissions.

### Patches

This is patched in [v0.8.2](https://github.com/charmbracelet/soft-serve/releases/tag/v0.8.2)

### Workarounds

Single user set-ups are not affected. This only affects multi-user Soft Serve set-ups that enable repository creation for users. Otherwise, upgrading is necessary to circumvent the attack.

## References
- https://github.com/charmbracelet/soft-serve/security/advisories/GHSA-j4jw-m6xr-fv6c
- https://nvd.nist.gov/vuln/detail/CVE-2025-22130
- https://github.com/charmbracelet/soft-serve/commit/a8d1bf3f9349c138383b65079b7b8ad97fff78f4
- https://github.com/charmbracelet/soft-serve
- https://github.com/charmbracelet/soft-serve/releases/tag/v0.8.2
