# [M] ERPNext: Path Traversal Leading to Sensitive File Exposure

## Summary
Severity: Medium
Advisory: CVE-2026-44440
Aliases: GHSA-6ffr-92hr-3394
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-44440
Type: osv

## Details
ERPNext is a free and open source Enterprise Resource Planning tool. Prior to 15.101.1 and 16.10.0, an Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal') vulnerability on an endpoint allows an authenticated adjacent attacker to read arbitrary files. This vulnerability is fixed in 15.101.1 and 16.10.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44440.json
- https://github.com/frappe/erpnext/security/advisories/GHSA-6ffr-92hr-3394
- https://nvd.nist.gov/vuln/detail/CVE-2026-44440
