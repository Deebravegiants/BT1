# [M] Frappe LMS enrollment bypass in paid courses via unrelated batch

## Summary
Severity: Medium
Advisory: CVE-2026-39385
Aliases: GHSA-c4xh-2rcm-6mgc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-39385
Type: osv

## Details
Frappe LMS is an open source learning management system. In version 2.51.0 and earlier, a user could bypass payment validation for courses by using unrelated batch. This has been patched in 2.52.0 with enrollment now validating that the batch is linked to course.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39385.json
- https://github.com/frappe/lms/security/advisories/GHSA-c4xh-2rcm-6mgc
- https://nvd.nist.gov/vuln/detail/CVE-2026-39385
