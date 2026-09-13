# [H] Budibase before 3.41.3 Privilege Escalation via User Update API

## Summary
Severity: High
Advisory: CVE-2026-82240
Aliases: GHSA-468g-55qj-v8rr
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82240
Type: osv

## Details
Budibase before 3.41.3 fails to validate app-scoped builder role assignments in the public user create and update endpoints, allowing an authenticated app-scoped builder to grant builder access to unrelated apps. Attackers can submit crafted requests to the user update API with builder.apps fields to escalate privileges and gain unauthorized builder access to other applications in the same tenant.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-468g-55qj-v8rr
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82240.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82240
- https://www.vulncheck.com/advisories/budibase-before-3.41.3-privilege-escalation-via-user-update-api
