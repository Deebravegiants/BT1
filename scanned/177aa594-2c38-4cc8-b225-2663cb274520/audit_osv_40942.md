# [C] Capgo - Privilege Escalation via Cross-Scope RBAC Role Assignment

## Summary
Severity: Critical
Advisory: CVE-2026-56247
Aliases: GHSA-55q2-p3m2-x66x
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-56247
Type: osv

## Details
Capgo before 12.128.2 allows org admins to assign org-scoped RBAC roles at app scope without validating role scope compatibility, including to pending invitees. Attackers can pre-seed malformed high-privilege bindings that survive invite acceptance, enabling accepted low-privilege users to perform unauthorized privileged app actions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56247.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-55q2-p3m2-x66x
- https://nvd.nist.gov/vuln/detail/CVE-2026-56247
- https://www.vulncheck.com/advisories/capgo-privilege-escalation-via-cross-scope-rbac-role-assignment
