# [M] Gokapi has stored XSS vulnerability in friendly name for API keys

## Summary
Severity: Medium
Advisory: GHSA-4xg4-54hm-9j77
CVE: CVE-2025-48495
CWE: CWE-79, CWE-87
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-06-03
Source: https://github.com/advisories/GHSA-4xg4-54hm-9j77
Type: github-advisory

## Affected
- Go: `github.com/forceu/gokapi` — affected >=1.0.1
- Go: `github.com/forceu/gokapi` — affected >=0 <0.0.0-20250530185940-65ddbc68fbfd

## Details
### Impact

By renaming the friendly name of an API key, an authenticated user could inject JS into the API key overview, which would also be executed when another user clicks on his API tab.
With the affected versions <v2.0, there was no user permission system implemented, therefore all authenticated users were already able to see and modify all resources, even if end-to-end encrypted, as the encryption key had to be the same for all users with <v2.0. Nethertheless with XSS, other attack vectors like redirection or crypto mining would be possble.

### Patches

This CVE has been fixed in v2.0.0

### Workarounds

If you are the only authenticated user using Gokapi, you are not affected. A workaround would be to not open the API page if you suspect that another user might have injected code.

## References
- https://github.com/Forceu/Gokapi/security/advisories/GHSA-4xg4-54hm-9j77
- https://nvd.nist.gov/vuln/detail/CVE-2025-48495
- https://github.com/Forceu/Gokapi/commit/65ddbc68fbfdf1c80cadb477f4bcbb7f2c4fdbf8
- https://github.com/Forceu/Gokapi
- https://pkg.go.dev/vuln/GO-2025-3736
