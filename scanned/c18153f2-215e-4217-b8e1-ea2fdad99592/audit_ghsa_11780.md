# [M] Netmaker has Privilege Escalation from Admin to Super-Admin via User Update

## Summary
Severity: Medium
Advisory: GHSA-ch3w-9456-38v3
CVE: CVE-2026-29195
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-ch3w-9456-38v3
Type: github-advisory

## Affected
- Go: `github.com/gravitl/netmaker` — affected >=0 <1.5.0

## Details
The user update handler (PUT /api/users/{username}) lacks validation to prevent an admin-role user from assigning the super-admin role during account updates. While the code correctly blocks an admin from assigning the admin role to another user, it does not include an equivalent check for the super-admin role.

> Credits
> Artem Danilov (Positive Technologies)

## References
- https://github.com/gravitl/netmaker/security/advisories/GHSA-ch3w-9456-38v3
- https://nvd.nist.gov/vuln/detail/CVE-2026-29195
- https://github.com/gravitl/netmaker
- https://github.com/gravitl/netmaker/releases/tag/v1.5.0
