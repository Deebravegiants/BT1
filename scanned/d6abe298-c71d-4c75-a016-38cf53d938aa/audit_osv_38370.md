# [M] Frappe has an Arbitrary File Read via Path Traversal in render_include

## Summary
Severity: Medium
Advisory: CVE-2026-39352
Aliases: GHSA-67rf-pxgh-vfqv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-39352
Type: osv

## Details
Frappe is a full-stack web application framework. Versions prior to 15.105.0 and 16.15.0 contain a possible Arbitrary File Read vulnerability via Path Traversal. The issue is resolved in versions 16.15.0, 15.105.0 and above.

## References
- https://github.com/frappe/frappe/releases/tag/v16.15.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39352.json
- https://github.com/frappe/frappe/security/advisories/GHSA-67rf-pxgh-vfqv
- https://nvd.nist.gov/vuln/detail/CVE-2026-39352
