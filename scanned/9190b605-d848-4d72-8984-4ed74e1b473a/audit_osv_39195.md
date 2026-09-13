# [C] ERPNext: Unauthorised Document modification due to missing validation

## Summary
Severity: Critical
Advisory: CVE-2026-44442
Aliases: GHSA-cg5w-7g26-p3w9
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-44442
Type: osv

## Details
ERPNext is a free and open source Enterprise Resource Planning tool. Prior to 16.9.1, certain endpoints failed to enforce proper authorization checks, allowing users to modify data beyond their permitted role. This vulnerability is fixed in 16.9.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44442.json
- https://github.com/frappe/erpnext/security/advisories/GHSA-cg5w-7g26-p3w9
- https://nvd.nist.gov/vuln/detail/CVE-2026-44442
