# [M] Gokapi has privilege escalation with auth token

## Summary
Severity: Medium
Advisory: GHSA-m2hx-wjxc-9fp4
CVE: CVE-2026-29060
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-m2hx-wjxc-9fp4
Type: github-advisory

## Affected
- Go: `github.com/forceu/gokapi` — affected >=0 <2.2.3

## Details
### Impact
A registered user without privileges to create or modify file requests is able to create a short-lived API key that has the permission to do so.

The user must be registered with Gokapi. If you do not have any other users with access to the admin/upload menu, you are not  impacted.

### Patches
This CVE is patched in v2.2.3

## References
- https://github.com/Forceu/Gokapi/security/advisories/GHSA-m2hx-wjxc-9fp4
- https://nvd.nist.gov/vuln/detail/CVE-2026-29060
- https://github.com/Forceu/Gokapi
- https://github.com/Forceu/Gokapi/releases/tag/v2.2.3
