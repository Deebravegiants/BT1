# [C] Frappe has Path Transversal via SCORM

## Summary
Severity: Critical
Advisory: CVE-2026-39405
Aliases: GHSA-mxh7-g3r7-g96h
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-39405
Type: osv

## Details
Frappe Learning Management System (LMS) is a learning system that helps users structure their content. In versions 2.50.0 and below, a user with course editing role could upload a SCORM ZIP package to write files outside the intended directory. This issue has been resolved in version 2.50.1.

## References
- https://github.com/frappe/lms/releases/tag/v2.50.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39405.json
- https://github.com/frappe/lms/security/advisories/GHSA-mxh7-g3r7-g96h
- https://nvd.nist.gov/vuln/detail/CVE-2026-39405
