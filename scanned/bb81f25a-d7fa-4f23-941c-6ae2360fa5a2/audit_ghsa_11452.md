# [M] Gokapi has CSRF in Login Endpoint

## Summary
Severity: Medium
Advisory: GHSA-hcff-qv74-7hr4
CVE: CVE-2026-29084
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-hcff-qv74-7hr4
Type: github-advisory

## Affected
- Go: `github.com/forceu/gokapi` — affected >=0 <2.2.3

## Details
### Summary
The login flow accepts credential-bearing requests without CSRF protection mechanisms tied to the browser session context. The handler parses form values directly and creates a session on successful credential validation.

*Issue found by [aisafe.io](aisafe.io)*

### Impact
An attacker can force a victim browser into a session associated with an existing user account where the attacker knows the credentials, causing user confusion, activity misattribution, and potential misuse of trusted user actions.

## References
- https://github.com/Forceu/Gokapi/security/advisories/GHSA-hcff-qv74-7hr4
- https://nvd.nist.gov/vuln/detail/CVE-2026-29084
- https://github.com/Forceu/Gokapi
- https://github.com/Forceu/Gokapi/releases/tag/v2.2.3
