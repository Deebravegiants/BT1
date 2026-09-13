# [H] InvenTree Affected by Privilege Escalation via API

## Summary
Severity: High
Advisory: CVE-2026-35476
Aliases: GHSA-r8q5-3595-3jh2
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-35476
Type: osv

## Details
InvenTree is an Open Source Inventory Management System. Prior to 1.2.7 and 1.3.0, a non-staff authenticated user can elevate their account to a staff level via a POST request against their user account endpoint. The write permissions on the API endpoint are improperly configured, allowing any user to change their staff status. This vulnerability is fixed in 1.2.7 and 1.3.0.

## References
- https://docs.inventree.org/en/stable/concepts/threat_model/#assumed-trust
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35476.json
- https://github.com/inventree/InvenTree/security/advisories/GHSA-r8q5-3595-3jh2
- https://nvd.nist.gov/vuln/detail/CVE-2026-35476
